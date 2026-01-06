from datetime import date, timedelta
from odoo import api, fields, models
from odoo.tools.float_utils import float_compare
from odoo.exceptions import ValidationError


class EstateOffer(models.Model):
    _name = 'estate.offer'
    _description = "An offer you cannot refuse."
    _order = "price desc"

    state=fields.Selection(
        selection=[
            ('accepted', 'Accepted'),
            ('refused', 'Refused'),
        ]
    )
    price = fields.Float("Price")
    partner = fields.Many2one("res.partner")
    date_availability = fields.Date('Deadline', compute="_compute_availability", inverse="_inverse_availability") # depends on validity
    validity = fields.Integer("Validity (days)") # depends on date_availability
    
    
    estate_id = fields.Many2one("estate.property", required=True, store=True)
    estate_type_ids = fields.Integer(related="estate_id.prop_type.id")
    
    # status = 
    
    _check_offer_price_above_zero = models.Constraint(
        "CHECK(price > 0)",
        "Offer price must be above 0"
    )

    @api.constrains("state")
    def _constraint_acception(self):
        if self.state == 'accepted' and float_compare(self.price, self.estate_id['expected_price'] * .9, 2) == -1:
            raise ValidationError("The offer of a price cannot be lower than 90% of the expected price")
        
    # @api.onchange("")

    def action_refuse_offer(self):
        self.estate_id['selling_price'] = 0
        self.estate_id['buyer_id'] = None
        self.estate_id['state'] = 'offer received'
        self.state = 'refused'
        return True

    def action_accept_offer(self):
        self.estate_id['selling_price'] = self.price
        self.estate_id['buyer_id'] = self.partner
        self.estate_id['state'] = 'accepted'
        self.state = 'accepted'
        return True
    
    @api.depends("validity")
    def _compute_availability(self):
        for record in self:
            record.date_availability = date.today() + timedelta(days=record.validity)
    
    def _inverse_availability(self):
        for record in self:
            if record.date_availability:
                record.validity = (record.date_availability - date.today()).days
