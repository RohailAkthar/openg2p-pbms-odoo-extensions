# Part of OpenG2P. See LICENSE file for full copyright and licensing details.
import logging
import psycopg2
import json
from odoo import api, models, fields, _
from odoo.exceptions import AccessError

_logger = logging.getLogger(__name__)

class PBMSDashboardLogic(models.Model):
    _name = "g2p.pbms.dashboard.logic"
    _description = "PBMS Dashboard Logic"

    def _parse_geojson_feature(self, raw_geojson):
        if not raw_geojson:
            return False
        try:
            parsed = json.loads(raw_geojson) if isinstance(raw_geojson, str) else raw_geojson
        except (TypeError, ValueError):
            return False
        if isinstance(parsed, dict) and parsed.get("type") == "Feature":
            return parsed
        return False

    def _get_bg_task_db_conn(self):
        """Establish connection to the BG Task Database"""
        get_param = self.env['ir.config_parameter'].sudo().get_param
        try:
            conn = psycopg2.connect(
                host=get_param('g2p_pbms_dashboard.bg_task_db_host', 'pbms-gen2-postgresql'),
                port=get_param('g2p_pbms_dashboard.bg_task_db_port', '5432'),
                user=get_param('g2p_pbms_dashboard.bg_task_db_user', 'postgres'),
                password=get_param('g2p_pbms_dashboard.bg_task_db_password', '8RNvbkjo7l'),
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

    def _get_benefit_code_for_program(self, program_id):
        """Fetch benefit_code_id from g2p_program_benefit_codes for a given program"""
        if not program_id:
            return None
        benefit_code = self.env['g2p.program.benefit.codes'].sudo().search([
            ('program_id', '=', int(program_id))
        ], limit=1, order='id')
        if benefit_code:
            # Convert to string for JSON key lookup!
            return str(benefit_code.benefit_code_id)
        return None

    @api.model
    def get_dashboard_data(self, filters=None, dashboard_type='beneficiary'):
        if not self.env.user.has_group("g2p_pbms_dashboard.group_dashboard_viewer"):
            raise AccessError(_("You do not have access to this dashboard."))
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
            'map_geojson': {'provinces': {'type': 'FeatureCollection', 'features': []}, 'districts': {'type': 'FeatureCollection', 'features': []}},
            'programs': []
        }

        # 1. Fetch Programs from Odoo DB
        programs = self.env['g2p.program.definition'].sudo().search_read(
            [], ['id', 'program_mnemonic'], order='program_mnemonic'
        )
        result['programs'] = [{"id": p['id'], "name": p['program_mnemonic']} for p in programs]
        result['kpi']['program_count'] = len(programs)

        if not bg_conn:
            return result

        try:
            bg_cr = bg_conn.cursor()

            # 2. Get Benefit Code for selected program (if filter applied)
            # -------------------------------------------------------------------------
            benefit_code_id_str = None
            if filters.get('program_id'):
                benefit_code_id_str = self._get_benefit_code_for_program(filters['program_id'])
                _logger.info("Resolved benefit_code_id: %s for program_id: %s", 
                           benefit_code_id_str, filters['program_id'])

            # 3. Identify Enrolled IDs and their amounts
            # -------------------------------------------------------------------------
            odoo_list_domain = [
                ('list_stage', '=', 'enrollment'),
                ('list_workflow_status', '=', 'approved_final_enrolment')
            ]
            if filters.get('program_id'):
                odoo_list_domain.append(('program_id', '=', int(filters['program_id'])))

            enrollment_lists = self.env['g2p.beneficiary.list'].sudo().search(odoo_list_domain)
            enrollment_uuids = enrollment_lists.mapped('beneficiary_list_id')

            beneficiary_amounts = {}  # registrant_id -> amount
            if enrollment_uuids:
                # FIXED: Use benefit_code_id as string key for JSON lookup
                if benefit_code_id_str:
                    # Use the benefit code from g2p_program_benefit_codes
                    query_enrolled = f"""
                        SELECT 
                            elem->>'registrant_id' as rid,
                            COALESCE((elem->'entitlement'->>%s)::float, 0.0) as amt
                        FROM beneficiary_list_details,
                        LATERAL jsonb_array_elements(registrant_details::jsonb) AS elem
                        WHERE beneficiary_list_id IN ({','.join(['%s']*len(enrollment_uuids))})
                    """
                    # benefit_code_id_str is FIRST parameter (converted to string!)
                    params = [benefit_code_id_str] + list(enrollment_uuids)
                    bg_cr.execute(query_enrolled, tuple(params))
                else:
                    # Fallback: sum all entitlement values if no specific benefit code
                    query_enrolled = f"""
                        SELECT 
                            elem->>'registrant_id' as rid,
                            COALESCE((elem->>'amount')::float, 0.0) as amt
                        FROM beneficiary_list_details,
                        LATERAL jsonb_array_elements(registrant_details::jsonb) AS elem
                        WHERE beneficiary_list_id IN ({','.join(['%s']*len(enrollment_uuids))})
                    """
                    bg_cr.execute(query_enrolled, tuple(enrollment_uuids))
                
                for rid, amt in bg_cr.fetchall():
                    if rid:  # Ensure rid is not None
                        beneficiary_amounts[rid] = beneficiary_amounts.get(rid, 0) + amt

            enrolled_ids = list(beneficiary_amounts.keys())
            result['kpi']['total_enrolled'] = len(enrolled_ids)

            # 4. Calculate Disbursed and Allocated Amounts from BG Task DB
            # -----------------------------------------------------------
            disb_list_filter = ""
            disb_params = []
            if filters.get('program_id'):
                disb_lists = self.env['g2p.beneficiary.list'].sudo().search([
                    ('program_id', '=', int(filters['program_id'])),
                    ('list_stage', '=', 'disbursement')
                ])
                disb_uuids = disb_lists.mapped('beneficiary_list_id')
                if disb_uuids:
                    disb_list_filter = f"AND beneficiary_list_id IN ({','.join(['%s']*len(disb_uuids))})"
                    disb_params = list(disb_uuids)
                else:
                    disb_list_filter = "AND 1=0"

            bg_cr.execute(
                f"SELECT SUM(total_disbursement_quantity) FROM disbursement_batch WHERE disbursement_status = 'complete' {disb_list_filter}", 
                disb_params
            )
            result['kpi']['total_disbursed_amount'] = float(bg_cr.fetchone()[0] or 0)

            bg_cr.execute(
                f"SELECT SUM(total_disbursement_quantity) FROM disbursement_batch WHERE 1=1 {disb_list_filter}", 
                disb_params
            )
            result['kpi']['total_budget_allocated'] = float(bg_cr.fetchone()[0] or 0)

            # 5. Fetch Demographics from SR DB for Enrolled IDs (by pensioner_id)
            # -----------------------------------------------------------------
            if not enrolled_ids:
                return result

            sr_conn = self._get_sr_db_conn()
            if not sr_conn:
                return result

            sr_cr = sr_conn.cursor()

            # --- Fetch GeoJSON features from SR DB ---
            try:
                sr_cr.execute("SELECT code, name, geojson_feature FROM g2p_region WHERE geojson_feature IS NOT NULL")
                province_features = []
                for r_code, r_name, r_geojson in sr_cr.fetchall():
                    f = self._parse_geojson_feature(r_geojson)
                    if f:
                        props = f.get("properties") or {}
                        props.setdefault("id", r_code or r_name)
                        props.setdefault("name", r_name)
                        f["properties"] = props
                        province_features.append(f)

                sr_cr.execute("""
                    SELECT d.code, d.name, d.geojson_feature, r.code
                    FROM g2p_district d
                    LEFT JOIN g2p_region r ON d.province_id = r.id
                    WHERE d.geojson_feature IS NOT NULL
                """)
                district_features = []
                for d_code, d_name, d_geojson, p_code in sr_cr.fetchall():
                    f = self._parse_geojson_feature(d_geojson)
                    if f:
                        props = f.get("properties") or {}
                        props.setdefault("id", d_code or d_name)
                        props.setdefault("shapeName", d_name)
                        props.setdefault("province_code", p_code)
                        f["properties"] = props
                        district_features.append(f)

                result['map_geojson'] = {
                    'provinces': {'type': 'FeatureCollection', 'features': province_features},
                    'districts': {'type': 'FeatureCollection', 'features': district_features}
                }
            except Exception as e:
                _logger.warning("Failed to fetch GeoJSON from SR DB: %s", str(e))

            region_filter_name = None
            if filters.get("region"):
                input_val = str(filters["region"]).strip()
                # Dynamically search the code, name, AND the geojson_feature for the map's ID
                # This ensures we don't need a hardcoded dictionary if new regions are added!
                sr_cr.execute(
                    "SELECT name FROM g2p_region WHERE code = %s OR UPPER(name) = UPPER(%s) OR geojson_feature LIKE %s LIMIT 1",
                    [input_val, input_val, f'%"{input_val}"%'],
                )
                row = sr_cr.fetchone()
                if row: 
                    region_filter_name = row[0]

            where = ["p.pensioner_id = ANY(%s)"]
            params = [enrolled_ids]

            if region_filter_name:
                where.append("r.name = %s")
                params.append(region_filter_name)

            if filters.get("district"):
                # Handle both numeric ID and name for district filter
                if isinstance(filters["district"], int) or (isinstance(filters["district"], str) and filters["district"].isdigit()):
                    where.append("d.id = %s")
                    params.append(int(filters["district"]))
                else:
                    where.append("d.name = %s")
                    params.append(str(filters["district"]))

            if filters.get("gender"):
                where.append("UPPER(p.gender) = UPPER(%s)")
                params.append(filters["gender"])

            if filters.get("age_bucket"):
                bucket = filters["age_bucket"]
                age_expr = "EXTRACT(YEAR FROM age(current_date, p.birthdate))"
                if bucket == "18-69":
                    where.append(f"{age_expr} >= 18 AND {age_expr} <= 69")
                elif bucket == "70-75":
                    where.append(f"{age_expr} >= 70 AND {age_expr} <= 75")
                elif bucket == "76-80":
                    where.append(f"{age_expr} >= 76 AND {age_expr} <= 80")
                elif bucket == "81-85":
                    where.append(f"{age_expr} >= 81 AND {age_expr} <= 85")
                elif bucket == "86-90":
                    where.append(f"{age_expr} >= 86 AND {age_expr} <= 90")
                elif bucket == "91-95":
                    where.append(f"{age_expr} >= 91 AND {age_expr} <= 95")
                elif bucket == "96-100":
                    where.append(f"{age_expr} >= 96 AND {age_expr} <= 100")
                elif bucket == "101+":
                    where.append(f"{age_expr} > 100")

            where_sql = " AND ".join(where)

            # Fetch raw demographic data for all relevant beneficiaries
            sr_cr.execute(
                f"""
                SELECT
                    p.pensioner_id,
                    p.gender,
                    EXTRACT(YEAR FROM age(current_date, p.birthdate)) AS age_val,
                    COALESCE(r.name, 'Unknown') AS region_name,
                    COALESCE(d.name, 'Unknown') AS district_name
                FROM res_partner p
                LEFT JOIN g2p_region r ON p.region = r.id
                LEFT JOIN g2p_district d ON p.district = d.id
                WHERE {where_sql}
                """,
                params,
            )

            raw_data = sr_cr.fetchall()

            # Aggregate locally based on dashboard_type
            gender_agg = {}
            age_agg = {
                "Unknown": 0, "70-75": 0, "76-80": 0, "81-85": 0, 
                "86-90": 0, "91-95": 0, "96-100": 0, "101+": 0
            }
            region_agg = {}
            district_agg = {}

            seen_rids = set()

            for rid, gender, age, region, district in raw_data:
                # FIX: Deduplicate based on registrant ID to avoid inflating numbers
                if rid in seen_rids:
                    continue
                seen_rids.add(rid)

                val = beneficiary_amounts.get(rid, 0) if dashboard_type == 'monetary' else 1

                # Gender
                g_key = (gender or 'Unknown').capitalize()
                gender_agg[g_key] = gender_agg.get(g_key, 0) + val

                # Age
                if age is None:
                    age_agg["Unknown"] += val
                elif 70 <= age <= 75: age_agg["70-75"] += val
                elif 76 <= age <= 80: age_agg["76-80"] += val
                elif 81 <= age <= 85: age_agg["81-85"] += val
                elif 86 <= age <= 90: age_agg["86-90"] += val
                elif 91 <= age <= 95: age_agg["91-95"] += val
                elif 96 <= age <= 100: age_agg["96-100"] += val
                elif age > 100: age_agg["101+"] += val

                # Region/District
                region_agg[region] = region_agg.get(region, 0) + val
                district_agg[district] = district_agg.get(district, 0) + val

            # Update total enrolled to accurately reflect the active filtered count without duplicates
            result['kpi']['total_enrolled'] = len(seen_rids)

            result["charts"]["gender"] = gender_agg
            result["charts"]["age"] = age_agg
            result["map_data"] = district_agg  # Still used for map shading

            # Region Bar Data
            if not region_filter_name:
                sorted_regions = sorted(region_agg.items(), key=lambda x: x[0])
                labels = [n for n, _ in sorted_regions]
                result["charts"]["region_data"] = {
                    "level": "province",
                    "labels": labels,
                    "keys": labels,
                    "datasets": [{"label": "Amount" if dashboard_type == 'monetary' else "Enrolled", "data": [v for _, v in sorted_regions], "backgroundColor": "#3b82f6"}]
                }
            else:
                sorted_districts = sorted(district_agg.items(), key=lambda x: x[0])
                labels = [n for n, _ in sorted_districts]
                result["charts"]["region_data"] = {
                    "level": "district",
                    "labels": labels,
                    "keys": labels,
                    "datasets": [{"label": "Amount" if dashboard_type == 'monetary' else "Enrolled", "data": [v for _, v in sorted_districts], "backgroundColor": "#3b82f6"}]
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