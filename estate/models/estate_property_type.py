from odoo import models, fields

class EstateType(models.Model):
    _name = "estate.property.type"
    _description = "The type of estate"

    name = fields.Char("Name", required=True)


