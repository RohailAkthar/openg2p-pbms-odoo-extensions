from enum import Enum
from odoo import models, fields


class G2PTargetModelMapping:

    MODEL_MAPPING = {
        "student": "g2p.student.registry",
        "farmer": "g2p.farmer.registry",
        "families": "g2p.register.families",
        "household": "g2p.register.household",
        "individual": "g2p.register.individual",
    }

    @classmethod
    def get_target_model_name(cls, key):
        return cls.MODEL_MAPPING.get(key)


class G2PRegistryType(Enum):
    HOUSEHOLD = "household"
    INDIVIDUAL = "individual"

    @classmethod
    def selection(cls):
        return [(member.value, member.name.replace("_", " ").title()) for member in cls]
