from odoo import fields, models, api
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta

class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = "A property that you can probably not afford."
    _order = "id desc"

    prop_type = fields.Many2one("estate.property.realtype")
    tags_ids = fields.Many2many("estate.property.type")

    # Buyer stored as a partner reference
    salesman_id = fields.Many2one("res.users", string="Salesman", default=lambda self: self.env.user)
    buyer_id = fields.Many2one("res.partner", string="Buyer")
    active = fields.Boolean('Active', default=True)
    state=fields.Selection(
        selection=[
            ('new', 'New'),
            ('offer received', 'Offer Received'),
            ('accepted', 'Accepted'),
            ('sold', 'Sold'),
            ('cancelled', 'Cancelled'),
        ]
    )

    name = fields.Char('Name', required=True, translate=True)
    description = fields.Text('Description')
    postcode = fields.Char('Postcode')
    date_availability = fields.Date('Available From', default=date.today()+timedelta(days=90))

    expected_price = fields.Float('Expected Price', required=True, store=True)
    selling_price = fields.Float('Selling Price', readonly=True)

    best_price = fields.Float(compute="_compute_best_price")

    bedrooms = fields.Integer('Bedrooms', default=2)
    living_area = fields.Integer('Living Area (sqm)')
    facades = fields.Integer('Facades')
    garage = fields.Boolean('Garage')
    garden = fields.Boolean('Garden')
    garden_area = fields.Integer('Garden Area (sqm)')
    garden_orientation = fields.Selection(
        selection=[
            ('north', 'North'),
            ('south', 'South'),
            ('east', 'East'),
            ('west', 'West')
        ],
        string='Garden Orientation'
    )

    total_area = fields.Float(compute="_compute_total_area")

    estate_offers = fields.One2many("estate.offer", inverse_name="estate_id")

    _check_expected_price_above_zero = models.Constraint(
        "CHECK(expected_price > 0)",
        "Expected price must be above 0"
    )
    _check_selling_price_above_zero = models.Constraint(
        "CHECK(selling_price >= 0)",
        "Selling price must be at or above 0"
    )
    _check_uniqueness_name = models.Constraint(
        'unique(name)',
        "Name must be unique."
    )

    def SoldFunction(self):
        self.env.user
        if self.state == 'cancelled':
            raise UserError("Cancelled property cannot be sold!")
        self.state = 'sold'
        return True
    
    def CancelFunction(self):
        if self.state == 'sold':
            raise UserError("Sold properties cannot be cancelled")
        self.state = 'cancelled'
        return True

    def _salesman_default_(self):
        if not self.salesman_id:
            self.salesman_id = self.env.user

    @api.depends("estate_offers.price")
    def _compute_best_price(self):
        for record in self:
            if record.estate_offers:
                record.best_price = max(record.estate_offers.mapped('price'))
            else:
                record.best_price = 0

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.onchange("estate_offers")
    def _compute_state(self):
        if len(self.estate_offers) < 1:
            self.state = 'new'
            return;
        for o_st in self.estate_offers.mapped('state'):
            if o_st == 'refused':
                self.state = 'offer received'
            if o_st == 'accepted':
                self.state = 'accepted'
                break

    @api.onchange("garden")
    def _set_garden_related_info(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = None



# class EstatePropertyInline(models.Model):
#     _name = "estate.property.inline"
#     _description = "estate.property inline version"

#     _inline_model_id = fields.One2many("estate.property", "_inline_id", index=True)

#     name = fields.Char('Name', required=True, translate=True)
#     # name = fields.Char()
#     expected_price = fields.Float('Expected Price', required=True, store=True)
#     # expected_price = fields.Float()
#     # state = fields.Selection()    
#     state=fields.Selection(
#         selection=[
#             ('new', 'New'),
#             ('offer received', 'Offer Received'),
#             ('accepted', 'Accepted'),
#             ('sold', 'Sold'),
#             ('cancelled', 'Cancelled'),
#         ]
#     )
