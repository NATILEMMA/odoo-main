from datetime import date
import datetime
from operator import index
from pickle import TRUE
from tokenize import group
from odoo import api, fields, models
from odoo.exceptions import UserError
import os
import fitz
from odoo.modules.module import get_module_resource
from PyPDF2 import PdfFileReader, PdfFileWriter

class BidDocument(models.Model):
    _name = 'bid.document'
    _description = 'Bid document for tender'


    reference_no = fields.Char(string='Bid Document Reference', required=True,
                          readonly=True, default='New', index=True)
    company_id = fields.Many2one('res.company', string=  'Company',default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True)
    subject_of_procurment  = fields.Char('Subject of Procurement')
    reference_number = fields.Char('Procurement Reference Number')
    project_name = fields.Char('Project Name')
    issue_date = fields.Date('Date of Issue of Bidding Document')
    location = fields.Char('Location')
    bid_bond = fields.Monetary('Bid Bond')
    validity_day = fields.Integer('Validity Days')
    delivery_date = fields.Date('Date of Delivery')

    file_content = fields.Html('Bid Content', compute = "loading_file")

    @api.model
    def create(self, vals):
        vals['reference_no'] = self.env['ir.sequence'].next_by_code('bid.document')
        res = super(BidDocument, self).create(vals)
        return res


    @api.depends('file_content')
    def loading_file(self):

        saved_variables = self.env['bid.document'].search([('reference_no','=',self.reference_no)])
        pdf_document = get_module_resource('tender', 'data', "final ERP bid docment[35].pdf")
        pdf = fitz.open(pdf_document)

        self.file_content = ""
        
        search_terms = ['An Implementation of Enterprise Resource Planning',
                    'AAPPPDS/SA/2014/NCB/PIS/1/09/2014',
                    'An Implementation of Enterprise Resource Planning (ERP) for Addis Ababa Democracy Building Office.','june,8,2022',
                    'Addis Ababa']

        to_be_placed = [saved_variables['subject_of_procurment'], saved_variables['reference_number'],
                        saved_variables['project_name'], saved_variables['issue_date'].strftime("%b,%d,%Y"),
                        saved_variables['location']]
        count=0
        for current_page in range(len(pdf_document)):
            print("len(pdf_document", len(pdf_document))
            page = pdf.load_page(current_page)
            print("page", page)
            page1text = page.get_text('xhtml')
            print("page1text", page1text)
           
            
            if count < 2:
                if page.search_for('(ERP) .'):
                    page1text = page1text.replace('(ERP) .', ' ')
                    count+=1

                if page.search_for('(ERP) for Addis Ababa Democracy Building Office.'):
                    page1text = page1text.replace('(ERP) for Addis Ababa Democracy Building Office.', ' ')
                    count+=1
                
            for i in range(len(search_terms)) :
                print("i",i)
                if page.search_for(search_terms[i]):
                    print("search_terms[i]",search_terms[i], "to_be_placed[i]", to_be_placed[i])
                    page1text = page1text.replace(search_terms[i], to_be_placed[i] )
            self.file_content += page1text

            
