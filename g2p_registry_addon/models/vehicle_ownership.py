from odoo import models, fields, api

from .registry import G2PRegistry


class G2PRegistryVehicleOwnership(models.Model):
    """Vehicle Ownership Registry Model"""
    _name = 'g2p.registry.vehicle.ownership'
    _description = 'Vehicle Ownership Registry'
    _inherit = 'g2p.registry'

    id = fields.Integer(
        string='ID',
        help='Primary key identifier for the vehicle ownership record'
    )
    vehicle_registration_id = fields.Char(
        string='Vehicle Registration ID',
        help='Unique identifier for the vehicle registration'
    )
    
    # Standard registry fields (present in all models except ration card)
    individual_registry_id = fields.Integer(
        string='Individual Registry ID',
        help='Reference to individual registry record'
    )
    
    individual_unique_id = fields.Char(
        string='Individual Unique ID',
        help='MOSIP generated unique ID for individual'
    )
    
    owner_aadhaar = fields.Char(
        string='Owner Aadhaar',
        help='Aadhaar number of the vehicle owner'
    )
    
    family_unique_id = fields.Char(
        string='Family Unique ID',
        help='MOSIP generated unique ID for family'
    )
    
    family_registry_id = fields.Integer(
        string='Family Registry ID',
        help='Reference to family registry record'
    )
    
    # Vehicle details
    class_of_vehicle = fields.Char(
        string='Class of Vehicle',
        help='Classification type of the vehicle'
    )

    number_of_wheels = fields.Integer(
        string='Number of Wheels',
        help='Number of wheels of the vehicle'
    )

    registration_from_date = fields.Date(
        string='Registration From Date',
        help='Vehicle registration start date'
    )
    
    registration_to_date = fields.Date(
        string='Registration To Date',
        help='Vehicle registration end date'
    )
    
    engine_no = fields.Char(
        string='Engine Number',
        help='Engine number of the vehicle'
    )
    
    chassis_no = fields.Char(
        string='Chassis Number',
        help='Chassis number of the vehicle'
    )
    
    manufacturer = fields.Char(
        string='Manufacturer',
        help='Vehicle manufacturer name'
    )
