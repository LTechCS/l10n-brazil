# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today - KMEE (<http://kmee.com.br>).
#  Luis Felipe Miléo - mileo@kmee.com.br
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api
from openerp.addons import decimal_precision as dp
from openerp.tools.float_utils import float_round as round
from openerp.exceptions import ValidationError


class PaymentOrder(models.Model):
    _inherit = 'payment.order'

    mode_type = fields.Many2one('payment.mode.type', related='mode.type',
                                string='Payment Type')
    total = fields.Float(compute='_compute_total', store=True)

    # TODO: Implementar total de juros e outras despesas acessórias.
    @api.depends('line_ids', 'line_ids.amount')
    @api.one
    def _compute_total(self):
        self.total = sum(self.mapped('line_ids.amount') or [0.0])

    @api.multi
    def action_open(self):
        """
        Validacao para nao confirmar ordem de pagamento vazia
        """
        for record in self:
            if not record.line_ids:
                raise ValidationError("Impossivel confirmar linha vazia!")
        res = super(PaymentOrder, self).action_open()
        return res


class PaymentLine(models.Model):
    _inherit = 'payment.line'

    def _get_info_partner(self, cr, uid, partner_record, context=None):
        if not partner_record:
            return False
        st = partner_record.street or ''
        n = partner_record.number or ''
        st1 = partner_record.street2 or ''
        zip = partner_record.zip or ''
        city = partner_record.l10n_br_city_id.name or ''
        uf = partner_record.state_id.code or ''
        zip_city = city + '-' + uf + '\n' + zip
        cntry = partner_record.country_id and \
            partner_record.country_id.name or ''
        cnpj = partner_record.cnpj_cpf or ''
        return partner_record.legal_name or '' + "\n" + cnpj + "\n" + st \
            + ", " + n + "  " + st1 + "\n" + zip_city + "\n" + cntry

    @api.one
    @api.depends('percent_interest', 'amount_currency')
    def _compute_interest(self):
        precision = self.env['decimal.precision'].precision_get('Account')
        self.amount_interest = round(self.amount_currency *
                                     (self.percent_interest / 100),
                                     precision)
        # self.line.mode.percent_interest

    linha_digitavel = fields.Char(string=u"Linha Digitável")
    percent_interest = fields.Float(string=u"Percentual de Juros",
                                    digits=dp.get_precision('Account'))
    amount_interest = fields.Float(string=u"Valor Juros",
                                   compute='_compute_interest',
                                   digits=dp.get_precision('Account'))

    #
    # # TODO: Implementar total de juros e outras despesas acessórias.
    # @api.depends('line_ids', 'line_ids.amount')
    # @api.one
    # def _compute_total(self):
    #     self.total = sum(self.mapped('line_ids.amount') or [0.0])
