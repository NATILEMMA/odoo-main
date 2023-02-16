from odoo import models
import string


class PayrollReport(models.AbstractModel):
    _name = 'report.xlsx_payroll_report.xlsx_payroll_report' 
    _inherit = 'report.odoo_report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        print("lines", lines)
        format1 = workbook.add_format({'font_size':12, 'align': 'vcenter', 'bold': True, 'bg_color':'#d3dde3', 'color':'black', 'bottom': True, })
        format2 = workbook.add_format({'font_size':12, 'align': 'vcenter', 'bold': True, 'bg_color':'#edf4f7', 'color':'black','num_format': '#,##0.00'})
        format3 = workbook.add_format({'font_size':11, 'align': 'vcenter', 'bold': False, 'num_format': '#,##0.00'})
        format3_colored = workbook.add_format({'font_size':11, 'align': 'vcenter', 'bg_color':'#f7fcff', 'bold': False, 'num_format': '#,##0.00'})
        format4 = workbook.add_format({'font_size':12, 'align': 'vcenter', 'bold': True})
        format5 = workbook.add_format({'font_size':12, 'align': 'vcenter', 'bold': False})
        # sheet = workbook.add_worksheet('Payrlip Report')

        # Fetch available salary rules:
        used_structures = []
        for sal_structure in lines.slip_ids.struct_id:
            if sal_structure.id not in used_structures:
                used_structures.append([sal_structure.id,sal_structure.name])


        # Logic for each workbook, i.e. group payslips of each salary structure into a separate sheet:
        struct_count = 1
        for used_struct in used_structures:
            # Generate Workbook
            sheet = workbook.add_worksheet(str(struct_count)+ ' - ' + str(used_struct[1]) )
            cols = list(string.ascii_uppercase) + ['AA', 'AB', 'AC', 'AD', 'AE', 'AF', 'AG', 'AH', 'AI', 'AJ', 'AK', 'AL', 'AM', 'AN', 'AO', 'AP', 'AQ', 'AR', 'AS', 'AT', 'AU', 'AV', 'AW', 'AX', 'AY', 'AZ']
            rules = []
            col_no = 2
            # Fetch available salary rules:

            for rule in lines.slip_ids.struct_id:
                for arule in rule.rule_ids:
                    arules = {
                        'name' : arule.name,
                        'code' : arule.code,
                        'parant_stracture_name' : rule.name
                    }
                    rules.append(arules)
                
        
            #Report Details:
            for item in lines.slip_ids:
                if item.struct_id.id == used_struct[0]:
                    batch_period = str(item.date_from.strftime('%B %d, %Y')) + '  To  ' + str(item.date_to.strftime('%B %d, %Y'))
                    company_name = item.company_id.name
                    break
            #Company Name
            sheet.write(0,0,company_name,format4)
    
            sheet.write(0,2,'Payslip Period:',format4)
            sheet.write(0,3,batch_period,format5)

            sheet.write(1,2,'Payslip Structure:',format4)
            sheet.write(1,3,used_struct[1],format5)
       
            # List report column headers:
            sheet.write(2,0,'Employee Name',format1)
            sheet.write(2,1,'Department',format1)
            columns = 2
            for rule in rules:
                 sheet.write(2,columns, rule['name'],format1)
                 columns+=1

            # Generate names, dept, and salary items:
            e_name = 3
            has_payslips = False
            for slip in lines.slip_ids:
                if lines.slip_ids:
                    has_payslips = True
                sheet.write(e_name, 0, slip.employee_id.name, format3)
                sheet.write(e_name, 1, slip.employee_id.department_id.name, format3)
                columns = 2
                for line in slip.line_ids:
                    sheet.write(e_name, columns, line.amount, format3)
                    columns += 1 
                e_name += 1

            total_salary_cols = 2
            for summary in lines.summary_id:
                sheet.write(e_name, total_salary_cols, summary.amount, format3)
                total_salary_cols+=1

            # Generate summission row at report end:
            sum_x = e_name
            if has_payslips:
                sheet.write(sum_x,0,'Total',format2)
                sheet.write(sum_x,1,'',format2)
                for i in range(2,col_no):
                    #sum_start = cols[i] + '3'
                    #sum_end = cols[i] + str(sum_x)
                    #sum_range = '{=SUM(' + str(sum_start) + ':' + sum_end + ')}'
                    #print(sum_range)
                    #sheet.write_formula(sum_x,i,sum_range,format2)
                    i += 1
            sheet.write(sum_x+2, 1, 'Prepared By', format1)
            sheet.write(sum_x+2, 8, 'Checked By', format1)
            sheet.write(sum_x+2, 12, 'Approved By', format1)

            # set width and height of colmns & rows:
            sheet.set_column('A:A',35)
            sheet.set_column('B:B',20)
            # for rule in rules:
            #     sheet.set_column(rule[3],rule[4])
            sheet.set_column('C:C',20)
            sheet.set_column('D:D',20)
            sheet.set_column('E:E',20)
            struct_count += 1
        
