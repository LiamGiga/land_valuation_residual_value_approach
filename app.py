import streamlit as st
import pandas as pd

# ---------- Configuration ----------
st.set_page_config(page_title="Residual Land Valuation", layout="wide")


# --- Custom Helper Function for Synced Slider & Input Box ---
def sync_slider_input(label, min_val, max_val, default_val, step, key, is_float=False):
    # 1. Initialize states (Number for Slider, Formatted String for Text Box)
    if key not in st.session_state:
        st.session_state[key] = default_val
    if f"{key}_txt" not in st.session_state:
        if is_float:
            st.session_state[f"{key}_txt"] = f"{default_val:,.2f}"
        else:
            st.session_state[f"{key}_txt"] = f"{default_val:,}"  # Formats with commas

    # 2. Callback: Slider to Text Box (Injects commas)
    def update_from_slider():
        val = st.session_state[key]
        if is_float:
            st.session_state[f"{key}_txt"] = f"{val:,.2f}"
        else:
            st.session_state[f"{key}_txt"] = f"{int(val):,}"

    # 3. Callback: Text Box to Slider (Strips commas for math)
    def update_from_txt():
        raw_str = st.session_state[f"{key}_txt"]

        # Remove commas so python can read it as a number
        clean_str = raw_str.replace(",", "").replace(" ", "")

        try:
            val = float(clean_str) if is_float else int(clean_str)
            val = max(min_val, min(val, max_val))  # Enforce min/max limits
            st.session_state[key] = val

            # Reformat the text box so it instantly looks pretty again
            if is_float:
                st.session_state[f"{key}_txt"] = f"{val:,.2f}"
            else:
                st.session_state[f"{key}_txt"] = f"{int(val):,}"
        except ValueError:
            # If they typed letters by accident, revert it to the slider's last safe number
            val = st.session_state[key]
            if is_float:
                st.session_state[f"{key}_txt"] = f"{val:,.2f}"
            else:
                st.session_state[f"{key}_txt"] = f"{int(val):,}"

        st.markdown(f"<span style='font-size: 14px; font-weight: 600;'>{label}</span>", unsafe_allow_html=True)
        col_slide, col_box = st.columns([3, 1])

        with col_slide:
            st.slider(
                label, min_value=min_val, max_value=max_val, step=step,
                key=key, on_change=update_from_slider, label_visibility="collapsed"
            )
        with col_box:
            # TEXT INPUT: Allows the user to type freely, while our logic formats it
            st.text_input(
                label, key=f"{key}_txt", on_change=update_from_txt, label_visibility="collapsed"
            )

        return st.session_state[key]

def main():
    # --- Custom CSS for layout spacing ---
    st.markdown("""
        <style>
        .stMetric { text-align: center; }
        hr { margin-top: 10px !important; margin-bottom: 20px !important; }
        </style>
    """, unsafe_allow_html=True)

    # --- Header ---
    st.title("Land Valuation Model Residual Value Approach")
    st.caption("Based on the HKIS Residual Method of Valuation")

    results_container = st.container()
    st.divider()

    # --- Inputs Layout (Using our new synced UI function) ---
    col_revenue, col_costs, col_finance = st.columns(3)

    with col_revenue:
        st.subheader("Scale & Revenue")
        gfa = sync_slider_input("Total GFA (sq ft)", 0, 1_000_000, 500_000, 100_000, "gfa")
        efficiency_pct = sync_slider_input("Efficiency (%)", 0, 100, 90, 1, "efficiency")
        asp = sync_slider_input("Average Selling Price ($/sf SFA)", 0, 100_000, 20000, 100, "asp")

    with col_costs:
        st.subheader("Development Costs")
        unit_const_cost = sync_slider_input("Construction Cost ($/sf GFA)", 0, 20_000, 5000, 100, "const_cost")
        prof_fee_pct = sync_slider_input("Professional Fees (%)", 0, 15, 4, 1, "prof_fee")
        sm_fee_pct = sync_slider_input("Sales & Marketing (%)", 0, 15, 6, 1, "sm_fee")
        dev_profit_pct = sync_slider_input("Developer Profit (%)", 0, 100, 20, 1, "dev_profit")

    with col_finance:
        st.subheader("Financing")
        interest_rate_pct = sync_slider_input("Interest Rate (%)", 0.0, 15.0, 5.0, 0.1, "interest", is_float=True)
        loan_period = sync_slider_input("Loan Period (Years)", 0.0, 10.0, 5.0, 0.5, "loan_period", is_float=True)

    # --- Interim Calculations ---
    # 1. Areas and Revenue
    sfa = gfa * (efficiency_pct / 100)
    gdv = sfa * asp

    # 2. Hard & Soft Costs
    const_cost = unit_const_cost * gfa
    prof_fee = const_cost * (prof_fee_pct / 100)
    sm_fee = gdv * (sm_fee_pct / 100)
    dev_profit = gdv * (dev_profit_pct / 100)

    # 3. Finance
    interest_rate = interest_rate_pct / 100

    # --- Main Calculation (Algebraic Solution) ---
    const_interest = const_cost * 0.5 * interest_rate * loan_period
    fixed_costs = const_cost + prof_fee + sm_fee + dev_profit + const_interest

    residual_value = (gdv - fixed_costs) / (1 + (interest_rate * loan_period))
    land_interest = residual_value * 1.0 * interest_rate * loan_period

    total_costs = fixed_costs + land_interest

    # 4. Key Performance Indicators
    accommodation_value = residual_value / gfa if gfa > 0 else 0

    # --- CSV Export Setup ---
    export_data = {
        "Total GFA (sq ft)": [gfa],
        "Efficiency (%)": [efficiency_pct],
        "Average Selling Price ($/sf SFA)": [asp],
        "Construction Cost ($/sf GFA)": [unit_const_cost],
        "Professional Fees (%)": [prof_fee_pct],
        "Sales & Marketing (%)": [sm_fee_pct],
        "Developer Profit (%)": [dev_profit_pct],
        "Interest Rate (%)": [interest_rate_pct],
        "Loan Period (Years)": [loan_period],
        "Gross Development Value (HKD)": [gdv],
        "Total Development Costs (HKD)": [total_costs],
        "Residual Land Value (HKD)": [residual_value],
        "Accommodation Value ($/sf GFA)": [accommodation_value]
    }

    df_export = pd.DataFrame(export_data)
    csv_file = df_export.to_csv(index=False).encode('utf-8')

    # --- Fill the Top Container with our Results & Download Button ---
    with results_container:
        header_col, btn_col = st.columns([4, 1])
        with header_col:
            st.subheader("Valuation Results")
        with btn_col:
            st.write("")  # Spacing to align button
            st.download_button(
                label="📥 Download CSV",
                data=csv_file,
                file_name="residual_valuation_model.csv",
                mime="text/csv",
                use_container_width=True
            )

        # Back to 3 columns so the numbers don't truncate
        res_col1, res_col2, res_col3 = st.columns(3)

        with res_col1:
            st.metric(label="Gross Development Value", value=f"HKD {gdv:,.0f}")
        with res_col2:
            st.metric(label="Total Development Costs", value=f"HKD {total_costs:,.0f}")
        with res_col3:
            # Stack the values vertically
            st.metric(label="Residual Land Value", value=f"HKD {residual_value:,.0f}")
            st.write("")  # small gap
            st.metric(label="Accommodation Value", value=f"HKD {accommodation_value:,.0f}/sf")


if __name__ == "__main__":
    main()