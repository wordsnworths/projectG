import json
import os
import pandas as pd

DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "hsn_master.json")
# This is the file you uploaded
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
                    # Read CSV. We use header=1 because your file has a date/rate in the first row.
                    df = pd.read_csv(CSV_SOURCE, header=1)
                    
                    # --- CRITICAL FIX: Normalize columns to lowercase ---
                    # This converts 'HSN' -> 'hsn' and 'DESCRIPTION' -> 'description'
                    df.columns = df.columns.str.strip().str.lower()
                    
                    # Handle missing 'gst_rate' column
                    if 'gst_rate' not in df.columns:
                        # If your file has metadata like "0.18" in the first row, we can default to 18
                        df['gst_rate'] = 18 
                    
                    # Ensure numeric types
                    df['gst_rate'] = pd.to_numeric(df['gst_rate'], errors='coerce').fillna(0)
                    
                    # Fill NaN descriptions
                    if 'description' in df.columns:
                        df['description'] = df['description'].fillna("")

                    # Save as JSON
                    self.save_data(df)
                    print("Successfully created master database from CSV.")
                    
                except Exception as e:
                    print(f"Error importing CSV: {e}")
                    # Create empty fallback
                    self.create_empty_file()
            else:
                print(f"CSV source {CSV_SOURCE} not found. Creating empty db.")
                self.create_empty_file()

    def create_empty_file(self):
        with open(DATA_FILE, 'w') as f:
            json.dump([], f)

    def load_data(self):
        """
        Loads data from JSON and ensures columns are correct.
        """
        try:
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                
            if not data:
                return pd.DataFrame(columns=['hsn', 'description', 'gst_rate'])

            df = pd.DataFrame(data)
            
            # --- SELF-HEALING: Standardize columns if loaded from bad JSON ---
            df.columns = df.columns.str.strip().str.lower()
            
            # Fix missing columns if they don't exist
            required_cols = ['hsn', 'description', 'gst_rate']
            for col in required_cols:
                if col not in df.columns:
                    if col == 'gst_rate':
                        df[col] = 18
                    else:
                        df[col] = ""
                        
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
