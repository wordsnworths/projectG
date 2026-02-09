import json
import os
import pandas as pd

DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "hsn_master.json")
DEFAULT_FILE = os.path.join(DATA_DIR, "hsn_defaults.json")
CSV_SOURCE = "hsn.csv"


class DataManager:
    def __init__(self):
        self.ensure_data_exists()
        self.hsn_data = self.load_data()

    # ------------------------------------------------------------
    # Ensure data exists (bootstrap logic)
    # ------------------------------------------------------------
    def ensure_data_exists(self):
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)

        if os.path.exists(DATA_FILE):
            return

        # 1️⃣ Try defaults JSON
        if os.path.exists(DEFAULT_FILE):
            try:
                with open(DEFAULT_FILE, "r") as f:
                    defaults = json.load(f)
                with open(DATA_FILE, "w") as f:
                    json.dump(defaults, f, indent=4)
                return
            except Exception:
                pass

        # 2️⃣ Try CSV import
        if os.path.exists(CSV_SOURCE):
            try:
                meta_df = pd.read_csv(CSV_SOURCE, header=None, nrows=1)
                try:
                    rate_val = float(meta_df.iloc[0, 0])
                    detected_rate = rate_val * 100 if rate_val < 1 else rate_val
                except Exception:
                    detected_rate = 18

                df = pd.read_csv(CSV_SOURCE, header=1)
                df.columns = df.columns.str.strip().str.lower()

                if 'gst_rate' not in df.columns:
                    df['gst_rate'] = detected_rate

                # Realistic defaults
                if 'weight' not in df.columns:
                    df['weight'] = 5
                if 'min_price' not in df.columns:
                    df['min_price'] = 50.0
                if 'max_price' not in df.columns:
                    df['max_price'] = 500.0
                if 'typical_price' not in df.columns:
                    df['typical_price'] = (df['min_price'] + df['max_price']) / 2

                with open(DATA_FILE, "w") as f:
                    json.dump(df.to_dict(orient="records"), f, indent=4)
                return
            except Exception as e:
                print("CSV bootstrap failed:", e)

        # 3️⃣ Fallback empty
        with open(DATA_FILE, "w") as f:
            json.dump([], f)

    # ------------------------------------------------------------
    # Load & normalize data
    # ------------------------------------------------------------
    def load_data(self):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)

            if not data:
                return self._empty_df()

            df = pd.DataFrame(data)
            df.columns = df.columns.str.strip().str.lower()

            # Mandatory columns
            if 'hsn' not in df.columns:
                df['hsn'] = ""
            if 'description' not in df.columns:
                df['description'] = ""
            if 'gst_rate' not in df.columns:
                df['gst_rate'] = 18

            # Realism columns
            if 'weight' not in df.columns:
                df['weight'] = 5
            if 'min_price' not in df.columns:
                df['min_price'] = 50.0
            if 'max_price' not in df.columns:
                df['max_price'] = 500.0
            if 'typical_price' not in df.columns:
                df['typical_price'] = (df['min_price'] + df['max_price']) / 2

            # Clean numeric fields
            for col in ['weight', 'min_price', 'max_price', 'typical_price', 'gst_rate']:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            # Fill NaNs sensibly
            df['weight'] = df['weight'].fillna(5)
            df['min_price'] = df['min_price'].fillna(50.0)
            df['max_price'] = df['max_price'].fillna(df['min_price'] * 5)
            df['typical_price'] = df['typical_price'].fillna(
                (df['min_price'] + df['max_price']) / 2
            )

            # Safety clamps
            df['min_price'] = df['min_price'].clip(lower=1)
            df['max_price'] = df[['max_price', 'min_price']].max(axis=1)
            df['typical_price'] = df[['typical_price', 'min_price']].max(axis=1)
            df['typical_price'] = df[['typical_price', 'max_price']].min(axis=1)

            return df

        except Exception as e:
            print("Error loading data:", e)
            return self._empty_df()

    # ------------------------------------------------------------
    # Save data
    # ------------------------------------------------------------
    def save_data(self, df):
        df = df.copy()
        df.columns = df.columns.str.strip().str.lower()

        with open(DATA_FILE, "w") as f:
            json.dump(df.to_dict(orient="records"), f, indent=4)

        self.hsn_data = df

    # ------------------------------------------------------------
    # Access helpers
    # ------------------------------------------------------------
    def get_hsn_by_slab(self, rate):
        if self.hsn_data.empty:
            return pd.DataFrame()

        df = self.hsn_data.copy()
        df['gst_rate'] = pd.to_numeric(df['gst_rate'], errors='coerce').fillna(0)
        return df[df['gst_rate'] == rate]

    def get_all_hsn(self):
        return self.hsn_data.copy()

    # ------------------------------------------------------------
    # Internal helper
    # ------------------------------------------------------------
    def _empty_df(self):
        return pd.DataFrame(columns=[
            'hsn',
            'description',
            'gst_rate',
            'weight',
            'min_price',
            'typical_price',
            'max_price'
        ])
