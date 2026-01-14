import pandas as pd
import io
import xlsxwriter
from datetime import datetime

class ExcelReportGenerator:
    def __init__(self):
        pass

    def generate_report(self, processed_slabs, b2b_df, month, year):
        """
        Generates the Excel report.
        processed_slabs: Dict { '18': df, '5': df, ... }
        """
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet("GST Report")

        # --- Formats ---
        fmt_bold = workbook.add_format({'bold': True, 'font_name': 'Arial', 'font_size': 10})
        fmt_title = workbook.add_format({'bold': True, 'font_name': 'Arial', 'font_size': 14, 'color': '#333333'})
        fmt_header = workbook.add_format({
            'bold': True, 'font_name': 'Arial', 'font_size': 9, 
            'bg_color': '#f0f0f0', 'border': 1, 'align': 'center', 'valign': 'vcenter'
        })
        fmt_cell = workbook.add_format({'font_name': 'Arial', 'font_size': 9, 'border': 1})
        fmt_cell_center = workbook.add_format({'font_name': 'Arial', 'font_size': 9, 'border': 1, 'align': 'center'})
        fmt_currency = workbook.add_format({'font_name': 'Arial', 'font_size': 9, 'border': 1, 'num_format': '#,##0.00'})
        fmt_date = workbook.add_format({'font_name': 'Arial', 'font_size': 10, 'num_format': 'yyyy-mm-dd', 'align': 'center'})
        
        # --- Company Header ---
        worksheet.write(0, 0, "WORDS & WORTHS BOOKS PVT LTD", fmt_title)
        
        current_row = 2
        
        # Columns Structure - Added GSTIN at Index 1
        columns = ["SL NO", "GSTIN", "HSN", "DESCRIPTION", "QTY", "TOTAL VALUE", "TAXABLE", "C GST", "S GST"]
        # Updated Widths
        col_widths = [6, 15, 10, 40, 8, 15, 15, 12, 12]
        
        for i, width in enumerate(col_widths):
            worksheet.set_column(i, i, width)

        # Helper to write a table block
        def write_block(df, rate_label, is_b2b=False):
            nonlocal current_row
            if df.empty:
                return

            # Block Meta Header (Date & Rate)
            report_date = datetime(year, month, 25) # defaulting to 25th of month
            
            # Row for Date and Rate - Shifted index due to new column
            worksheet.write(current_row, 3, report_date, fmt_date) 
            if not is_b2b:
                worksheet.write(current_row, 5, float(rate_label)/100, workbook.add_format({'num_format': '0.00%'}))
            else:
                worksheet.write(current_row, 5, "B2B Supply")

            current_row += 1

            # Table Headers
            for col_idx, col_name in enumerate(columns):
                worksheet.write(current_row, col_idx, col_name, fmt_header)
            current_row += 1

            # Data Rows
            sl_no = 1
            total_taxable = 0
            total_val = 0
            total_cgst = 0
            total_sgst = 0

            for _, row in df.iterrows():
                # Safe get for GSTIN as it might not exist in non-B2B slabs
                gstin_val = row.get('gstin', '')
                if pd.isna(gstin_val): gstin_val = ''

                worksheet.write(current_row, 0, sl_no, fmt_cell_center)
                worksheet.write(current_row, 1, gstin_val, fmt_cell_center) # GSTIN Column
                worksheet.write(current_row, 2, row['hsn'], fmt_cell_center)
                worksheet.write(current_row, 3, row['description'], fmt_cell)
                worksheet.write(current_row, 4, row['qty'], fmt_cell_center)
                worksheet.write(current_row, 5, row['total_value'], fmt_currency)
                worksheet.write(current_row, 6, row['final_taxable'], fmt_currency)
                worksheet.write(current_row, 7, row['cgst_amt'], fmt_currency)
                worksheet.write(current_row, 8, row['sgst_amt'], fmt_currency)
                
                total_taxable += row['final_taxable']
                total_val += row['total_value']
                total_cgst += row['cgst_amt']
                total_sgst += row['sgst_amt']
                
                current_row += 1
                sl_no += 1
            
            # Total Row for Block
            worksheet.write(current_row, 3, "Total", fmt_bold) # Shifted to column 3
            worksheet.write(current_row, 5, total_val, fmt_currency)
            worksheet.write(current_row, 6, total_taxable, fmt_currency)
            worksheet.write(current_row, 7, total_cgst, fmt_currency)
            worksheet.write(current_row, 8, total_sgst, fmt_currency)
            
            current_row += 3 # Spacing between blocks

        # --- Generate Blocks ---
        
        # 1. B2B First (Optional order, but keeping B2B separate)
        if not b2b_df.empty:
            write_block(b2b_df, "B2B", is_b2b=True)

        # 2. Slab Wise
        # Sort keys to ensure order 18, 5, 3, 0
        sorted_keys = sorted(processed_slabs.keys(), key=lambda x: float(x), reverse=True)
        
        for rate in sorted_keys:
            df = processed_slabs[rate]
            if not df.empty:
                write_block(df, rate)

        workbook.close()
        output.seek(0)
        return output