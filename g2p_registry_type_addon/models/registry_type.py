from enum import Enum


class G2PRegistryType(Enum):
    RATION_CARD_APPLICANTS = "ration_card_applicants"
    REGISTRY_INDIVIDUALS = "registry_individuals"
    REGISTRY_FAMILIES = "registry_families"
    ELEC_MONTHLY_AVG = "elec_monthly_avg"
    GOVT_EMPLOYEES = "govt_employees"
    LAND_HOLDINGS = "land_holdings"
    LRS_BRS_APPLICATION = "lrs_brs_application"
    PROFESSIONAL_TAX_PAYERS = "professional_tax_payers"
    RESIDENTIAL_HOUSES = "residential_houses"
    VEHICLE_OWNERSHIP = "vehicle_ownership"
    OTHER = "other"

    @classmethod
    def selection(cls):
        """Return a list of tuples for Odoo selection fields."""
        # Each tuple is of the form (value, label)
        return [(member.value, member.name.replace("_", " ").title()) for member in cls]


class G2PTargetModelMapping:
    """Static mapping from registry type key to model name."""

    MODEL_MAPPING = {
        "ration_card_applicants": "g2p.registry.ration.card.applicants",
        "registry_individuals": "g2p.registry.individuals",
        "registry_families": "g2p.registry.families",
        "elec_monthly_avg": "g2p.registry.elec.monthly.avg",
        "govt_employees": "g2p.registry.govt.employees",
        "land_holdings": "g2p.registry.land.holdings",
        "lrs_brs_application": "g2p.registry.lrs.brs.application",
        "professional_tax_payers": "g2p.registry.professional.tax.payers",
        "residential_houses": "g2p.registry.residential.houses",
        "vehicle_ownership": "g2p.registry.vehicle.ownership",
    }

    @classmethod
    def get_target_model_name(cls, key):
        """Get the model name for a given key."""
        return cls.MODEL_MAPPING.get(key)
