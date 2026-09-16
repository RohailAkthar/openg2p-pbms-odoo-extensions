from odoo import models, fields, api

from .registry import G2PRegistry


class G2PStudentRegistry(models.Model):
    _name = "g2p.student.registry"
    _description = "Student Registry"
    _inherit = "g2p.registry"
    _table = "g2p_register_students"
    _rec_name = "record_name"

    # Compatibility aliases
    name = fields.Char(string="Name", compute="_compute_name", search="_search_name")
    date_of_birth = fields.Date(string="Date of Birth", compute="_compute_date_of_birth", search="_search_date_of_birth")

    def _compute_name(self):
        for rec in self:
            rec.name = rec.record_name or f"{rec.first_name or ''} {rec.last_name or ''}".strip() or ""

    def _search_name(self, operator, value):
        return [("record_name", operator, value)]

    def _compute_date_of_birth(self):
        for rec in self:
            rec.date_of_birth = rec.birth_date

    def _search_date_of_birth(self, operator, value):
        return [("birth_date", operator, value)]

    # Student Identification & Demographics
    record_name = fields.Char(string="Record Name")
    functional_record_id = fields.Char(string="System ID / Functional ID")
    student_id = fields.Char(string="Student ID")
    udise_student_id = fields.Char(string="UDISE+ Student ID")
    foundational_id = fields.Char(string="Student Aadhaar Number")
    first_name = fields.Char(string="First Name")
    last_name = fields.Char(string="Last Name")
    gender = fields.Selection(
        selection=[
            ("male", "Male"),
            ("female", "Female"),
            ("other", "Other"),
        ],
        string="Gender",
    )
    birth_date = fields.Date(string="Date of Birth")
    guardian_aadhaar_number = fields.Char(string="Guardian Aadhaar Number")
    guardian_name = fields.Char(string="Guardian Name")
    father_name = fields.Char(string="Father Name")
    mother_name = fields.Char(string="Mother Name")
    social_category = fields.Char(string="Social Category")
    apaar_id = fields.Char(string="APAAR ID")
    pen_number = fields.Char(string="PEN Number")
    mobile_phone_number = fields.Char(string="Mobile Phone Number")

    # School & Academics
    school_name = fields.Char(string="School Name")
    school_udise_code = fields.Char(string="School UDISE Code")
    education_level = fields.Char(string="Education Level")
    class_grade = fields.Char(string="Class / Grade")
    medium_of_instruction = fields.Char(string="Medium of Instruction")
    attendance_percentage = fields.Float(string="Attendance Percentage")

    # Entitlements & Banking
    scholarship_status = fields.Char(string="Scholarship Status")
    bank_account_no = fields.Char(string="Bank Account Number")
    bank_name = fields.Char(string="Bank Name")
    ifsc_code = fields.Char(string="IFSC Code")

    # Geographic Location
    district = fields.Char(string="District")
    block = fields.Char(string="Block")
    village = fields.Char(string="Village")
    state = fields.Char(string="State")
