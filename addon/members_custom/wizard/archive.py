"""This file will deal with the archiving members"""

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import date, datetime
import base64


class ArchiveMembers(models.TransientModel):
    _name="archive.members.wizard"
    _description="This model will handle the archiving members"

    reason = fields.Text(translate=True)


    def action_done(self):
        """This function will be the action for wizards"""
        member = self.env['res.partner'].browse(self.env.context.get('active_ids'))
        if member.user_name:
            user = self.env['res.users'].search([('partner_id', '=', member.id)])
            user.write({
                'active': False
            })
        member.write({
            'active': False,
            'reason': self.reason
        })

class ArchiveCandidate(models.TransientModel):
    _name="archive.candidate.wizard"
    _description="This model will handle the archiving of members"

    reason = fields.Text(translate=True)


    def action_done(self):
        """This function will be the action for wizards"""
        candidate = self.env['candidate.members'].browse(self.env.context.get('active_ids'))
        candidate.write({
            'active': False,
            'reason': self.reason
        })

class ArchiveSupporter(models.TransientModel):
    _name="archive.supporter.wizard"
    _description="This model will handle the archiving of members"

    reason = fields.Text(translate=True)


    def action_done(self):
        """This function will be the action for wizards"""
        candidate = self.env['supporter.members'].browse(self.env.context.get('active_ids'))
        candidate.write({
            'active': False,
            'reason': self.reason
        })


class ArchiveDonor(models.TransientModel):
    _name="archive.donor.wizard"
    _description="This model will handle the archiving of members"

    reason = fields.Text(translate=True)


    def action_done(self):
        """This function will be the action for wizards"""
        candidate = self.env['donors'].browse(self.env.context.get('active_ids'))
        candidate.write({
            'active': False,
            'reason': self.reason
        })

class CreateMember(models.TransientModel):
    _name="create.member.wizard"
    _description="This model will handle the creation of members"

    membership_org = fields.Many2one('membership.organization')
    member_responsibility = fields.Many2one('members.responsibility')
    start_of_membership = fields.Selection(selection=[(str(num), num) for num in range(1980, (datetime.now().year)+1 )], string='Membership Start Year')
    stock = fields.Selection(selection=[('selected', 'Selected'), ('not selected', 'Not Selected')], default='not selected')
    income = fields.Float(store=True)
    national_id = fields.Char(translate=True)

    def action_done(self):
        """This function will be the action for wizards"""
        partner = self.env['res.partner'].browse(self.env.context.get('active_ids'))
        if self.national_id:
            all_partner = self.env['res.partner'].search([('national_id', '=', self.national_id)])
            if all_partner:
                raise UserError(_("A Member With This National Id Already Exists. You might be duplicating a record."))
            else:
                if self.membership_org and self.member_responsibility and self.start_of_membership:
                    partner.write({
                        'membership_org': self.membership_org.id,
                        'member_responsibility': self.member_responsibility.id,
                        'start_of_membership' :self.start_of_membership,
                        'stock': self.stock,
                        'income': self.income,
                        'national_id': self.national_id
                    })
                else:
                   raise UserError(_("Please Add All The Required Fields")) 
        else:
            raise UserError(_("Please Add A National ID"))


class CreateLeader(models.TransientModel):
    _name="create.leader.wizard"
    _description="This model will handle the creation of leaders"

    membership_org = fields.Many2one('membership.organization')
    leader_responsibility = fields.Many2one('leaders.responsibility')
    experience = fields.Char(translate=True)
    leadership_status = fields.Selection(selection=[('active', 'Active'), ('inactive', 'Inactive')], default='inactive')

    def action_done(self):
        """This function will be the action for wizards"""
        partner = self.env['res.partner'].browse(self.env.context.get('active_ids'))
        if self.membership_org and self.leader_responsibility and self.experience:
            partner.write({
                'membership_org': self.membership_org.id,
                'leader_responsibility': self.leader_responsibility.id,
                'experience': self.experience,
                'leadership_status': self.leadership_status
            })
        else:
            raise UserError(_("Please Add All The Given Fields"))

