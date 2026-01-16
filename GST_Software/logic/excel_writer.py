import pandas as pd
import io
import xlsxwriter
from datetime import datetime


class ExcelReportGenerator:
    def __init__(self):
        pass

    def generate_report(self, processed_slabs, b2b_df, month, year):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet("GST Report")

        # --- Formats ---
        fmt_bold = workbook.add_format({'bold': True, 'font_name': 'Arial', 'font_size': 10})
        fmt_title = workbook.add_format({'bold': True, 'font_name': 'Arial', 'font_size': 14})
        fmt_header = workbook.add_format({
            'bold': True, 'font_name': 'Arial', 'font_size': 9,
            'bg_color': '#f0f0f0', 'border': 1, 'align': 'center'
        })
        fmt_cell = workbook.add_format({'font_name': 'Arial', 'font_size': 9, 'border': 1})
        fmt_cell_center = workbook.add_format({'font_name': 'Arial', 'font_size': 9, 'border': 1, 'align': 'center'})
        fmt_currency = workbook.add_format({'font_name': 'Arial', 'font_size': 9, 'border': 1, 'num_format': '#,##0.00'})
        fmt_date = workbook.add_format({'font_name': 'Arial', 'font_size': 10, 'num_format': 'yyyy-mm-dd', 'align': 'center'})

        # --- Header ---
        worksheet.write(0, 0, "WORDS & WORTHS BOOKS PVT LTD", fmt_title)
        current_row = 2

        columns = ["SL NO", "GSTIN", "HSN", "DESCRIPTION", "QTY", "TOTAL VALUE", "TAXABLE", "C GST", "S GST"]
        col_widths = [6, 15, 10, 40, 8, 15, 15, 12, 12]

        for i, width in enumerate(col_widths):
            worksheet.set_column(i, i, width)

        # -------- SAFE FLOAT HELPER --------
        def safe_float(val):
            if val is None or pd.isna(val):
                return 0.0
            return float(val)

        # -------- BLOCK WRITER --------
        def write_block(df, rate_label, is_b2b=False):
            nonlocal current_row
            if df.empty:
                return

            report_date = datetime(year, month, 25)

            worksheet.write(current_row, 3, report_date, fmt_date)
            if not is_b2b:
                worksheet.write(current_row, 5, float(rate_label) / 100,
                                workbook.add_format({'num_format': '0.00%'}))
            else:
                worksheet.write(current_row, 5, "B2B Supply")

            current_row += 1

            for col_idx, col_name in enumerate(columns):
                worksheet.write(current_row, col_idx, col_name, fmt_header)
            current_row += 1

            sl_no = 1
            total_taxable = 0.0
            total_val = 0.0
            total_cgst = 0.0
            total_sgst = 0.0

            for _, row in df.iterrows():
                gstin_val = row.get('gstin', '')
                if pd.isna(gstin_val):
                    gstin_val = ''

                qty = int(row.get('qty', 0))

                total_value = safe_float(row.get('total_value'))
                final_taxable = safe_float(row.get('final_taxable'))
                cgst_amt = safe_float(row.get('cgst_amt'))
                sgst_amt = safe_float(row.get('sgst_amt'))

                worksheet.write(current_row, 0, sl_no, fmt_cell_center)
                worksheet.write(current_row, 1, gstin_val, fmt_cell_center)
                worksheet.write(current_row, 2, row.get('hsn', ''), fmt_cell_center)
                worksheet.write(current_row, 3, row.get('description', ''), fmt_cell)
                worksheet.write(current_row, 4, qty, fmt_cell_center)
                worksheet.write(current_row, 5, total_value, fmt_currency)
                worksheet.write(current_row, 6, final_taxable, fmt_currency)
                worksheet.write(current_row, 7, cgst_amt, fmt_currency)
                worksheet.write(current_row, 8, sgst_amt, fmt_currency)

                total_taxable += final_taxable
                total_val += total_value
                total_cgst += cgst_amt
                total_sgst += sgst_amt

                current_row += 1
                sl_no += 1

            worksheet.write(current_row, 3, "Total", fmt_bold)
            worksheet.write(current_row, 5, total_val, fmt_currency)
            worksheet.write(current_row, 6, total_taxable, fmt_currency)
            worksheet.write(current_row, 7, total_cgst, fmt_currency)
            worksheet.write(current_row, 8, total_sgst, fmt_currency)

            current_row += 3

        # -------- GENERATION --------
        if not b2b_df.empty:
            write_block(b2b_df, "B2B", is_b2b=True)

        sorted_keys = sorted(processed_slabs.keys(), key=lambda x: float(x), reverse=True)
        for rate in sorted_keys:
            df = processed_slabs[rate]
            if not df.empty:
                write_block(df, rate)

        workbook.close()
        output.seek(0)
        return output
