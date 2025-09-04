from enum import Enum


class G2PRegistryType(Enum):
    FAMILIES = "families"
    INDIVIDUALS = "individuals"
    LAND_HOLDINGS = "land_holdings"
    VEHICLE_OWNERSHIP = "vehicle_ownership"
    RESIDENTIAL_HOUSES = "residential_houses"
    LRS_BRS_APPLICATION = "lrs_brs_application"
    RATION_CARD_APPLICANTS = "ration_card_applicants"
    PROFESSIONAL_TAX_PAYERS = "professional_tax_payers"
    GOVT_EMPLOYEES = "govt_employees"
    ELEC_MONTHLY_AVG = "elec_monthly_avg"
    OTHER = "other"

    @classmethod
    def selection(cls):
        """Return a list of tuples for Odoo selection fields."""
        # Each tuple is of the form (value, label)
        return [(member.value, member.name.replace("_", " ").title()) for member in cls]


class G2PTargetModelMapping:
    """Static mapping from registry type key to model name."""

    MODEL_MAPPING = {
        "families": "g2p.registry.families",
        "individuals": "g2p.registry.individuals",
        "land_holdings": "g2p.registry.land.holdings",
        "vehicle_ownership": "g2p.registry.vehicle.ownership",
        "residential_houses": "g2p.registry.residential.houses",
        "lrs_brs_application": "g2p.registry.lrs.brs.application",
        "ration_card_applicants": "g2p.registry.ration.card.applicants",
        "professional_tax_payers": "g2p.registry.professional.tax.payers",
        "govt_employees": "g2p.registry.govt.employees",
        "elec_monthly_avg": "g2p.registry.elec.monthly.avg",
    }

    @classmethod
    def get_target_model_name(cls, key):
        """Get the model name for a given key."""
        return cls.MODEL_MAPPING.get(key)