class CreateLeague(models.TransientModel):
    _name="create.league.wizard"
    _description="This model will handle the creation of leagues"

    league_type = fields.Selection(selection=[('young', 'Youngsters'), ('women', 'Women')])
    league_org = fields.Selection(selection=[('labourer', 'Labourer'), ('urban', 'Urban Dweller')])
    league_status = fields.Selection(selection=[('league member', 'League Member'), ('league leader', 'League Leader')])
    start_of_league = fields.Selection(selection=[(str(num), num) for num in range(2001, (datetime.now().year)+1 )], string='League Start Year')


    def action_done(self):
        """This function will be the action for wizards"""
        partner = self.env['res.partner'].browse(self.env.context.get('active_ids'))
        if self.league_org and self.league_type and self.league_status and self.start_of_league:
            partner.write({
                'league_type': self.league_type,
                'league_org': self.league_org,
                'start_of_league': self.start_of_league,
                'league_status': self.league_status
            })
        else:
            raise UserError(_("Please Add All The Given Fields"))


class CreateAttachment(models.TransientModel):
    _name="attachment.wizard"
    _description="This model will handle the archiving of members"

    name = fields.Char(translate=True)
    res_model = fields.Char()
    res_id = fields.Many2oneReference('Resource ID', model_field='res_model')
    attachment_type = fields.Many2one('attachment.type')
    description = fields.Text('Description')
    type = fields.Selection([('url', 'URL'), ('binary', 'File')])
    datas = fields.Binary()


    def action_done(self):
        """This function will be the action for wizards"""
        wizard = self.env['attachment.wizard'].search([('id', '=', self.id)])
        if self.name and self.attachment_type and self.datas:
            attachment = self.env['ir.attachment'].sudo().create({
                'name': self.name,
                'res_model': wizard.res_model,
                'res_id': wizard.res_id,
                'attachment_type': self.attachment_type.id,
                'description': self.description,
                'type': 'binary',
                'datas': self.datas
            })
        else:
            raise UserError(_("Please Add All The Given Fields"))


class CreateLeagueMember(models.TransientModel):
    _name="create.from.league.wizard"
    _description="This model will handle the creation of members"

    membership_org = fields.Many2one('membership.organization')
    member_responsibility = fields.Many2one('members.responsibility')
    stock = fields.Selection(selection=[('selected', 'Selected'), ('not selected', 'Not Selected')], default='not selected')
    income = fields.Float()
    start_of_membership = fields.Selection(selection=[(str(num), num) for num in range(1980, (datetime.now().year)+1 )], string='Membership Start Year')
    national_id = fields.Char(translate=True)

    def action_done(self):
        """This function will be the action for wizards"""
        partner = self.env['res.partner'].browse(self.env.context.get('active_ids'))
        if self.national_id:
            all_partner = self.env['res.partner'].search([('national_id', '=', self.national_id)])
            if all_partner:
                raise UserError(_("A Member With This National Id Already Exists. You might be duplicating a record."))
            else:
                if self.membership_org and self.member_responsibility and self.start_of_membership:
                    partner.write({
                        'membership_org': self.membership_org.id,
                        'member_responsibility': self.member_responsibility.id,
                        'start_of_membership': self.start_of_membership,
                        'stock': self.stock,
                        'income': self.income,
                        'national_id': self.national_id
                    })
                else:
                   raise UserError(_("Please Add All The Required Fields")) 
        else:
            raise UserError(_("Please Add A National ID"))


class CreateCandidateMember(models.TransientModel):
    _name="create.from.candidate.wizard"
    _description="This model will handle the creation of members"

    partner_id = fields.Many2one('res.partner')
    membership_org = fields.Many2one('membership.organization')
    member_responsibility = fields.Many2one('members.responsibility')
    start_of_membership = fields.Selection(selection=[(str(num), num) for num in range(1980, (datetime.now().year)+1 )], string='Membership Start Year')
    stock = fields.Selection(selection=[('selected', 'Selected'), ('not selected', 'Not Selected')], default='not selected')
    national_id = fields.Char(translate=True)

    def action_done(self):
        """This function will be the action for wizards"""
        wizard = self.env['create.from.candidate.wizard'].search([('id', '=', self.id)])
        if self.national_id:
            all_partner = self.env['res.partner'].search([('national_id', '=', self.national_id)])
            if all_partner:
                raise UserError(_("A Member With This National Id Already Exists. You might be duplicating a record."))
            else:
                if self.membership_org and self.member_responsibility and self.start_of_membership:
                    wizard.partner_id.write({
                        'membership_org': self.membership_org.id,
                        'member_responsibility': self.member_responsibility.id,
                        'start_of_membership': self.start_of_membership,
                        'stock': self.stock,
                        'national_id': self.national_id
                    })
                else:
                   raise UserError(_("Please Add All The Required Fields")) 
        else:
            raise UserError(_("Please Add A National ID"))