from enum import Enum
from odoo import models, fields


class G2PTargetModelMapping:

    MODEL_MAPPING = {
        "individual": "g2p.individual.registry",
        "household": "g2p.household.registry",
        "farmer": "g2p.farmer.registry",
        "student": "g2p.student.registry",
        "group": "g2p.group.registry",
        "gramstackhousehold": "g2p.gramstack.household.registry",
    }

    @classmethod
    def get_target_model_name(cls, key):
        return cls.MODEL_MAPPING.get(key)


class G2PRegistryType(Enum):
    INDIVIDUAL = "individual"
    HOUSEHOLD = "household"
    FARMER = "farmer"
    STUDENT = "student"
    GROUP = "group"
    GRAMSTACKHOUSEHOLD = "gramstackhousehold"

    @classmethod
    def selection(cls):
        # Only show Gramstack Household in UI dropdowns; all others are hidden
        return [(cls.GRAMSTACKHOUSEHOLD.value, "Gramstack Household")]
