import numpy as np
import pandas as pd
import random


class DistributionEngine:
    def __init__(self):
        pass

    def distribute_slab(self, target_total_taxable, hsn_list):
        """
        Distributes a target taxable amount across a list of HSN objects.
        """

        # ---------- SAFETY GUARDS ----------
        if not hsn_list or target_total_taxable <= 0:
            return pd.DataFrame()

        df = pd.DataFrame(hsn_list)

        if df.empty:
            return df

        # Ensure required columns exist
        required_cols = {'weight', 'gst_rate'}
        if not required_cols.issubset(df.columns):
            raise ValueError(f"Missing required columns: {required_cols - set(df.columns)}")

        # ---------- RANDOMIZED WEIGHT LOGIC ----------
        df['random_factor'] = np.random.uniform(0.8, 1.2, size=len(df))
        df['effective_weight'] = df['weight'] * df['random_factor']

        total_weight = df['effective_weight'].sum()

        if total_weight == 0:
            df['share'] = 1 / len(df)
        else:
            df['share'] = df['effective_weight'] / total_weight

        # ---------- TAXABLE DISTRIBUTION ----------
        df['allocated_taxable'] = df['share'] * target_total_taxable

        # ---------- SAFE QTY CALCULATION ----------
        def calculate_qty(row):
            # 0% GST slab → fixed safe qty
            if float(row.get('gst_rate', 0)) == 0:
                return 1

            allocated = row['allocated_taxable']

            if allocated <= 0 or pd.isna(allocated):
                return 1

            min_p = max(1, row.get('min_price', 10))
            max_p = max(min_p, row.get('max_price', 100))

            unit_price = random.uniform(min_p, max_p)

            raw_qty = allocated / unit_price

            if pd.isna(raw_qty) or raw_qty <= 0:
                return 1

            return max(1, int(round(raw_qty)))

        df['qty'] = df.apply(calculate_qty, axis=1)

        # ---------- FINAL TAXABLE ----------
        df['final_taxable'] = df['allocated_taxable'].round(2)

        # ---------- BALANCING ----------
        current_sum = df['final_taxable'].sum()
        diff = round(target_total_taxable - current_sum, 2)

        if abs(diff) > 0.01:
            valid_idx = df[df['final_taxable'] > 0].index
            if not valid_idx.empty:
                idx = df.loc[valid_idx, 'final_taxable'].idxmax()
                df.loc[idx, 'final_taxable'] += diff

        df['final_taxable'] = df['final_taxable'].round(2)

        # ---------- TAX CALCULATION ----------
        df['gst_rate'] = df['gst_rate'].astype(float)

        df['cgst_amt'] = (df['final_taxable'] * (df['gst_rate'] / 100) / 2).round(2)
        df['sgst_amt'] = (df['final_taxable'] * (df['gst_rate'] / 100) / 2).round(2)
        df['total_value'] = (
            df['final_taxable'] + df['cgst_amt'] + df['sgst_amt']
        ).round(2)

        return df

    def process_b2b(self, b2b_entries):
        """
        Process manual B2B entries.
        """

        if not b2b_entries:
            return pd.DataFrame()

        df = pd.DataFrame(b2b_entries)

        if df.empty:
            return df

        df['qty'] = df['qty'].astype(int)
        df['taxable_value'] = df['taxable_value'].astype(float)
        df['gst_rate'] = df['gst_rate'].astype(float)

        df['final_taxable'] = df['taxable_value'].round(2)
        df['cgst_amt'] = (df['final_taxable'] * (df['gst_rate'] / 100) / 2).round(2)
        df['sgst_amt'] = (df['final_taxable'] * (df['gst_rate'] / 100) / 2).round(2)
        df['total_value'] = (
            df['final_taxable'] + df['cgst_amt'] + df['sgst_amt']
        ).round(2)

        return df
