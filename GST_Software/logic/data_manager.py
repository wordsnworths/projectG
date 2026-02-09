import json
import os
import pandas as pd

DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "hsn_master.json")

# -----------------------------------------------------------------------------
# EMBEDDED DEFAULTS (Your full data, embedded so files aren't required)
# -----------------------------------------------------------------------------
DEFAULT_HSN_DATA = [
  { "hsn": "9608", "description": "Ball point pens, felt tipped pens, markers, fountain pens, stylograph pens", "gst_rate": 18, "weight": 8, "min_price": 10, "max_price": 80 },
  { "hsn": "3213", "description": "Artists' and painters' colours", "gst_rate": 18, "weight": 5, "min_price": 100, "max_price": 500 },
  { "hsn": "3506", "description": "Prepared glues and adhesives", "gst_rate": 18, "weight": 3, "min_price": 20, "max_price": 150 },
  { "hsn": "9017", "description": "Steel scale, Scale", "gst_rate": 18, "weight": 3, "min_price": 15, "max_price": 60 },
  { "hsn": "3824", "description": "Correction pen", "gst_rate": 18, "weight": 3, "min_price": 25, "max_price": 55 },
  { "hsn": "9603", "description": "Paint brushes and other brushes", "gst_rate": 18, "weight": 5, "min_price": 30, "max_price": 250 },
  { "hsn": "3926", "description": "Articles of plastics (folders, files, photo frames, glitter foam)", "gst_rate": 18, "weight": 3, "min_price": 40, "max_price": 200 },
  { "hsn": "3407", "description": "Clay", "gst_rate": 18, "weight": 3, "min_price": 50, "max_price": 150 },
  { "hsn": "9503", "description": "Toys", "gst_rate": 18, "weight": 5, "min_price": 150, "max_price": 1200 },
  { "hsn": "4202", "description": "Bag, wallet, gift set", "gst_rate": 18, "weight": 5, "min_price": 400, "max_price": 1500 },
  { "hsn": "8470", "description": "Calculator", "gst_rate": 18, "weight": 3, "min_price": 200, "max_price": 800 },
  { "hsn": "3919", "description": "Scotch tape, foam tape, Post-it notes, stickers", "gst_rate": 18, "weight": 3, "min_price": 20, "max_price": 120 },
  { "hsn": "7317", "description": "Drawing pins, corrugated nails, staples", "gst_rate": 18, "weight": 1, "min_price": 10, "max_price": 50 },
  { "hsn": "8305", "description": "Binder clip, stapler pin", "gst_rate": 18, "weight": 3, "min_price": 10, "max_price": 80 },
  { "hsn": "7013", "description": "Crystal mud, mugs", "gst_rate": 18, "weight": 3, "min_price": 100, "max_price": 300 },
  { "hsn": "8214", "description": "Pencil kit, sapphire file", "gst_rate": 18, "weight": 3, "min_price": 50, "max_price": 200 },
  { "hsn": "8506", "description": "Batteries", "gst_rate": 18, "weight": 5, "min_price": 15, "max_price": 60 },
  { "hsn": "3304", "description": "Nail polish, eye liner", "gst_rate": 18, "weight": 3, "min_price": 50, "max_price": 250 },
  { "hsn": "8472", "description": "Punching machine", "gst_rate": 18, "weight": 3, "min_price": 80, "max_price": 250 },
  { "hsn": "4822", "description": "Paper straw", "gst_rate": 18, "weight": 2, "min_price": 50, "max_price": 200 },
  { "hsn": "3307", "description": "Room freshener, agarbatti", "gst_rate": 18, "weight": 3, "min_price": 50, "max_price": 300 },
  { "hsn": "9505", "description": "Colouring book, toys", "gst_rate": 18, "weight": 5, "min_price": 100, "max_price": 500 },
  { "hsn": "4909", "description": "Greetings card", "gst_rate": 18, "weight": 3, "min_price": 20, "max_price": 100 },
  { "hsn": "3208", "description": "Painting material, varnish", "gst_rate": 18, "weight": 5, "min_price": 100, "max_price": 500 },
  { "hsn": "8523", "description": "Pendrives", "gst_rate": 18, "weight": 5, "min_price": 300, "max_price": 900 },
  { "hsn": "8213", "description": "Scissors, stapler", "gst_rate": 18, "weight": 3, "min_price": 50, "max_price": 300 },
  { "hsn": "3805", "description": "Turpentine", "gst_rate": 18, "weight": 5, "min_price": 100, "max_price": 400 },
  { "hsn": "9105", "description": "Clocks", "gst_rate": 18, "weight": 3, "min_price": 200, "max_price": 800 },
  { "hsn": "8301", "description": "Locks", "gst_rate": 18, "weight": 3, "min_price": 50, "max_price": 250 },
  { "hsn": "4816", "description": "Carbon", "gst_rate": 18, "weight": 2, "min_price": 50, "max_price": 200 },
  { "hsn": "9506", "description": "Sport goods", "gst_rate": 18, "weight": 5, "min_price": 100, "max_price": 1000 },
  { "hsn": "3214", "description": "Clay", "gst_rate": 18, "weight": 3, "min_price": 50, "max_price": 150 },
  { "hsn": "9610", "description": "Drawing board", "gst_rate": 18, "weight": 3, "min_price": 200, "max_price": 600 },
  { "hsn": "8465", "description": "Glue gun", "gst_rate": 18, "weight": 3, "min_price": 200, "max_price": 500 },
  { "hsn": "9617", "description": "Thermos flask", "gst_rate": 18, "weight": 3, "min_price": 300, "max_price": 900 },
  { "hsn": "4411", "description": "Writing board", "gst_rate": 18, "weight": 3, "min_price": 100, "max_price": 400 },
  { "hsn": "7319", "description": "Craft/needle items", "gst_rate": 18, "weight": 2, "min_price": 20, "max_price": 100 },
  { "hsn": "8211", "description": "Craft knife", "gst_rate": 18, "weight": 3, "min_price": 50, "max_price": 150 },
  { "hsn": "8205", "description": "Clay tool", "gst_rate": 18, "weight": 3, "min_price": 50, "max_price": 350 },
  { "hsn": "4817", "description": "Envelope", "gst_rate": 18, "weight": 2, "min_price": 10, "max_price": 50 },
  { "hsn": "8203", "description": "Tweezers", "gst_rate": 18, "weight": 1, "min_price": 50, "max_price": 150 },
  { "hsn": "3924", "description": "Plastic lunch box", "gst_rate": 18, "weight": 3, "min_price": 100, "max_price": 400 },
  { "hsn": "3923", "description": "Water bottle", "gst_rate": 18, "weight": 3, "min_price": 100, "max_price": 400 },
  { "hsn": "9612", "description": "Ink-pads", "gst_rate": 18, "weight": 2, "min_price": 20, "max_price": 80 },
  { "hsn": "3215", "description": "Ink, ink-bottle, stamp pad ink", "gst_rate": 18, "weight": 2, "min_price": 20, "max_price": 100 },
  { "hsn": "8516", "description": "Rechargeable battery/hair dryer", "gst_rate": 18, "weight": 3, "min_price": 500, "max_price": 1500 },
  { "hsn": "8513", "description": "Rechargeable torch", "gst_rate": 18, "weight": 3, "min_price": 200, "max_price": 500 },
  { "hsn": "8510", "description": "Trimmer", "gst_rate": 18, "weight": 3, "min_price": 400, "max_price": 1200 },
  { "hsn": "8308", "description": "ID holder", "gst_rate": 18, "weight": 2, "min_price": 10, "max_price": 50 },
  { "hsn": "2106", "description": "Chocolate syrup", "gst_rate": 18, "weight": 3, "min_price": 100, "max_price": 300 },
  { "hsn": "8518", "description": "Headphones, earphones", "gst_rate": 18, "weight": 5, "min_price": 300, "max_price": 1000 },
  { "hsn": "9504", "description": "Board games", "gst_rate": 18, "weight": 5, "min_price": 200, "max_price": 800 },
  { "hsn": "4802", "description": "Paper", "gst_rate": 18, "weight": 3, "min_price": 100, "max_price": 300 },
  { "hsn": "4804", "description": "Brown sheet paper", "gst_rate": 18, "weight": 2, "min_price": 10, "max_price": 50 },
  { "hsn": "4820", "description": "Diary, Notebook", "gst_rate": 18, "weight": 5, "min_price": 100, "max_price": 400 },
  { "hsn": "5901", "description": "Canvas boards", "gst_rate": 18, "weight": 3, "min_price": 50, "max_price": 200 },
  { "hsn": "6913", "description": "Incense sticks", "gst_rate": 18, "weight": 2, "min_price": 50, "max_price": 200 },
  { "hsn": "3406", "description": "Fragrance preparations", "gst_rate": 18, "weight": 3, "min_price": 100, "max_price": 400 },
  { "hsn": "9615", "description": "Combs and fashion jewellery", "gst_rate": 18, "weight": 2, "min_price": 50, "max_price": 300 },
  { "hsn": "1704", "description": "Chewing gum (and sugar confectionery)", "gst_rate": 18, "weight": 2, "min_price": 20, "max_price": 100 },
  { "hsn": "4906", "description": "Sketch books", "gst_rate": 18, "weight": 5, "min_price": 40, "max_price": 120 },
  { "hsn": "5601", "description": "Cotton balls", "gst_rate": 18, "weight": 2, "min_price": 20, "max_price": 100 },
  { "hsn": "7117", "description": "Imitation jewellery", "gst_rate": 3, "weight": 5, "min_price": 150, "max_price": 900 },
  { "hsn": "4602", "description": "Palm leaves", "gst_rate": 5, "weight": 3, "min_price": 15, "max_price": 25 },
  { "hsn": "1905", "description": "Wafer biscuits/chocolate", "gst_rate": 5, "weight": 5, "min_price": 35, "max_price": 150 },
  { "hsn": "4823", "description": "Paper, paperboard", "gst_rate": 5, "weight": 5, "min_price": 50, "max_price": 300 },
  { "hsn": "9503", "description": "Toys", "gst_rate": 5, "weight": 8, "min_price": 50, "max_price": 300 },
  { "hsn": "4818", "description": "Toilet paper, handkerchiefs, cleansing or facial tissues, napkins", "gst_rate": 5, "weight": 3, "min_price": 30, "max_price": 200 },
  { "hsn": "1806", "description": "Chocolate", "gst_rate": 5, "weight": 3, "min_price": 50, "max_price": 500 },
  { "hsn": "4906", "description": "Sketch books", "gst_rate": 5, "weight": 5, "min_price": 40, "max_price": 120 },
  { "hsn": "7323", "description": "Water bottles (Iron or steel wool and utensils)", "gst_rate": 5, "weight": 5, "min_price": 200, "max_price": 800 },
  { "hsn": "4016", "description": "Rubber bands", "gst_rate": 5, "weight": 2, "min_price": 10, "max_price": 50 },
  { "hsn": "4911", "description": "Printed picture", "gst_rate": 5, "weight": 2, "min_price": 50, "max_price": 200 },
  { "hsn": "4901", "description": "Printed books, drawing or colouring books", "gst_rate": 0, "weight": 10, "min_price": 100, "max_price": 1200 },
  { "hsn": "4820", "description": "Notebooks", "gst_rate": 0, "weight": 5, "min_price": 50, "max_price": 250 },
  { "hsn": "0604", "description": "Potpourri (fragrance preparations)", "gst_rate": 0, "weight": 2, "min_price": 50, "max_price": 200 },
  { "hsn": "9609", "description": "Pencils, crayons, pencil leads, pastels, drawing chalk", "gst_rate": 0, "weight": 8, "min_price": 5, "max_price": 150 },
  { "hsn": "4016", "description": "Eraser", "gst_rate": 0, "weight": 3, "min_price": 3, "max_price": 30 },
  { "hsn": "8214", "description": "Sharpener", "gst_rate": 0, "weight": 2, "min_price": 5, "max_price": 30 },
  { "hsn": "4903", "description": "Children's picture, drawing or colouring books", "gst_rate": 0, "weight": 8, "min_price": 30, "max_price": 250 }
]

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

        # Always check if we need to write embedded defaults (e.g. if file missing or empty)
        should_write = False
        if not os.path.exists(DATA_FILE):
            should_write = True
        else:
            try:
                with open(DATA_FILE, 'r') as f:
                    content = f.read().strip()
                    if not content or content == "[]":
                        should_write = True
            except:
                should_write = True

        if should_write:
            print("Writing embedded defaults to master file...")
            with open(DATA_FILE, "w") as f:
                json.dump(DEFAULT_HSN_DATA, f, indent=4)

    # ------------------------------------------------------------
    # Load & normalize data
    # ------------------------------------------------------------
    def load_data(self):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)

            if not data:
                # Fallback to embedded if file read results in empty
                data = DEFAULT_HSN_DATA

            df = pd.DataFrame(data)
            # Normalize column names: strip spaces, lowercase, replace spaces with underscores
            df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

            # --- COLUMN MAPPING FIX ---
            # Map 'default_weight' to 'weight' if weight is missing
            if 'default_weight' in df.columns and 'weight' not in df.columns:
                df['weight'] = df['default_weight']
            
            # Mandatory columns
            if 'hsn' not in df.columns: df['hsn'] = ""
            if 'description' not in df.columns: df['description'] = ""
            if 'gst_rate' not in df.columns: df['gst_rate'] = 18

            # Realism columns
            if 'weight' not in df.columns: df['weight'] = 5
            
            # Numeric cleanup
            cols_to_numeric = ['min_price', 'max_price', 'gst_rate', 'weight']
            for col in cols_to_numeric:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            if 'min_price' not in df.columns: df['min_price'] = 50.0
            else: df['min_price'] = df['min_price'].fillna(50.0)

            if 'max_price' not in df.columns: df['max_price'] = 500.0
            else: df['max_price'] = df['max_price'].fillna(500.0)

            # --- KEY FIX: Calculate typical_price if missing ---
            if 'typical_price' not in df.columns:
                df['typical_price'] = (df['min_price'] + df['max_price']) / 2
            
            # Ensure it is numeric and filled
            df['typical_price'] = pd.to_numeric(df['typical_price'], errors='coerce')
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
            # Critical fallback: return dataframe from embedded defaults
            return pd.DataFrame(DEFAULT_HSN_DATA)

    # ------------------------------------------------------------
    # Save data
    # ------------------------------------------------------------
    def save_data(self, df):
        df = df.copy()
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

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
        
        # Robust conversion to handle float 18.0 vs int 18
        df['gst_rate'] = pd.to_numeric(df['gst_rate'], errors='coerce').fillna(0)
        
        # Filter with tolerance for float comparison or exact match
        return df[df['gst_rate'].astype(int) == int(rate)]

    def get_all_hsn(self):
        return self.hsn_data.copy()

    # ------------------------------------------------------------
    # Internal helper
    # ------------------------------------------------------------
    def _empty_df(self):
        # Return dataframe based on embedded defaults to prevent empty UI
        return pd.DataFrame(DEFAULT_HSN_DATA)
