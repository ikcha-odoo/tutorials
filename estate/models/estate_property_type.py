from odoo import models, fields

class EstateType(models.Model):
    _name = "estate.property.type"
    _description = "The type of estate"
    _order = "sequence"

    color = fields.Integer('Color')
    sequence = fields.Integer('Sequence', default=0)
    name = fields.Char("Name", required=True)
    # properties_ids = fields.One2many("estate.property", "estate_type")

    property_ids = fields.One2many("estate.property", "tags_ids", index=True)

    _check_uniqueness_name = models.Constraint(
        'unique(name)',
        "Name must be unique."
    )


