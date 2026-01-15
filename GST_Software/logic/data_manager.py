import json
import pandas as pd
from pathlib import Path

# ------------------------------------------------------------------
# PATHS (CLOUD + LOCAL SAFE)
# ------------------------------------------------------------------

# GST_Software/
BASE_DIR = Path(__file__).resolve().parent.parent

# GST_Software/data/
DATA_DIR = BASE_DIR / "data"
DATA_FILE = DATA_DIR / "hsn_master.json"

# Optional CSV fallback (only used if JSON is missing)
CSV_SOURCE = BASE_DIR / "hsn.csv"


class DataManager:
    def __init__(self):
        self.ensure_data_exists()
        self.hsn_data = self.load_data()

    # ------------------------------------------------------------------
    # DATA BOOTSTRAP
    # ------------------------------------------------------------------
    def ensure_data_exists(self):
        """Ensure data folder and master JSON exist."""
        DATA_DIR.mkdir(exist_ok=True)

        if not DATA_FILE.exists():
            if CSV_SOURCE.exists():
                try:
                    df = pd.read_csv(CSV_SOURCE)

                    df = self._normalize_columns(df)

                    if "gst_rate" not in df.columns:
                        df["gst_rate"] = 18

                    self.save_data(df)
                except Exception:
                    self._create_empty_master()
            else:
                self._create_empty_master()

    def _create_empty_master(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)

    # ------------------------------------------------------------------
    # LOAD / SAVE
    # ------------------------------------------------------------------
    def load_data(self):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            df = pd.DataFrame(data)

            if df.empty:
                return pd.DataFrame()

            df = self._normalize_columns(df)

            # Self-healing defaults
            if "gst_rate" not in df.columns:
                df["gst_rate"] = 18

            if "default_weight" not in df.columns:
                df["default_weight"] = 5

            return df

        except Exception as e:
            print("HSN load error:", e)
            return pd.DataFrame()

    def save_data(self, df):
        df = self._normalize_columns(df)

        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(df.to_dict(orient="records"), f, indent=4)

        self.hsn_data = df

    # ------------------------------------------------------------------
    # NORMALIZATION (THE KEY FIX)
    # ------------------------------------------------------------------
    def _normalize_columns(self, df):
        df.columns = (
            df.columns
            .str.strip()
            .str.lower()
            .str.replace(" ", "_")
        )

        # Common aliases fix
        rename_map = {
            "hsn_code": "hsn",
            "hsncode": "hsn",
            "description_": "description",
            "gst%": "gst_rate",
            "gst": "gst_rate",
        }

        df = df.rename(columns=rename_map)

        return df

    # ------------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------------
    def get_hsn_by_slab(self, rate):
        if self.hsn_data.empty:
            return pd.DataFrame()

        df = self.hsn_data.copy()
        df["gst_rate"] = pd.to_numeric(df["gst_rate"], errors="coerce").fillna(0)

        return df[df["gst_rate"] == rate]

    def get_all_hsn(self):
        return self.hsn_data.copy()
