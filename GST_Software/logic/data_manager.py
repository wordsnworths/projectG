import json
import os
import pandas as pd

DATA_FILE = "data/hsn_master.json"
DEFAULT_FILE = "data/hsn_defaults.json"

class DataManager:
    def __init__(self):
        self.ensure_data_exists()
        self.hsn_data = self.load_data()

    def ensure_data_exists(self):
        if not os.path.exists("data"):
            os.makedirs("data")
        
        if not os.path.exists(DATA_FILE):
            if os.path.exists(DEFAULT_FILE):
                with open(DEFAULT_FILE, 'r') as f:
                    defaults = json.load(f)
                with open(DATA_FILE, 'w') as f:
                    json.dump(defaults, f, indent=4)
            else:
                # Fallback if default file missing
                with open(DATA_FILE, 'w') as f:
                    json.dump([], f)

    def load_data(self):
        with open(DATA_FILE, 'r') as f:
            return pd.DataFrame(json.load(f))

    def save_data(self, df):
        # Convert dataframe back to list of dicts
        data = df.to_dict(orient='records')
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=4)
        self.hsn_data = df

    def get_hsn_by_slab(self, rate):
        return self.hsn_data[self.hsn_data['gst_rate'] == rate].copy()

    def get_all_hsn(self):
        return self.hsn_data