# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'


    def write(self, vals):
        if self.env.context.get('skip_price_sync'):
            return super().write(vals)

        res = super().write(vals)

        if 'list_price' in vals:
            active_company = self.env.company

            for record in self:
                if not record.default_code:
                    continue

                other_companies = self.env['res.company'].search([
                    ('id', '!=', active_company.id)
                ])

                for company in other_companies:
                    # ✅ reemplazado con with_company()
                    target_product = self.env['product.template'].with_company(company).sudo().search([
                        ('default_code', '=', record.default_code),
                        ('company_id', '=', company.id)
                    ], limit=1)

                    if target_product:
                        target_product.with_context(skip_price_sync=True).sudo().write({
                            'list_price': vals['list_price']
                        })

        return res



    # def write(self, vals):

    #     if self.env.context.get('skip_price_sync'):
    #         return super().write(vals)

    #     res = super().write(vals)

    #     if 'list_price' in vals:
    #         active_company = self.env.company  # Empresa desde donde se hace el cambio

    #         for record in self:
    #             if not record.default_code:
    #                 continue

    #             # Buscar empresas diferentes a la actual
    #             other_companies = self.env['res.company'].search([
    #                 ('id', '!=', active_company.id)
    #             ])

    #             for company in other_companies:
    #                 # Buscar producto con el mismo código en la otra empresa
    #                 target_product = self.env['product.template'].with_context(force_company=company.id).sudo().search([
    #                     ('default_code', '=', record.default_code),
    #                     ('company_id', '=', company.id)
    #                 ], limit=1)

    #                 if target_product:
    #                     # Actualizar precio en la empresa remota
    #                     target_product.with_context(skip_price_sync=True).sudo().write({
    #                         'list_price': vals['list_price']
    #                     })

    #     return res
