from enum import Enum
from odoo import models, fields


class G2PTargetModelMapping:
    """Static mapping from registry type key to model name."""

    MODEL_MAPPING = {
        "student": "g2p.student.registry",
        "farmer": "g2p.farmer.registry",
        "individual": "g2p.individual.registry",
    }

    @classmethod
    def get_target_model_name(cls, key):
        """Get the model name for a given key."""
        return cls.MODEL_MAPPING.get(key)


class G2PRegistryType(Enum):
    FARMER = "farmer"
    STUDENT = "student"
    INDIVIDUAL = "individual"
    OTHER = "other"

    @classmethod
    def selection(cls):
        """Return a list of tuples for Odoo selection fields."""
        # Each tuple is of the form (value, label)
        return [(member.value, member.name.replace("_", " ").title()) for member in cls]
