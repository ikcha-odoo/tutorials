from odoo import api, models, fields

class EstateRealType(models.Model):
    _name = "estate.property.type"
    _description = "The type of estate"
    _order = "sequence"

    sequence = fields.Integer('Sequence', default=0)
    name = fields.Char("Name", required=True)
    # properties_ids = fields.One2many("estate.property", "estate_type")

    property_ids = fields.One2many("estate.property", "prop_type", index=True)

    offer_ids = fields.One2many("estate.offer", "estate_type_ids", tracking=True,index=True)
    offer_count = fields.Integer("Offer Count", compute="_compute_offer_count")

    _check_uniqueness_name = models.Constraint(
        'unique(name)',
        "Name must be unique."
    )

    @api.depends("offer_ids")
    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)


