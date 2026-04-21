import io
import csv
import json
from odoo import http
from odoo.http import request


class G2PBeneficiaryExportController(http.Controller):

    # Ordered list of (raw_field, friendly_header)
    # Fields not listed here will be excluded from the export
    EXPORT_COLUMNS = [
        ("name", "Name"),
        ("gender", "Gender"),
        ("birthdate", "Date of Birth"),
        ("region_name", "Region"),
        ("district_name", "District"),
        ("benf_zan_id", "ZAN ID"),
        ("street", "Address"),
        ("phone", "Phone"),
        ("benf_post_code", "Post Code"),
        ("disability", "Disability"),
        ("is_receiving_allowance", "Receiving Allowance"),
        ("has_health_insurance", "Health Insurance"),
        ("payment_mode", "Payment Method"),
        ("bank_name", "Bank Name"),
        ("account_num", "Account Number"),
        ("account_name", "Account Name"),
        ("mobile_wallet", "Mobile Wallet"),
        ("other_pension", "Other Pension"),
        ("scheme_name", "Scheme Name"),
        # Nominee fields — first/middle/last name merged into "Nominee Name"
        ("nominee_name", "Nominee Name"),
        ("nominee_gender", "Nominee Gender"),
        ("nominee_zanid", "Nominee ZAN ID"),
        ("nominee_mobile", "Nominee Mobile"),
        ("nominee_rel_benf", "Nominee Relationship"),
        ("nominee_region", "Nominee Region"),
        ("nominee_district", "Nominee District"),
        ("nominee_shehia", "Nominee Shehia"),
        ("nominee_house_street", "Nominee Address"),
        ("nominee_post_code", "Nominee Post Code"),
    ]

    @http.route(
        "/g2p_pbms/export/beneficiaries/<int:wizard_id>",
        type="http",
        auth="user"
    )
    def export_beneficiaries(self, wizard_id, **kw):
        wizard = request.env["g2p.bgtask.summary.wizard"].sudo().browse(wizard_id)

        if not wizard.exists():
            return request.not_found()

        filename = "beneficiaries_%s.csv" % wizard.id

        def stream_csv():
            from odoo import api
            # Open a new cursor for the stream to avoid 'Cursor already closed' errors
            new_cr = request.env.registry.cursor()
            try:
                new_env = api.Environment(new_cr, request.env.uid, request.env.context)
                new_wizard = wizard.with_env(new_env)

                output = io.StringIO()
                # Write UTF-8 BOM once for Excel compatibility on Windows.
                # It will be included in the first yielded chunk.
                output.write('\ufeff')
                writer = csv.writer(output)

                page = 1
                page_size = 500
                odoo_domain = None
                first_batch = True

                # Precompute field names for optimization
                field_names = [f[0] for f in self.EXPORT_COLUMNS]
                friendly_headers = [f[1] for f in self.EXPORT_COLUMNS]

                while True:
                    res = new_wizard.get_beneficiaries(
                        new_wizard.id,
                        page,
                        page_size,
                        odoo_domain
                    )

                    message = res.get("message", {})
                    beneficiaries = message.get("beneficiaries", [])

                    if not beneficiaries:
                        if first_batch:
                            writer.writerow(["No data"])
                            yield output.getvalue()
                        break

                    if first_batch:
                        writer.writerow(friendly_headers)
                        first_batch = False

                    for row in beneficiaries:
                        # Merge nominee first + middle + last name into single "Nominee Name"
                        nominee_parts = []
                        for name_field in ("nominee_first_name", "nominee_middle_name", "nominee_last_name"):
                            val = row.get(name_field)
                            if val and str(val).strip():
                                nominee_parts.append(str(val).strip())
                        row["nominee_name"] = " ".join(nominee_parts) if nominee_parts else ""

                        csv_row = []
                        for field in field_names:
                            val = row.get(field)
                            if isinstance(val, (dict, list)):
                                val = json.dumps(val)
                            csv_row.append(val if val is not None else "")
                        writer.writerow(csv_row)

                    # Yield current buffer and clear it for the next batch
                    yield output.getvalue()
                    output.seek(0)
                    output.truncate(0)

                    if len(beneficiaries) < page_size:
                        break

                    page += 1
            finally:
                new_cr.close()

        return request.make_response(
            stream_csv(),
            headers=[
                ("Content-Type", "text/csv; charset=utf-8"),
                ("Content-Disposition", f'attachment; filename="{filename}"')
            ]
        )

