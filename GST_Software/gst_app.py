import streamlit as st
import pandas as pd
from datetime import datetime

# Logic imports
from logic.data_manager import DataManager
from logic.distribution_engine import DistributionEngine
from logic.excel_writer import ExcelReportGenerator

# ------------------------------------------------------------------
# Config & Setup
# ------------------------------------------------------------------
st.set_page_config(
    page_title="GST Report Architect",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------------------------------------------
# CSS / Theme
# ------------------------------------------------------------------
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        font-family: 'Segoe UI', sans-serif;
    }
    .stButton > button {
        background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(75,108,183,0.4);
    }
    [data-testid="stSidebar"] {
        background-color: #13151c;
        border-right: 1px solid #2d303e;
    }
    .metric-card {
        background-color: #1e2130;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #2d303e;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# Session State
# ------------------------------------------------------------------
if "b2b_entries" not in st.session_state:
    st.session_state.b2b_entries = []

# ------------------------------------------------------------------
# Modules
# ------------------------------------------------------------------
# Initialize modules
data_mgr = DataManager()
engine = DistributionEngine()
excel_gen = ExcelReportGenerator()

# ------------------------------------------------------------------
# Sidebar
# ------------------------------------------------------------------
with st.sidebar:
    st.title("GST Architect 🚀")
    st.markdown("---")
    nav = st.radio("Navigation", ["Report Generator", "B2B Entry", "HSN Settings"], index=0)
    
    st.markdown("---")
    st.info("💡 **Tip:** Use 'Weight' to control how much of the total value goes to a specific item. Higher weight (8-10) means significantly more value.")
    st.caption("v1.2.0 | Enhanced Distribution")

# ==================================================================
# PAGE: REPORT GENERATOR
# ==================================================================
if nav == "Report Generator":

    st.header("📄 Generate GST Report")

    # Date Inputs
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        month = st.selectbox("Month", range(1, 13), index=datetime.now().month - 1)
    with col2:
        year = st.number_input("Year", min_value=2024, max_value=2030, value=datetime.now().year)

    st.markdown("### Slab Inputs")
    st.markdown("Enter the **Total Taxable Value** for each GST slab below. The system will distribute this amount based on your HSN weights.")

    slabs = ['18', '5', '3', '0']
    slab_inputs = {}
    slab_weights = {}

    for slab in slabs:
        # Determine if expanded by default
        is_expanded = slab in ['18', '5']
        
        with st.expander(f"{slab}% GST Slab", expanded=is_expanded):
            c1, c2 = st.columns([1, 2])

            with c1:
                slab_inputs[slab] = st.number_input(
                    f"Total Taxable Value (₹) - {slab}%",
                    min_value=0.0,
                    step=1000.0,
                    format="%.2f",
                    key=f"val_{slab}"
                )
                if slab_inputs[slab] > 0:
                    st.success(f"Allocating: ₹{slab_inputs[slab]:,.2f}")

            with c2:
                hsn_df = data_mgr.get_hsn_by_slab(int(slab))
                if hsn_df.empty:
                    st.warning("No HSN codes found for this slab.")
                    continue

                st.caption(f"HSN Configuration for {slab}%")
                
                # Enhanced Data Editor
                edited = st.data_editor(
                    hsn_df[['hsn', 'description', 'weight', 'min_price', 'typical_price', 'max_price']],
                    hide_index=True,
                    use_container_width=True,
                    key=f"editor_{slab}",
                    column_config={
                        "hsn": st.column_config.TextColumn("HSN", disabled=True),
                        "description": st.column_config.TextColumn("Description", disabled=True),
                        "weight": st.column_config.SelectboxColumn(
                            "Weight (0-10)",
                            options=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                            help="10 = Highest priority (Gets most value). 0 = Exclude entirely.",
                            required=True
                        ),
                        "min_price": st.column_config.NumberColumn("Min ₹", width="small"),
                        "typical_price": st.column_config.NumberColumn("Avg Unit Price ₹", width="medium", help="The target price per unit. Logic tries to stick close to this."),
                        "max_price": st.column_config.NumberColumn("Max ₹", width="small"),
                    }
                )

                edited["gst_rate"] = int(slab)
                slab_weights[slab] = edited.to_dict("records")

    st.markdown("---")

    if st.button("Generate Intelligent Report", type="primary", use_container_width=True):
        with st.spinner("Balancing quantities, prices & totals..."):
            processed_data = {}
            has_data = False

            # 1. Process Slabs
            for slab, taxable in slab_inputs.items():
                if taxable > 0:
                    rows = slab_weights.get(slab, [])
                    if rows:
                        df_result = engine.distribute_slab(
                            target_total_taxable=taxable,
                            hsn_list=rows,
                            seed=f"{year}-{month}-{slab}" # Deterministic seed
                        )
                        processed_data[slab] = df_result
                        has_data = True
                    else:
                        st.error(f"{slab}% slab has taxable value but no HSN configured.")

            # 2. Process B2B
            b2b_df = pd.DataFrame()
            if st.session_state.b2b_entries:
                b2b_df = engine.process_b2b(st.session_state.b2b_entries)
                has_data = True

            if not has_data:
                st.info("Please enter taxable values or add B2B entries.")
                st.stop()

            # 3. Generate Excel
            excel_file = excel_gen.generate_report(processed_data, b2b_df, month, year)

            st.success("Report generated successfully!")

            # 4. Preview & Download
            tabs = st.tabs(["Preview Data", "Download"])

            with tabs[0]:
                for rate, df in processed_data.items():
                    if not df.empty:
                        st.subheader(f"{rate}% Slab Preview")
                        st.dataframe(
                            df[['hsn', 'description', 'qty', 'unit_price', 'final_taxable', 'total_value']],
                            use_container_width=True,
                            column_config={
                                "unit_price": st.column_config.NumberColumn("Unit Price", format="₹%.2f"),
                                "final_taxable": st.column_config.NumberColumn("Taxable", format="₹%.2f"),
                                "total_value": st.column_config.NumberColumn("Total", format="₹%.2f"),
                            }
                        )

            with tabs[1]:
                filename = f"GST_Report_{year}_{month}_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
                st.download_button(
                    "📥 Download Excel File",
                    data=excel_file,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

# ==================================================================
# PAGE: B2B ENTRY
# ==================================================================
elif nav == "B2B Entry":

    st.header("🏢 B2B Transactions")
    st.markdown("Add specific Business-to-Business invoices here.")

    col1, col2 = st.columns(2)
    hsn_master = data_mgr.get_all_hsn()

    with col1:
        hsn_options = hsn_master['hsn'].astype(str) + " - " + hsn_master['description']
        hsn_select = st.selectbox("Select HSN", hsn_options)

        selected_hsn = hsn_select.split(" - ")[0]
        selected_desc = " - ".join(hsn_select.split(" - ")[1:])

        gstin = st.text_input("GSTIN (Optional)")
        qty = st.number_input("Quantity", min_value=1, value=1)

    with col2:
        taxable = st.number_input("Taxable Value", min_value=0.0, step=100.0)

        try:
            default_rate = int(hsn_master[hsn_master['hsn'] == selected_hsn]['gst_rate'].iloc[0])
        except:
            default_rate = 18

        gst_rate = st.selectbox("GST Rate (%)", [18, 5, 3, 0], index=[18,5,3,0].index(default_rate))

    if st.button("Add Entry", type="primary"):
        st.session_state.b2b_entries.append({
            "gstin": gstin.upper(),
            "hsn": selected_hsn,
            "description": selected_desc,
            "qty": qty,
            "taxable_value": taxable,
            "gst_rate": gst_rate
        })
        st.success("B2B entry added")

    st.subheader("Current Session B2B Entries")
    if st.session_state.b2b_entries:
        df = pd.DataFrame(st.session_state.b2b_entries)
        st.dataframe(df, use_container_width=True)
        if st.button("Clear All"):
            st.session_state.b2b_entries = []
            st.rerun()
    else:
        st.caption("No entries yet")

# ==================================================================
# PAGE: HSN SETTINGS
# ==================================================================
elif nav == "HSN Settings":

    st.header("⚙️ HSN Master Settings")
    st.markdown("Changes here are persistent. Adjust default prices and weights.")

    current_df = data_mgr.get_all_hsn()

    edited_df = st.data_editor(
        current_df,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "weight": st.column_config.SelectboxColumn("Weight", options=list(range(0, 11))),
            "typical_price": st.column_config.NumberColumn("Avg Unit Price ₹"),
        }
    )

    if st.button("Save Changes"):
        data_mgr.save_data(edited_df)
        st.success("Settings saved successfully")
