from odoo import models, api, fields

'''
    product_delivery_report" is folder name and "product_shop_wise_delivery" is template name
'''

class WizardProductDeliver(models.TransientModel):
    _name = 'wizard.product.delivery'

    start_date = fields.Datetime(string='From Date')
    end_date = fields.Datetime(string='End Date')
    shop_id = fields.Many2one('sale.shop', string='Shop')

    @api.multi
    def print_report(self, data):
        return self.env['report'].get_action(self, 'product_delivery_report.product_shop_wise_delivery', data=data)

