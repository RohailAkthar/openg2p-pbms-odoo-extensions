import csv
import io
import logging
from datetime import datetime
from werkzeug.wrappers import Response

from odoo import http, api, _
from odoo.http import request

try:
    from werkzeug.wsgi import stream_with_context
except ImportError:
    try:
        from werkzeug.wrappers import stream_with_context
    except ImportError:
        def stream_with_context(gen):
            return gen

_logger = logging.getLogger(__name__)


class DisbursementExportController(http.Controller):

    @http.route('/g2p/export_disbursement_beneficiaries', type='http', auth='user')
    def export_disbursement_beneficiaries(self, wizard_id, domain="[]", **kw):
        """
        Streams beneficiary records for a household disbursement list as a CSV file.
        CSV Columns: Household Name, Household Size, Head Name, Head Gender, Head Phone
        """
        try:
            wizard_id = int(wizard_id)
            wizard = request.env['g2p.bgtask.summary.wizard'].sudo().browse(wizard_id)
            if not wizard.exists():
                return request.not_found()

            # Ensure this export is ONLY available for disbursement lists
            if (wizard.list_stage or '').lower() != 'disbursement':
                return request.make_response(
                    "Download is only available for Disbursement Lists.",
                    status=403
                )

            sanitized_mnemonic = "".join([c if c.isalnum() else "_" for c in (wizard.mnemonic or str(wizard_id))])
            filename = f"disbursement_beneficiaries_{sanitized_mnemonic}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

            registry = request.env.registry
            uid = request.uid
            context = dict(request.env.context)

            def generate_csv_chunks():
                with registry.cursor() as new_cr:
                    new_env = api.Environment(new_cr, uid, context)
                    wizard_model = new_env['g2p.bgtask.summary.wizard'].sudo()

                    output = io.StringIO()
                    output.write('\ufeff')  # UTF-8 BOM for Excel compatibility
                    writer = csv.writer(output)

                    # Write CSV header row
                    header = ["Household Name", "Household Size", "Head Name", "Head Gender", "Head Phone", "Head Monthly Income", "Residential Address"]
                    writer.writerow(header)
                    yield output.getvalue()

                    page = 1
                    page_size = 100
                    more_records = True

                    while more_records:
                        output = io.StringIO()
                        writer = csv.writer(output)

                        _logger.info("Export streaming page %s (page_size=%s) for wizard %s", page, page_size, wizard_id)
                        try:
                            res = wizard_model.get_beneficiaries(
                                wizard_id, page, page_size, domain
                            )
                        except Exception as fetch_err:
                            _logger.error("Error fetching beneficiaries page %s for wizard %s: %s", page, wizard_id, fetch_err)
                            break

                        beneficiaries = []
                        if isinstance(res, dict) and res.get('message'):
                            beneficiaries = res.get('message', {}).get('beneficiaries', [])
                        elif isinstance(res, dict) and res.get('beneficiaries'):
                            beneficiaries = res.get('beneficiaries', [])

                        if not beneficiaries:
                            _logger.info("No more beneficiaries returned for wizard %s at page %s", wizard_id, page)
                            more_records = False
                            break

                        for b in beneficiaries:
                            hh_name = str(b.get('name') or b.get('head_name') or b.get('household_name') or '').strip()
                            hh_size = b.get('household_size') if b.get('household_size') is not None else 0
                            try:
                                hh_size = int(hh_size)
                            except (ValueError, TypeError):
                                hh_size = 0

                            head_name = str(b.get('head_name') or b.get('name') or '').strip()

                            raw_gender = str(b.get('head_gender') or b.get('gender') or '').strip().lower()
                            if raw_gender.startswith('f'):
                                head_gender = 'Female'
                            elif raw_gender.startswith('m'):
                                head_gender = 'Male'
                            elif raw_gender:
                                head_gender = raw_gender.capitalize()
                            else:
                                head_gender = ''

                            head_phone = str(b.get('head_phone') or b.get('phone') or '').strip()
                            try:
                                raw_income = b.get('head_income')
                                head_income_val = float(raw_income) if raw_income is not None else 0.0
                                head_income = f"{head_income_val:,.2f}"
                            except (ValueError, TypeError):
                                head_income = "0.00"
                            address = str(b.get('address') or '').strip()

                            writer.writerow([hh_name, hh_size, head_name, head_gender, head_phone, head_income, address])



                        yield output.getvalue()

                        if len(beneficiaries) < page_size:
                            more_records = False
                        else:
                            page += 1

            headers = [
                ('Content-Type', 'text/csv; charset=utf-8'),
                ('Content-Disposition', f'attachment; filename="{filename}"'),
                ('Cache-Control', 'no-cache, no-store, must-revalidate'),
                ('Pragma', 'no-cache'),
                ('Expires', '0'),
            ]

            return Response(
                stream_with_context(generate_csv_chunks()),
                headers=headers,
                status=200
            )

        except Exception as e:
            _logger.error("Error streaming disbursement beneficiaries export: %s", str(e), exc_info=True)
            return request.make_response(_("Error generating export: %s") % str(e), status=500)
