from odoo import models, fields
from odoo.orm import commands


class EstatePropertyInvoiced(models.Model):
    _name = 'estate.property'
    _inherit = ['estate.property']
    _description = 'estate.property but with invoice'
    

    def SoldFunction(self):
        print("Here is the inherited version talking.")
        invoice = self._create_invoice()
        return super().SoldFunction() # type: ignore

    def _prepare_record_kwargs(self, model_name: str, kwargs: dict):
        for key, value in kwargs.items():
            if isinstance(value, models.BaseModel):
                if self.env[model_name]._fields[key].type in ('one2many', 'many2many'):
                    kwargs[key] = [commands.Command.set(value.ids)]
                else:
                    kwargs[key] = value.id

        none_keys = [key for key, val in kwargs.items() if val is None]
        for key in none_keys:
            del kwargs[key]
    
    def _create_invoice(self, move_type='out_invoice', invoice_date=None, date=None, post=False, **invoice_args):
        """
        This method quickly generates an ``account.move`` record with some quality of life helpers.
        These quality of life helpers are:

        - if `invoice_date`/`date` is filled but not the other, autofill the other date fields
        - if no `date` or `invoice_date` is passed, set the `invoice_date` to today by default
        - allow passing record immediately instead of getting the id / creating [Command.set(...)] everytime for one2many/many2many fields
        - allow passing None value in `invoice_args`, they will be filtered out before calling the move `create` method

        :param post: if True, the invoice will be posted
        :param invoice_args: additional overrides on the `account.move` `create` call
        :return: the created ``account.move`` record
        """
        # QoL: if `invoice_date`/`date` is filled but not the other, autofill the other date fields
        if move_type in self.env['account.move'].get_invoice_types(): # type: ignore
            if invoice_date and not date:
                date = invoice_date
            elif date and not invoice_date:
                invoice_date = date
            elif not date and not invoice_date:
                invoice_date = fields.Date.today()

        invoice_args |= {'date': date, 'invoice_date': invoice_date}

        # QoL: allow passing record immediately instead of getting the id / creating [Command.set(...)] everytime
        # QoL: delete all keys with None value from invoice_args
        self._prepare_record_kwargs('account.move', invoice_args)

        selling_for = self['selling_price'] * .06 # 6% of selling price
        admin_fee = 100.00

        invoice_obj = {
            'move_type': move_type,
            'partner_id': self['buyer_id'].id,
            'invoice_line_ids': [
                self._prepare_invoice_line(selling_for),
                self._prepare_invoice_line(admin_fee)
            ],
            **invoice_args,
        };
        invoice = self.env['account.move'].create([invoice_obj])

        self.env.flush_all()
        return invoice


    def _prepare_invoice_line(self, price_unit=None, product_id=None, quantity=1.0, tax_ids=None, **line_args):
        assert price_unit is not None or product_id is not None, "Either `price_unit` or `product_id` must be filled!"
        invoice_line_args = {
            'price_unit': price_unit,
            'product_id': product_id,
            'quantity': quantity,
            **line_args,
        }
        self._prepare_record_kwargs('account.move.line', invoice_line_args)
        return commands.Command.create(invoice_line_args)

