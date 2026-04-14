from odoo import fields, models

class ZanzibarProvince(models.Model):
    _inherit = 'g2p.region'
    _description = 'Province'

    geojson_feature = fields.Text(
        string="GeoJSON Feature",
        help="GeoJSON feature payload for rendering this region on the map.",
    )


class ZanzibarDistrict(models.Model):
    _inherit = 'g2p.district'
    _description = 'District'
    
    geojson_feature = fields.Text(
        string="GeoJSON Feature",
        help="GeoJSON feature payload for rendering this district on the map.",
    )
