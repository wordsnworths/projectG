import streamlit as st
import pandas as pd
from datetime import datetime
import time

from logic.data_manager import DataManager
from logic.distribution_engine import DistributionEngine
from logic.excel_writer import ExcelReportGenerator

# --- Config & Setup ---
st.set_page_config(
    page_title="GST Report Architect",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS / Theme ---
st.markdown("""
<style>
    /* Global Clean Look */
    .stApp {
        background-color: #0e1117;
        font-family: 'Segoe UI', sans-serif;
    }
    
    /* Custom Cards */
    div.css-1r6slb0 {
        background-color: #1e212b;
        border: 1px solid #2d303e;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Input Fields */
    .stTextInput > div > div > input, .stNumberInput > div > div > input {
        background-color: #1e212b;
        color: #e0e0e0;
        border-radius: 8px;
        border: 1px solid #383b47;
    }
    
    /* Buttons */
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
        box-shadow: 0 5px 15px rgba(75, 108, 183, 0.4);
    }
    
    /* Tables */
    .dataframe {
        font-size: 0.9rem !important;
        border-radius: 8px;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #13151c;
        border-right: 1px solid #2d303e;
    }
</style>
""", unsafe_allow_html=True)

# --- State Init ---
if 'b2b_entries' not in st.session_state:
    st.session_state.b2b_entries = []

# --- Modules ---
data_mgr = DataManager()
engine = DistributionEngine()
excel_gen = ExcelReportGenerator()

# --- Sidebar ---
with st.sidebar:
    st.title("GST Architect 🚀")
    st.markdown("---")
    
    nav = st.radio("Navigation", ["Report Generator", "B2B Entry", "HSN Settings"], index=0)
    
    st.markdown("---")
    st.caption("v1.0.4 | Internal Use Only")

# --- Page: Report Generator ---
if nav == "Report Generator":
    st.header("📄 Generate GST Report")
    
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        month = st.selectbox("Month", range(1, 13), index=datetime.now().month - 1)
    with col2:
        year = st.number_input("Year", min_value=2024, max_value=2030, value=datetime.now().year)
    
    st.markdown("### Slab Inputs")
    
    # Slab Containers
    slabs = ['18', '5', '3', '0']
    slab_inputs = {}
    slab_weights = {} # Store modified weights per session
    
    for slab in slabs:
        with st.expander(f"{slab}% GST Slab", expanded=(slab in ['18', '5'])):
            c1, c2 = st.columns([1, 2])
            with c1:
                slab_inputs[slab] = st.number_input(
                    f"Total Taxable Value (₹) - {slab}%", 
                    min_value=0.0, 
                    step=1000.0, 
                    key=f"val_{slab}",
                    format="%.2f"
                )
            
            with c2:
                # Get HSNs for this slab
                hsn_df = data_mgr.get_hsn_by_slab(int(slab))
                if not hsn_df.empty:
                    st.caption("HSN Distribution Weights")
                    
                    # Edit Weights UI
                    edited_weights = st.data_editor(
                        hsn_df[['hsn', 'description', 'default_weight', 'min_price', 'max_price']],
                        column_config={
                            "default_weight": st.column_config.SelectboxColumn(
                                "Weight",
                                help="Relative importance (0 to exclude)",
                                options=[0, 1, 3, 5, 8, 10], # Added 0 option
                                required=True
                            ),
                            "min_price": st.column_config.NumberColumn("Min ₹"),
                            "max_price": st.column_config.NumberColumn("Max ₹"),
                        },
                        hide_index=True,
                        key=f"editor_{slab}",
                        use_container_width=True
                    )
                    # Use 'default_weight' column as 'weight' for logic
                    edited_weights = edited_weights.rename(columns={'default_weight': 'weight'})

                    # --- INJECT GST RATE BACK INTO DATA ---
                    edited_weights['gst_rate'] = int(slab)
                    
                    slab_weights[slab] = edited_weights.to_dict('records')
                else:
                    st.warning("No HSN codes found for this slab. Go to Settings.")
    
    st.markdown("---")
    
    if st.button("Generate Intelligent Report", type="primary", use_container_width=True):
        with st.spinner("Crunching numbers & balancing decimals..."):
            
            processed_data = {}
            has_data = False
            
            # Process Slabs
            for slab, taxable in slab_inputs.items():
                if taxable > 0:
                    hsn_list = slab_weights.get(slab, [])
                    if hsn_list:
                        df_result = engine.distribute_slab(taxable, hsn_list)
                        processed_data[slab] = df_result
                        has_data = True
                    else:
                        st.error(f"Taxable value entered for {slab}%, but no HSNs configured!")
            
            # Process B2B
            b2b_df = pd.DataFrame()
            if st.session_state.b2b_entries:
                b2b_df = engine.process_b2b(st.session_state.b2b_entries)
                has_data = True
            
            if has_data:
                # Generate Excel
                excel_file = excel_gen.generate_report(processed_data, b2b_df, month, year)
                
                # Previews
                st.success("Report Generated Successfully!")
                
                tabs = st.tabs(["Preview Data", "Download"])
                
                with tabs[0]:
                    for rate, df in processed_data.items():
                        st.subheader(f"{rate}% Slab Breakdown")
                        # Show all rows including 0s so user can verify
                        st.dataframe(df[['hsn', 'description', 'qty', 'final_taxable', 'total_value']], use_container_width=True)
                
                with tabs[1]:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
                    filename = f"GST_Report_{year}_{month}_{timestamp}.xlsx"
                    
                    st.download_button(
                        label="📥 Download Excel File",
                        data=excel_file,
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            else:
                st.info("Please enter taxable values or add B2B entries to generate a report.")

# --- Page: B2B Entry ---
elif nav == "B2B Entry":
    st.header("🏢 B2B Transactions")
    
    col1, col2 = st.columns(2)
    hsn_master = data_mgr.get_all_hsn()
    
    with col1:
        # HSN Dropdown
        hsn_options = hsn_master['hsn'].astype(str) + " - " + hsn_master['description']
        hsn_select = st.selectbox("Select HSN", hsn_options)
        
        # Parse selected HSN to trigger updates
        selected_hsn_code = hsn_select.split(" - ")[0]
        selected_hsn_desc = " - ".join(hsn_select.split(" - ")[1:])
        
        # GSTIN Input
        gstin = st.text_input("GSTIN", placeholder="Enter GST Number (Optional)")
        
        qty = st.number_input("Quantity", min_value=1, value=1)
            
    with col2:
        taxable = st.number_input("Taxable Value (Total for Line)", min_value=0.0, step=100.0)
        
        # Auto-detect GST Rate based on HSN selection
        try:
            default_rate_val = int(hsn_master[hsn_master['hsn'] == selected_hsn_code]['gst_rate'].iloc[0])
        except:
            default_rate_val = 18 # Fallback
            
        # Map rate to index in options
        rate_options = [18, 5, 3, 0]
        try:
            default_idx = rate_options.index(default_rate_val)
        except ValueError:
            default_idx = 0
            
        gst_rate = st.selectbox("GST Rate (%)", rate_options, index=default_idx)
    
    # Submit Button
    if st.button("Add Entry", type="primary"):
        entry = {
            "gstin": gstin.upper() if gstin else "",
            "hsn": selected_hsn_code,
            "description": selected_hsn_desc,
            "qty": qty,
            "taxable_value": taxable,
            "gst_rate": gst_rate
        }
        st.session_state.b2b_entries.append(entry)
        st.success("Added!")

    st.subheader("Current Session B2B Entries")
    if st.session_state.b2b_entries:
        b2b_df = pd.DataFrame(st.session_state.b2b_entries)
        
        display_cols = ['gstin', 'hsn', 'description', 'qty', 'taxable_value', 'gst_rate']
        final_cols = [c for c in display_cols if c in b2b_df.columns]
        
        st.dataframe(b2b_df[final_cols], use_container_width=True)
        if st.button("Clear All"):
            st.session_state.b2b_entries = []
            st.rerun()
    else:
        st.caption("No entries yet.")

# --- Page: Settings ---
elif nav == "HSN Settings":
    st.header("⚙️ HSN Master Settings")
    st.markdown("Modify the default database. Changes here persist.")
    
    current_df = data_mgr.get_all_hsn()
    
    edited_df = st.data_editor(
        current_df,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "gst_rate": st.column_config.NumberColumn("GST %"),
            "default_weight": st.column_config.SelectboxColumn("Default Weight", options=[0, 1, 3, 5, 8, 10]), # Added 0 option
        }
    )
    
    if st.button("Save Changes"):
        data_mgr.save_data(edited_df)
        st.success("Settings saved successfully!")