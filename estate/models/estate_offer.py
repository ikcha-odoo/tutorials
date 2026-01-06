from datetime import date, timedelta
from odoo import api, fields, models
from odoo.orm.types import ValuesType
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

    @api.model
    def create(self, vals_list): # type: ignore
        for record in vals_list:
            _property_id = record['estate_id']
            cached_property = self.env['estate.property'].browse(_property_id)
            _price = record['price']

            _all_prices = cached_property['estate_offers'].mapped('price')
            _max_offer = -1
            if _all_prices:
                _max_offer = max(_all_prices)
        
            # 1. Check price
            if float_compare(_price, cached_property['expected_price'] * .9, 2) == -1:
                raise ValidationError("The offer of a price cannot be lower than 90% of the expected price")
            if float_compare( _price,  _max_offer, 2) == -1:
                raise ValidationError("Your price of [%s] is not higher than the max [%s]" % (record['price'], _max_offer))

            # 2. Update estate state through browsing cache
            _prop_state = cached_property['state']
            if _prop_state == 'new':
                cached_property['state'] = 'offer received'
        return super().create(vals_list)
        
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
