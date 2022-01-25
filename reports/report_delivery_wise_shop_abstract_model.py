from odoo import models, fields, api
from datetime import datetime, timedelta

class AbstractModelReportDeviver(models.AbstractModel):
    _name = 'report.product_delivery_report.product_shop_wise_delivery'

    def data_for_delivery_report(self, start_date, end_date, shop_id):

        sale_order = self.env['sale.order'].search(
            [('create_date', '>=', start_date), ('create_date', '<=', end_date), ('invoice_status', '=', 'invoiced'),
             ('shop_id', '=', shop_id)])

        data_set = set()
        sale_origin = []

        for rec in sale_order:
            sale_origin.append(rec.name)
            for i in rec.order_line:
                data_set.add(i.product_id)

        data_pro = []
        data_another_pro=[]
        for rec in data_set:
            dict_order_line = {}
            dict_order_line2 = {}
            sale_order_line = self.env['sale.order.line'].search(
                [('create_date', '>=', start_date), ('create_date', '<=', end_date), ('product_id', '=', rec.id)])
            qty = 0
            for i in sale_order_line:
                qty = qty + i.product_uom_qty
                unit_price = i.price_unit
                total_price = qty * i.price_unit
            dict_order_line['name'] = rec.product_tmpl_id.name
            dict_order_line['id'] = rec.id
            dict_order_line['quantity'] = qty
            dict_order_line['unit_price'] = unit_price
            dict_order_line['total_unit_price'] = total_price
            data_pro.append(dict_order_line)



            # calculating cost price of each product
            for i in data_pro:
                product_object = self.env['product.product'].browse([i['id']])
                i['cost_price'] = product_object.product_tmpl_id.standard_price


            # cost benefit
            for i in data_pro:
                total_cost = i['quantity'] * i['cost_price']
                i['total_cost_price'] = total_cost
                total_benifit = i['total_unit_price'] - i['total_cost_price']
                i['total_benefit'] = total_benifit


        # for refund data

        data_set_2 = set()

        account_invoice = self.env['account.invoice'].search(
            [('create_date', '>=', start_date), ('create_date', '<=', end_date), ('type', '=', 'out_refund')])

        for i in account_invoice:

            account_invoice_2 = self.env['account.invoice'].search(
                [('create_date', '>=', start_date), ('create_date', '<=', end_date), ('number', '=', i.origin)])

            for j in account_invoice_2:
                for k in sale_origin:
                    if k == j.origin:
                        for l in i.invoice_line_ids:
                            data_set_2.add(l.product_id)

        result = []
        for rec in data_set_2:
            dict_account_invoice_line = {}
            account_inv_line = self.env['account.invoice.line'].search(
                [('create_date', '>=', start_date), ('create_date', '<=', end_date), ('product_id', '=', rec.id),
                 ('price_subtotal_signed', '<=', 0)])

            qty = 0

            for pro in account_inv_line:
                qty += pro.quantity
                unit_price = pro.price_unit
                total_price = qty * pro.price_unit

            dict_account_invoice_line['name'] = rec.product_tmpl_id.name
            dict_account_invoice_line['quantity'] = qty
            dict_account_invoice_line['unit_price'] = unit_price
            dict_account_invoice_line['id'] = rec.id
            dict_account_invoice_line['refund_total_unit_price'] = total_price
            result.append(dict_account_invoice_line)

            for i in result:
                product_object = self.env['product.product'].browse([i['id']])
                i['refund_cost_price'] = product_object.product_tmpl_id.standard_price

            # Refund cost benefit
            for i in result:
                refund_benefit_count = i['quantity'] * i['refund_cost_price']
                i['refund_total_cost_price'] = refund_benefit_count
                total_benifit = i['refund_total_unit_price'] - i['refund_total_cost_price']
                i['refund_total_benefit'] = total_benifit


        shop = self.env['sale.shop'].search([('id', '=', shop_id)])
        shop_name = shop.name



        # Net Quantity
        net_data=[]
        collection_product_set=set()
        for i in data_pro:
            product_object_collection=self.env['product.product'].browse([i['id']])
            collection_product_set.add(product_object_collection)

        refund_product_set=set()
        for i in result:
            product_object_refund=self.env['product.product'].browse([i['id']])
            refund_product_set.add(product_object_refund)
        not_refund_product=collection_product_set - refund_product_set
        refund_product=collection_product_set & refund_product_set


        for i in data_pro:
            for j in result:
                if j['id']==i['id']:
                    net_quantity= i['quantity']-j['quantity']
                    dict_net_quantity={}
                    dict_net_quantity['name'] = j['name']
                    dict_net_quantity['total_net_quantity'] =net_quantity
                    dict_net_quantity['id'] =j['id']
                    dict_net_quantity['net_unit_price'] =j['unit_price']
                    dict_net_quantity['net_total_unit_price'] =j['refund_total_unit_price']
                    dict_net_quantity['net_cost_price'] =j['refund_cost_price']
                    net_data.append(dict_net_quantity)


        for i in data_pro:
            for j in not_refund_product:
                if j.id==i['id']:
                    dict_net_quantity = {}
                    dict_net_quantity['name'] = i['name']
                    dict_net_quantity['total_net_quantity'] =i['quantity']
                    dict_net_quantity['net_unit_price'] =i['unit_price']
                    dict_net_quantity['net_total_unit_price'] =i['total_unit_price']
                    dict_net_quantity['net_cost_price'] =i['cost_price']
                    net_data.append(dict_net_quantity)


        # Net cost benefit
        for i in net_data:
            net_total_cost_price = i['total_net_quantity'] * i['net_cost_price']
            i['net_total_cost'] = net_total_cost_price
            net_total_benifit = i['net_total_unit_price'] - i['net_total_cost']
            i['net_total_benefit'] = net_total_benifit


        return data_pro, result, shop_name, net_data



    @api.model
    def render_html(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('product_delivery_report.product_shop_wise_delivery')

        order_lines, order_refund_line, shop_name, net_data = self.data_for_delivery_report(docs.start_date, docs.end_date,
                                                                                  docs.shop_id.id)
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        sd = datetime.strptime(docs.start_date, DATETIME_FORMAT)
        ed = datetime.strptime(docs.end_date, DATETIME_FORMAT)
        sd_convert = sd + timedelta(hours=6, minutes=00)
        ed_convert = ed + timedelta(hours=6, minutes=00)


        docargs = {
            'doc_model': data.get('model'),
            'docs': self,
            'from_date': docs.start_date,
            'to_date': docs.end_date,
            'order_line': order_lines,
            'refund_order_line': order_refund_line,
            'start_date': sd_convert,
            'end_date': ed_convert,
            'shop_name': shop_name,
            'net_data': net_data,
        }

        return self.env['report'].render('product_delivery_report.product_shop_wise_delivery', docargs)
