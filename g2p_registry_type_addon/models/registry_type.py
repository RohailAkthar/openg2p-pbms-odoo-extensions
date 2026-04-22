from enum import Enum
from odoo import models, fields


class G2PTargetModelMapping:

    MODEL_MAPPING = {
        "student": "g2p.student.registry",
        "farmer": "g2p.farmer.registry",
        "families": "g2p.register.families",
    }

    @classmethod
    def get_target_model_name(cls, key):
        return cls.MODEL_MAPPING.get(key)


class G2PRegistryType(Enum):
    FARMER = "farmer"
    STUDENT = "student"
    FAMILIES = "families"

    @classmethod
    def selection(cls):
        return [(member.value, member.name.replace("_", " ").title()) for member in cls]
