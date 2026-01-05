from datetime import date, timedelta
from odoo import api, fields, models


class EstateOffer(models.Model):
    _name = 'estate.offer'
    _description = "An offer you cannot refuse."


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
    estate_id = fields.Many2one("estate.property", required=True)
    # status = 
    
    _check_offer_price_above_zero = models.Constraint(
        "CHECK(price > 0)",
        "Offer price must be above 0"
    )

    def action_refuse_offer(self):
        self.estate_id['selling_price'] = 0
        self.estate_id['buyer_id'] = None
        self.state = 'refused'
        return True

    def action_accept_offer(self):
        self.estate_id['selling_price'] = self.price
        self.estate_id['buyer_id'] = self.partner
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
