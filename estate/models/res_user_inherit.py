from odoo import fields, models

class SalesmanUser(models.Model):
    _name = 'res.users'
    _inherit = ['res.users']
    properties_selling = fields.One2many("estate.property", "salesman_id")
    # company_ids = fields.Many2many(relation="salesman_company_ids")
