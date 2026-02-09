import numpy as np
import pandas as pd
import random
import math

class DistributionEngine:
    def __init__(self):
        pass

    # ------------------------------------------------------------
    # MAIN DISTRIBUTION LOGIC (ENHANCED)
    # ------------------------------------------------------------
    def distribute_slab(self, target_total_taxable, hsn_list, seed=None):
        """
        Enhanced distribution engine focused on realistic outcomes.
        
        Improvements:
        1. Aggressive Weighting: Weight 10 dominates Weight 1 significantly (Pareto style).
        2. Price Anchoring: Quantities are derived from the 'Typical Price' to ensure
           unit prices remain realistic (e.g., a book stays around ₹500, not ₹5000).
        3. Bounds Checking: Strict adherence to min/max prices.
        4. Chaos Factor: Ensures random distribution even if weights are identical.
        """

        if not hsn_list or target_total_taxable <= 0:
            return pd.DataFrame()

        # --------------------------------------------------------
        # Deterministic randomness
        # --------------------------------------------------------
        if seed:
            random.seed(seed)
            np.random.seed(abs(hash(seed)) % (2**32))

        df = pd.DataFrame(hsn_list).copy()

        # --------------------------------------------------------
        # Clean & normalize inputs
        # --------------------------------------------------------
        df['weight'] = pd.to_numeric(df.get('weight', 0), errors='coerce').fillna(0)
        df['min_price'] = pd.to_numeric(df.get('min_price', 10), errors='coerce').fillna(10)
        df['max_price'] = pd.to_numeric(df.get('max_price', 1000), errors='coerce').fillna(1000)
        
        # Ensure typical price is valid
        df['typical_price'] = pd.to_numeric(
            df.get('typical_price', 0), errors='coerce'
        )
        # If typical price is missing or 0, fallback to average of min/max
        mask_bad_typical = (df['typical_price'] <= 0) | (df['typical_price'].isna())
        df.loc[mask_bad_typical, 'typical_price'] = (
            df.loc[mask_bad_typical, 'min_price'] + df.loc[mask_bad_typical, 'max_price']
        ) / 2

        # Exclude weight == 0
        df_active = df[df['weight'] > 0].copy()
        if df_active.empty:
            return pd.DataFrame()

        # --------------------------------------------------------
        # STEP 1: Aggressive Revenue Allocation (Pareto Power + Chaos)
        # --------------------------------------------------------
        # Power of 3: Weight 10 (1000) dominates Weight 5 (125).
        POWER_FACTOR = 3.0 
        
        # Chaos Factor: Multiplying by a random number (0.1 to 2.5) ensures that 
        # even if weights are identical (e.g. all 5), the amounts will vary wildly.
        # This prevents the "equal amounts" look in the report.
        chaos_factors = [random.uniform(0.1, 2.5) for _ in range(len(df_active))]
        
        df_active['effective_weight'] = (df_active['weight'] ** POWER_FACTOR) * chaos_factors
        total_weight = df_active['effective_weight'].sum()

        df_active['target_revenue'] = (
            df_active['effective_weight'] / total_weight
        ) * target_total_taxable

        # --------------------------------------------------------
        # STEP 2: Realistic Quantity Generation (Price Anchored)
        # --------------------------------------------------------
        results = []

        for _, row in df_active.iterrows():
            allocated_amt = row['target_revenue']
            
            # Skip negligible amounts
            if allocated_amt < 1:
                continue

            min_p = row['min_price']
            max_p = row['max_price']
            typical_p = row['typical_price']

            # 1. Start with ideal quantity based on Typical Price
            # This ensures we get ~1500 qty for 750k revenue at 500 price
            ideal_qty = allocated_amt / typical_p

            # 2. Add slight noise to quantity (not price) for organic feel
            # +/- 5% variation
            noise_factor = random.uniform(0.95, 1.05)
            target_qty = int(round(ideal_qty * noise_factor))
            target_qty = max(1, target_qty) # Ensure at least 1

            # 3. Calculate resulting unit price
            calculated_unit_price = allocated_amt / target_qty

            # 4. Enforce Price Bounds by adjusting Quantity
            # If price is too high (above max), we need MORE quantity to lower it
            if calculated_unit_price > max_p:
                target_qty = int(math.ceil(allocated_amt / max_p))
                calculated_unit_price = allocated_amt / target_qty # Recalculate
            
            # If price is too low (below min), we need LESS quantity to raise it
            elif calculated_unit_price < min_p:
                target_qty = int(math.floor(allocated_amt / min_p))
                target_qty = max(1, target_qty)
                calculated_unit_price = allocated_amt / target_qty # Recalculate

            # 5. Final Calculation
            # We fix quantity and allow price to float within bounds
            final_unit_price = round(calculated_unit_price, 2)
            
            # Ensure price is strictly within min/max after rounding
            final_unit_price = max(min_p, min(final_unit_price, max_p))
            
            final_taxable = round(target_qty * final_unit_price, 2)

            results.append({
                "hsn": row['hsn'],
                "description": row.get('description', ''),
                "qty": target_qty,
                "unit_price": final_unit_price,
                "final_taxable": final_taxable,
                "gst_rate": row.get('gst_rate', 0)
            })

        result_df = pd.DataFrame(results)
        if result_df.empty:
             return pd.DataFrame()

        # --------------------------------------------------------
        # STEP 3: Reconciliation (Fixing the Total)
        # --------------------------------------------------------
        current_total = result_df['final_taxable'].sum()
        diff = round(target_total_taxable - current_total, 2)

        # Distribute difference to the row with the HIGHEST REVENUE
        # This hides the adjustment in the largest number where it's least noticeable
        if abs(diff) >= 0.01:
            idx = result_df['final_taxable'].idxmax()
            
            old_taxable = result_df.at[idx, 'final_taxable']
            new_taxable = old_taxable + diff
            qty = result_df.at[idx, 'qty']
            
            # Update taxable
            result_df.at[idx, 'final_taxable'] = new_taxable
            
            # Adjust unit price to match new total
            new_unit_price = round(new_taxable / qty, 2)
            result_df.at[idx, 'unit_price'] = new_unit_price

        # --------------------------------------------------------
        # STEP 4: GST Calculation
        # --------------------------------------------------------
        result_df['gst_rate'] = pd.to_numeric(
            result_df['gst_rate'], errors='coerce'
        ).fillna(0)

        result_df['cgst_amt'] = (
            result_df['final_taxable'] * (result_df['gst_rate'] / 100) / 2
        ).round(2)

        result_df['sgst_amt'] = (
            result_df['final_taxable'] * (result_df['gst_rate'] / 100) / 2
        ).round(2)

        result_df['total_value'] = (
            result_df['final_taxable'] +
            result_df['cgst_amt'] +
            result_df['sgst_amt']
        ).round(2)

        return result_df[
            [
                'hsn',
                'description',
                'qty',
                'unit_price',
                'final_taxable',
                'gst_rate',
                'cgst_amt',
                'sgst_amt',
                'total_value'
            ]
        ]

    # ------------------------------------------------------------
    # B2B LOGIC (UNCHANGED)
    # ------------------------------------------------------------
    def process_b2b(self, b2b_entries):
        if not b2b_entries:
            return pd.DataFrame()

        df = pd.DataFrame(b2b_entries)

        df['qty'] = df['qty'].astype(int)
        df['taxable_value'] = df['taxable_value'].astype(float)
        df['gst_rate'] = df['gst_rate'].astype(float)

        if 'unit_price' not in df.columns:
            df['unit_price'] = (df['taxable_value'] / df['qty']).round(2)

        df['cgst_amt'] = (df['taxable_value'] * (df['gst_rate'] / 100) / 2).round(2)
        df['sgst_amt'] = (df['taxable_value'] * (df['gst_rate'] / 100) / 2).round(2)
        df['total_value'] = (
            df['taxable_value'] + df['cgst_amt'] + df['sgst_amt']
        ).round(2)

        df.rename(columns={'taxable_value': 'final_taxable'}, inplace=True)
        return df
