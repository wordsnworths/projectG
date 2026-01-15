import json
import os
import pandas as pd

DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "hsn_master.json")
DEFAULT_FILE = os.path.join(DATA_DIR, "hsn_defaults.json")
# We keep this just as a fallback, but we will prioritize JSON
CSV_SOURCE = "hsn.csv"

class DataManager:
    def __init__(self):
        self.ensure_data_exists()
        self.hsn_data = self.load_data()

    def ensure_data_exists(self):
        """
        Ensures the data directory and master JSON file exist.
        """
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
        
        # If master JSON doesn't exist, try to populate it
        if not os.path.exists(DATA_FILE):
            # 1. Try Default JSON first
            if os.path.exists(DEFAULT_FILE):
                try:
                    with open(DEFAULT_FILE, 'r') as f:
                        defaults = json.load(f)
                    with open(DATA_FILE, 'w') as f:
                        json.dump(defaults, f, indent=4)
                    print(f"Initialized data from {DEFAULT_FILE}")
                    return
                except Exception as e:
                    print(f"Error loading defaults: {e}")

            # 2. Try CSV second (as recovery)
            if os.path.exists(CSV_SOURCE):
                try:
                    df = pd.read_csv(CSV_SOURCE, header=1) # Assuming header on row 2
                    # Normalize columns immediately
                    df.columns = df.columns.str.strip().str.lower()
                    if 'gst_rate' not in df.columns: df['gst_rate'] = 18
                    
                    data = df.to_dict(orient='records')
                    with open(DATA_FILE, 'w') as f:
                        json.dump(data, f, indent=4)
                    print(f"Initialized data from {CSV_SOURCE}")
                except:
                    pass
            
            # 3. If all else fails, create empty file
            if not os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'w') as f:
                    json.dump([], f)

    def load_data(self):
        """
        Loads data from JSON and normalizes keys to ensure app compatibility.
        """
        try:
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
            
            if not data:
                return pd.DataFrame(columns=['hsn', 'description', 'gst_rate'])

            df = pd.DataFrame(data)
            
            # --- CRITICAL FIX: Normalize columns to lowercase ---
            # This fixes the mismatch if JSON has "HSN" but app wants "hsn"
            df.columns = df.columns.str.strip().str.lower()
            
            # Ensure required columns exist
            if 'gst_rate' not in df.columns:
                df['gst_rate'] = 18
            
            # Convert NaN to empty strings for text fields
            if 'description' in df.columns:
                df['description'] = df['description'].fillna("")

            return df
        except Exception as e:
            print(f"Error loading data: {e}")
            return pd.DataFrame(columns=['hsn', 'description', 'gst_rate'])

    def save_data(self, df):
        """
        Saves the DataFrame to the master JSON file.
        """
        # Ensure we always save with lowercase keys
        df.columns = df.columns.str.strip().str.lower()
        
        data = df.to_dict(orient='records')
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=4)
        self.hsn_data = df

    def get_hsn_by_slab(self, rate):
        """
        Returns HSN codes filtered by GST rate.
        """
        if self.hsn_data.empty:
            return pd.DataFrame(columns=['hsn', 'description', 'gst_rate'])
        
        # Ensure types are correct for comparison
        self.hsn_data['gst_rate'] = pd.to_numeric(self.hsn_data['gst_rate'], errors='coerce').fillna(0)
        
        return self.hsn_data[self.hsn_data['gst_rate'] == rate].copy()

    def get_all_hsn(self):
        """
        Returns all HSN data.
        """
        if self.hsn_data.empty:
             return pd.DataFrame(columns=['hsn', 'description', 'gst_rate'])
        return self.hsn_data.copy()
