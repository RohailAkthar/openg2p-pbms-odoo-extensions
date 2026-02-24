# Part of OpenG2P. See LICENSE file for full copyright and licensing details.
import logging
import psycopg2
from odoo import api, models, fields

_logger = logging.getLogger(__name__)

class PBMSDashboardLogic(models.Model):
    _name = "g2p.pbms.dashboard.logic"
    _description = "PBMS Dashboard Logic"

    def _get_bg_task_db_conn(self):
        """Establish connection to the BG Task Database"""
        get_param = self.env['ir.config_parameter'].sudo().get_param
        try:
            conn = psycopg2.connect(
                host=get_param('g2p_pbms_dashboard.bg_task_db_host', 'localhost'),
                port=get_param('g2p_pbms_dashboard.bg_task_db_port', '5432'),
                user=get_param('g2p_pbms_dashboard.bg_task_db_user', 'postgres'),
                password=get_param('g2p_pbms_dashboard.bg_task_db_password', ''),
                dbname=get_param('g2p_pbms_dashboard.bg_task_db_name', 'bgtaskdb'),
                connect_timeout=5
            )
            return conn
        except Exception as e:
            _logger.error("Failed to connect to BG Task DB: %s", str(e))
            return None

    def _get_sr_db_conn(self):
        """Establish connection to the Social Registry (SR) Database"""
        get_param = self.env["ir.config_parameter"].sudo().get_param
        try:
            conn = psycopg2.connect(
                host=get_param("g2p_pbms_dashboard.sr_db_host", "socialregistry-postgresql"),
                port=get_param("g2p_pbms_dashboard.sr_db_port", "5432"),
                user=get_param("g2p_pbms_dashboard.sr_db_user", "postgres"),
                password=get_param("g2p_pbms_dashboard.sr_db_password", ""),
                dbname=get_param("g2p_pbms_dashboard.sr_db_name", "socialregistrydb"),
                connect_timeout=5,
            )
            return conn
        except Exception as e:
            _logger.error("Failed to connect to SR DB: %s", str(e))
            return None

    @api.model
    def get_dashboard_data(self, filters=None):
        filters = filters or {}
        bg_conn = self._get_bg_task_db_conn()
        sr_conn = None
        
        result = {
            'kpi': {
                'total_enrolled': 0,
                'total_disbursed_amount': 0,
                'total_budget_allocated': 0,
                'program_count': 0
            },
            'charts': {'age': {}, 'gender': {}, 'region_data': {}},
            'map_data': {},
            'programs': []
        }

        # 1. Fetch Programs from Odoo DB
        programs = self.env['g2p.program.definition'].search_read(
            [], ['id', 'program_mnemonic'], order='program_mnemonic'
        )
        result['programs'] = [{"id": p['id'], "name": p['program_mnemonic']} for p in programs]
        result['kpi']['program_count'] = len(programs)

        if not bg_conn:
            return result

        try:
            bg_cr = bg_conn.cursor()
            
            # 2. Identify Enrolled IDs (Unique Beneficiaries in Approved Enrollment Lists)
            # -------------------------------------------------------------------------
            odoo_list_domain = [
                ('list_stage', '=', 'enrollment'),
                ('list_workflow_status', '=', 'approved_final_enrolment')
            ]
            if filters.get('program_id'):
                odoo_list_domain.append(('program_id', '=', int(filters['program_id'])))
            
            enrollment_lists = self.env['g2p.beneficiary.list'].search(odoo_list_domain)
            enrollment_uuids = enrollment_lists.mapped('beneficiary_list_id')

            enrolled_ids = []
            if enrollment_uuids:
                query_enrolled = f"""
                    SELECT DISTINCT jsonb_array_elements(registrant_details::jsonb)->>'registrant_id'
                    FROM beneficiary_list_details
                    WHERE beneficiary_list_id IN ({','.join(['%s']*len(enrollment_uuids))})
                """
                bg_cr.execute(query_enrolled, tuple(enrollment_uuids))
                enrolled_ids = [r[0] for r in bg_cr.fetchall()]
            
            result['kpi']['total_enrolled'] = len(enrolled_ids)

            # 3. Calculate Disbursed and Allocated Amounts from BG Task DB
            # -----------------------------------------------------------
            disb_list_filter = ""
            disb_params = []
            if filters.get('program_id'):
                disb_lists = self.env['g2p.beneficiary.list'].search([
                    ('program_id', '=', int(filters['program_id'])),
                    ('list_stage', '=', 'disbursement')
                ])
                disb_uuids = disb_lists.mapped('beneficiary_list_id')
                if disb_uuids:
                    disb_list_filter = f"AND beneficiary_list_id IN ({','.join(['%s']*len(disb_uuids))})"
                    disb_params = list(disb_uuids)
                else:
                    disb_list_filter = "AND 1=0"

            bg_cr.execute(f"SELECT SUM(total_disbursement_quantity) FROM disbursement_batch WHERE disbursement_status = 'complete' {disb_list_filter}", disb_params)
            result['kpi']['total_disbursed_amount'] = float(bg_cr.fetchone()[0] or 0)

            bg_cr.execute(f"SELECT SUM(total_disbursement_quantity) FROM disbursement_batch WHERE 1=1 {disb_list_filter}", disb_params)
            result['kpi']['total_budget_allocated'] = float(bg_cr.fetchone()[0] or 0)

            # 4. Fetch Demographics from SR DB for Enrolled IDs (by benf_zan_id)
            # -----------------------------------------------------------------
            if not enrolled_ids:
                return result

            sr_conn = self._get_sr_db_conn()
            if not sr_conn:
                return result

            sr_cr = sr_conn.cursor()

            # -----------------------------------------------------------------
            # Region filter: accept either code OR name → always filter by NAME
            # (no hardcoded TZ codes anywhere)
            # -----------------------------------------------------------------
            region_filter_name = None
            if filters.get("region"):
                input_val = str(filters["region"]).strip()
                # Resolve input (could be code like "TZ06" or a name) to the actual region name
                sr_cr.execute(
                    """
                    SELECT name
                    FROM g2p_region
                    WHERE code = %s OR UPPER(name) = UPPER(%s)
                    LIMIT 1
                    """,
                    [input_val, input_val],
                )
                row = sr_cr.fetchone()
                if row:
                    region_filter_name = row[0]
                else:
                    # Fallback: use input as-is (might be a name that doesn't exist yet)
                    region_filter_name = input_val

            where = ["p.benf_zan_id = ANY(%s)"]
            params = [enrolled_ids]

            if region_filter_name:
                where.append("r.name = %s")
                params.append(region_filter_name)

            if filters.get("district"):
                where.append("d.id = %s")
                params.append(int(filters["district"]))

            if filters.get("gender"):
                where.append("p.gender = %s")
                params.append(filters["gender"])

            where_sql = " AND ".join(where)

            # ---------------------------------------------------------------
            # SINGLE AGGREGATED QUERY (gender/age/kpi)
            # ---------------------------------------------------------------
            sr_cr.execute(
                f"""
                WITH base AS (
                    SELECT
                        p.id,
                        p.gender,
                        p.birthdate,
                        r.name AS region_name,
                        d.id AS district_id,
                        d.name AS district_name,
                        EXTRACT(YEAR FROM age(current_date, p.birthdate)) AS age_val
                    FROM res_partner p
                    LEFT JOIN g2p_region r ON p.region = r.id
                    LEFT JOIN g2p_district d ON p.district = d.id
                    WHERE {where_sql}
                )

                SELECT
                    COUNT(*) AS total_count,

                    COUNT(*) FILTER (WHERE LOWER(gender) = 'male') AS male_count,
                    COUNT(*) FILTER (WHERE LOWER(gender) = 'female') AS female_count,
                    COUNT(*) FILTER (WHERE LOWER(gender) = 'other') AS other_count,
                    COUNT(*) FILTER (WHERE gender IS NULL) AS unknown_gender_count,

                    COUNT(*) FILTER (WHERE birthdate IS NULL) AS age_unknown,
                    COUNT(*) FILTER (WHERE age_val BETWEEN 70 AND 75) AS age_70_75,
                    COUNT(*) FILTER (WHERE age_val BETWEEN 76 AND 80) AS age_76_80,
                    COUNT(*) FILTER (WHERE age_val BETWEEN 81 AND 85) AS age_81_85,
                    COUNT(*) FILTER (WHERE age_val BETWEEN 86 AND 90) AS age_86_90,
                    COUNT(*) FILTER (WHERE age_val BETWEEN 91 AND 95) AS age_91_95,
                    COUNT(*) FILTER (WHERE age_val BETWEEN 96 AND 100) AS age_96_100,
                    COUNT(*) FILTER (WHERE age_val > 101) AS age_101_plus
                FROM base
                """,
                params,
            )

            row = sr_cr.fetchone()
            (
                total_count,
                male,
                female,
                other,
                unknown_gender,
                age_unknown,
                age_70_75,
                age_76_80,
                age_81_85,
                age_86_90,
                age_91_95,
                age_96_100,
                age_101_plus,
            ) = row or (0, 0, 0, 0, 0, 0, 0, 0, 0)

            result["kpi"]["total_enrolled"] = int(total_count)

            result["charts"]["gender"] = {
                "Male": int(male),
                "Female": int(female),
                "Other": int(other),
                "Unknown": int(unknown_gender),
            }

            result["charts"]["age"] = {
                "Unknown": int(age_unknown),
                "70-75": int(age_70_75),
                "76-80": int(age_76_80),
                "81-85": int(age_81_85),
                "86-90": int(age_86_90),
                "91-95": int(age_91_95),
                "96-100": int(age_96_100),
                "101+": int(age_101_plus),
            }

            # ---------------------------------------------------------------
            # DISTRICT MAP + REGION BAR (grouped by NAME, no hard-coded codes)
            # ---------------------------------------------------------------
            sr_cr.execute(
                f"""
                SELECT
                    COALESCE(d.name, 'Unknown') AS district_name,
                    COALESCE(r.name, 'Unknown') AS region_name,
                    COUNT(*)
                FROM res_partner p
                LEFT JOIN g2p_region r ON p.region = r.id
                LEFT JOIN g2p_district d ON p.district = d.id
                WHERE {where_sql}
                GROUP BY district_name, region_name
                """,
                params,
            )

            rows = sr_cr.fetchall()

            district_counts = {}
            region_counts = {}

            for district_name, region_name, count in rows:
                district_counts[district_name] = count
                region_counts[region_name] = region_counts.get(region_name, 0) + count

            result["map_data"] = district_counts

            # Province-level bar → uses region NAMES (sorted alphabetically)
            if not region_filter_name:
                sorted_regions = sorted(region_counts.items(), key=lambda x: x[0])  # alphabetical by name

                labels = [name for name, _ in sorted_regions]
                values = [count for _, count in sorted_regions]
                keys = labels  # keys = names (what frontend will send back as filter.region)

                result["charts"]["region_data"] = {
                    "level": "province",
                    "labels": labels,
                    "keys": keys,
                    "datasets": [
                        {"label": "Enrolled", "data": values, "backgroundColor": "#3b82f6"}
                    ],
                }

            # District-level bar (when a region is selected)
            else:
                district_labels = []
                district_values = []

                for district_name, count in sorted(district_counts.items(), key=lambda x: x[0]):
                    district_labels.append(district_name)
                    district_values.append(count)

                result["charts"]["region_data"] = {
                    "level": "district",
                    "labels": district_labels,
                    "keys": district_labels,
                    "datasets": [
                        {"label": "Enrolled", "data": district_values, "backgroundColor": "#3b82f6"}
                    ],
                }

            return result

        except Exception as e:
            _logger.exception("Error during dual-DB dashboard data fetch: %s", str(e))
            return result
        finally:
            if bg_conn:
                bg_conn.close()
            if sr_conn:
                sr_conn.close()