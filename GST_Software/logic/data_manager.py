import json
import os
import pandas as pd

DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "hsn_master.json")
# We will look for this CSV if the JSON doesn't exist or is broken
CSV_SOURCE = "hsn.csv"

class DataManager:
    def __init__(self):
        self.ensure_data_exists()
        self.hsn_data = self.load_data()

    def ensure_data_exists(self):
        """
        Ensures the data directory and master JSON file exist.
        If JSON is missing, it tries to create it from 'hsn.csv'.
        """
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
        
        # If master JSON doesn't exist, try to create it from CSV
        if not os.path.exists(DATA_FILE):
            if os.path.exists(CSV_SOURCE):
                print(f"Found {CSV_SOURCE}. Converting to master JSON...")
                try:
                    # Read CSV, skipping the first row (metadata) to find headers on row 2
                    # If your CSV is standard, remove 'header=1'. Based on your file, keep 'header=1'.
                    df = pd.read_csv(CSV_SOURCE, header=1)
                    
                    # Clean column names
                    df.columns = [c.strip() for c in df.columns]
                    
                    # Add missing gst_rate if it doesn't exist
                    if 'gst_rate' not in df.columns:
                        df['gst_rate'] = 18 # Defaulting to 18% based on your file metadata
                    
                    # Save as JSON
                    self.save_data(df)
                except Exception as e:
                    print(f"Error importing CSV: {e}")
                    # Create empty fallback if CSV fails
                    with open(DATA_FILE, 'w') as f:
                        json.dump([], f)
            else:
                # Create empty fallback if no CSV found
                with open(DATA_FILE, 'w') as f:
                    json.dump([], f)

    def load_data(self):
        """
        Loads data from JSON and performs self-healing if columns are missing.
        """
        try:
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                df = pd.DataFrame(data)
                
                # SELF-HEALING: Fix missing 'gst_rate' column error
                if not df.empty and 'gst_rate' not in df.columns:
                    print("Fixing missing 'gst_rate' column...")
                    df['gst_rate'] = 18
                    self.save_data(df) # Save the fix
                    
                return df
        except Exception as e:
            print(f"Error loading data: {e}")
            return pd.DataFrame()

    def save_data(self, df):
        """
        Saves the DataFrame to the master JSON file.
        """
        data = df.to_dict(orient='records')
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=4)
        self.hsn_data = df

    def get_hsn_by_slab(self, rate):
        """
        Returns HSN codes filtered by GST rate.
        """
        if self.hsn_data.empty:
            return pd.DataFrame()
        
        # Ensure gst_rate is numeric for comparison
        self.hsn_data['gst_rate'] = pd.to_numeric(self.hsn_data['gst_rate'], errors='coerce').fillna(0)
        
        return self.hsn_data[self.hsn_data['gst_rate'] == rate].copy()

    def get_all_hsn(self):
        """
        Returns all HSN data.
        """
        return self.hsn_data.copy()
