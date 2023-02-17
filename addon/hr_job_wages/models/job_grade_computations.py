"""This file will compute the wage of different job titles"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError  

class Grade(models.Model):
  _name="hr.job.grade"
  _description="This class will create grades for a job positions"

  name = fields.Char(required=True, copy=False, string="Grade Name")
  job_grade_id = fields.Many2one(related="job_dup_id.name")
  minimum_wage = fields.Float(required=True, copy=False)
  maximum_wage = fields.Float(required=True, copy=False)
  job_dup_id = fields.Many2one('hr.job.dup')

  _sql_constraints = [
                      ('check_on_maximum_wage', 'CHECK(maximum_wage > 0 AND maximum_wage > minimum_wage)', 'Maximum wage must be more than Minimum Wage and 0'),
                      ('check_on_minimum_wage', 'CHECK(minimum_wage > 0 AND minimum_wage < maximum_wage)', 'Minimum wage must be less than Maximum Wage and greater than 0')
                     ]


class JobDuplicate(models.Model):
  _name="hr.job.dup"
  _description="This class will handle the addtion of job grades to their respective job positions"

  name = fields.Many2one('hr.job', required=True)
  job_dup_ids = fields.One2many('hr.job.grade', 'job_dup_id' ,required=True)


  @api.onchange('name')
  def _compute_name_repeation(self):
     """This function will check to see if there is repeation in job positions"""
     if self.name:
       all_values = self.env['hr.job.dup'].search([])
       # Find a mapped value of all the job positions with their given ids, hence = mapped('name.id')
       all_job_ids = all_values.mapped('name.id')
       if self.name.id in all_job_ids:
          job_position = self.env['hr.job'].browse(self.name.id)
          message = f"A job position by the name {job_position.name} already exists."
          raise UserError(_(message))


class JobWageCheck(models.Model):
  _inherit="hr.contract"

  grade_id = fields.Many2one('hr.job.grade', domain="[('job_grade_id', '=', job_id)]", required=True, string="Grade")

  @api.onchange('wage')
  def check_wage_range(self):
    """This function will check if wage matches to job grade range"""
    minimum = self.grade_id.minimum_wage
    maximum = self.grade_id.maximum_wage
    if (self['wage'] < minimum):
      Message = "Wage must be more than the company Minimum wage scale of " + str(minimum)
      raise UserError(_(Message))
    elif (self['wage'] > maximum):
      Message = "Wage must be less than the company Maximum wage scale of " + str(maximum)
      raise UserError(_(Message))
