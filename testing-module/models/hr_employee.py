from datetime import datetime
from odoo import models, fields, api
from odoo.exceptions import UserError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.depends('end_date')
    def _default(self):
        for order in self:
            order.end_date = fields.Date.today()

    start_date = fields.Date(string='Entry date', store=True)
    end_date = fields.Date(string='Departure date')
    stage_duration = fields.Char(string="Years of Service", store=True)
    paul_feild = fields.Datetime(string="Paul")
    victor_feild = fields.Datetime(string="Paul"

    @api.onchange('start_date', 'end_date')
    def onchange_start_date(self):
        for i in self:
            if i.start_date and i.end_date:
                s_date = datetime.strptime(str(i.start_date), "%Y-%m-%d").date()
                e_date = datetime.strptime(str(i.end_date), "%Y-%m-%d").date()
                if s_date < e_date:
                    months = e_date.month - s_date.month
                    years = e_date.year - s_date.year
                    days = e_date.day - s_date.day

                    i.stage_duration = ('{0} years, {1} months, {2} days'.format(years, months, days))
                else:
                    msg = f'{s_date} Must be older than {e_date}'
                    raise UserError(msg)

            elif i.start_date:
                dated = fields.Date.today()
                months = dated.month - i.start_date.month
                years = dated.year - i.start_date.year
                days = dated.day - i.start_date.day

                i.stage_duration = ('{0} years, {1} months, {2} days'.format(years, months, days))
            else:
                print('The dates are yet to be set')
