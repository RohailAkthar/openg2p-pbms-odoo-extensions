from odoo import models, fields

from .registry import G2PRegistry


class G2PRegisterIndividual(models.Model):
    _name = "g2p.register.individual"
    _description = "Nigeria NSR Individual Registry"
    _table = "g2p_register_individuals"
    _inherit = "g2p.registry"

    # Core Identifiers & Links
    functional_record_id = fields.Char(string="Functional Record ID")
    link_internal_record_id = fields.Char(string="Link Internal Record ID")
    link_foundational_id = fields.Char(string="Link Foundational ID")
    record_name = fields.Char(string="Record Name")
    record_image_document_id = fields.Text(string="Record Image Document ID")
    search_text = fields.Text(string="Search Text")
    record_status = fields.Selection(
        selection=[
            ("ACTIVE", "Active"),
            ("INACTIVE", "Inactive"),
            ("ARCHIVED", "Archived"),
        ],
        string="Record Status",
        default="ACTIVE",
    )
    record_status_reason = fields.Char(string="Record Status Reason")

    # Foundational ID / Identity
    foundational_id = fields.Char(string="National ID (Foundational ID / NIN)")
    foundational_id_masked = fields.Char(string="National ID (Masked NIN)")
    foundational_id_verification_status = fields.Selection(
        selection=[
            ("VERIFIED", "Verified"),
            ("PENDING", "Pending Verification"),
            ("FAILED", "Failed Verification"),
            ("EXCEPTION", "Exception / Override"),
        ],
        string="ID Verification Status",
    )
    identity_evidence_type = fields.Selection(
        selection=[
            ("FOUNDATIONAL_ID_VERIFIED", "Foundational ID Verified"),
            ("DOCUMENT", "Physical Document / Certificate"),
            ("NONE", "None"),
            ("EXCEPTION", "Exception"),
        ],
        string="Identity Evidence Type",
    )

    # Names & Demographics
    full_name = fields.Char(string="Full Name")
    first_name = fields.Char(string="First Name")
    middle_name = fields.Char(string="Middle Name")
    last_name = fields.Char(string="Last Name")
    given_name = fields.Char(string="Given Name")
    prefix = fields.Char(string="Prefix / Title")
    suffix = fields.Char(string="Suffix")
    alias_names = fields.Char(string="Alias Names (JSON)")
    gender = fields.Selection(
        selection=[
            ("male", "Male"),
            ("female", "Female"),
            ("other", "Other"),
        ],
        string="Gender",
    )
    birth_date = fields.Date(string="Date of Birth")
    estimated_age = fields.Integer(string="Estimated Age (Years)")
    age_method = fields.Selection(
        selection=[
            ("DOCUMENTED", "Documented / Verified"),
            ("ESTIMATED", "Estimated"),
        ],
        string="Age Determination Method",
    )
    citizenship_category = fields.Selection(
        selection=[
            ("CITIZEN", "National Citizen"),
            ("REFUGEE", "Refugee"),
            ("IDP", "Internally Displaced Person (IDP)"),
            ("RETURNEE", "Returnee"),
            ("RESIDENT", "Resident Alien / Foreigner"),
        ],
        string="Citizenship Category",
    )
    marital_status = fields.Selection(
        selection=[
            ("SINGLE", "Single / Never Married"),
            ("MARRIED", "Married"),
            ("DIVORCED", "Divorced / Separated"),
            ("WIDOWED", "Widowed"),
        ],
        string="Marital Status",
    )

    # Contact & Household Relations
    phone_numbers = fields.Char(string="Phone Numbers (JSON)")
    emails = fields.Char(string="Email Addresses (JSON)")
    preferred_contact_method = fields.Selection(
        selection=[
            ("CALL", "Voice Call"),
            ("SMS", "SMS Text"),
            ("VIA_LOCAL_OFFICE", "Via Local Ward Office"),
            ("NONE", "None"),
        ],
        string="Preferred Contact Method",
    )
    contact_person_name = fields.Char(string="Contact Person Name")
    relationship_to_head = fields.Selection(
        selection=[
            ("SELF", "Head of Household"),
            ("SPOUSE", "Spouse / Partner"),
            ("CHILD", "Child (Son / Daughter)"),
            ("PARENT", "Parent (Father / Mother)"),
            ("SIBLING", "Sibling (Brother / Sister)"),
            ("OTHER_RELATIVE", "Other Relative"),
            ("NON_RELATIVE", "Non-Relative"),
        ],
        string="Relationship to Household Head",
    )
    residency_status = fields.Selection(
        selection=[
            ("USUAL_MEMBER", "Usual Resident Member"),
            ("TEMPORARY", "Temporary Resident"),
            ("ABSENT", "Temporarily Absent"),
        ],
        string="Residency Status",
    )
    dependency_indicator = fields.Boolean(string="Dependent Member", default=False)

    # Geographic Location
    latitude = fields.Char(string="Latitude")
    longitude = fields.Char(string="Longitude")
    altitude = fields.Char(string="Altitude")
    plus_code = fields.Char(string="Plus Code")
    address_line_1 = fields.Char(string="Address Line 1 / Settlement")
    address_line_2 = fields.Char(string="Address Line 2")
    postal_code = fields.Char(string="Postal Code")
    country_code = fields.Char(string="Country Code")
    geo_lowest_level_value_id = fields.Char(string="Geo Location / Ward Code")
    geo_code_hierarchy_json = fields.Char(string="Geo Hierarchy (JSON)")

    # Vulnerability & Social Protection
    disability_status = fields.Selection(
        selection=[
            ("YES", "Has Disability"),
            ("NO", "No Disability"),
            ("UNKNOWN", "Unknown"),
        ],
        string="Disability Status",
    )
    plw_status = fields.Boolean(string="Pregnant or Lactating Woman (PLW)", default=False)
    plw_status_date = fields.Date(string="PLW Registered Date")
    orphanhood_flag = fields.Boolean(string="Orphan Child", default=False)
    chronic_illness_flag = fields.Boolean(string="Chronic Illness / Critical Condition", default=False)
    displacement_status = fields.Selection(
        selection=[
            ("HOST_COMMUNITY", "Host Community"),
            ("IDP", "Internally Displaced Person"),
            ("RETURNEE", "Returnee"),
            ("REFUGEE", "Refugee"),
        ],
        string="Displacement Status",
    )
    pastoralist_classification = fields.Selection(
        selection=[
            ("PASTORALIST", "Nomadic Pastoralist"),
            ("SEMI_PASTORALIST", "Semi-Nomadic Pastoralist"),
            ("SETTLED", "Settled / Agro-Pastoralist"),
        ],
        string="Pastoralist Classification",
    )
    high_mobility_indicator = fields.Boolean(string="High Mobility Indicator", default=False)

    # Livelihood, Education & Socio-Economics
    primary_livelihood = fields.Selection(
        selection=[
            ("AGRICULTURE", "Subsistence / Crop Farming"),
            ("LIVESTOCK", "Livestock / Pastoralism"),
            ("FISHING", "Fishery / Aquaculture"),
            ("WAGE_LABOR", "Casual / Daily Wage Labor"),
            ("SELF_EMPLOYMENT", "Small Business / Informal Trade"),
            ("GOVERNMENT_EMPLOYEE", "Public Sector / Government"),
            ("PRIVATE_SECTOR_EMPLOYEE", "Formal Private Sector"),
            ("BUSINESS_TRADE", "Wholesale / Retail Trade"),
            ("REMITTANCE", "Family Remittances"),
            ("PENSION", "Pension / Retirement"),
            ("UNEMPLOYED", "Unemployed / Seeking Work"),
            ("OTHER", "Other"),
        ],
        string="Primary Livelihood",
    )
    secondary_livelihood = fields.Char(string="Secondary Livelihood")
    occupation = fields.Char(string="Occupation")
    income_level = fields.Char(string="Income Level")
    employment_status = fields.Selection(
        selection=[
            ("EMPLOYED", "Employed (Full/Part-Time)"),
            ("SELF_EMPLOYED", "Self-Employed / Entrepreneur"),
            ("UNEMPLOYED", "Unemployed"),
            ("STUDENT", "Student / In Training"),
            ("RETIRED", "Retired / Elderly"),
            ("OTHER", "Other"),
        ],
        string="Employment Status",
    )
    education_level = fields.Selection(
        selection=[
            ("NONE", "No Formal Education"),
            ("PRIMARY", "Primary School"),
            ("SECONDARY", "Secondary School"),
            ("TERTIARY", "Tertiary / University"),
            ("VOCATIONAL", "Vocational Training"),
        ],
        string="Education Level",
    )
    language_code = fields.Char(string="Language Code")
    registration_date = fields.Date(string="Registration Date")
    legacy_program_ids = fields.Char(string="Legacy Program IDs (JSON)")
    coping_strategies_index = fields.Integer(string="Coping Strategies Index (CSI)")
