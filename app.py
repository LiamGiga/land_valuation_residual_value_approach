import streamlit as st
import pandas as pd

# ---------- Configuration ----------
st.set_page_config(page_title="Residual Land Valuation", layout="wide")


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

    # Reserve a spot at the top for our results
    results_container = st.container()
    st.divider()

    # --- Inputs Layout ---
    st.info("💡 **Pro-Tip:** Click on the red number above any slider to type an exact value!")

    col_revenue, col_costs, col_finance = st.columns(3)

    with col_revenue:
        st.subheader("Scale & Revenue")
        gfa = st.slider("Total GFA (sq ft)", min_value=100_000, max_value=10_000_000, value=5_000_000, step=100_000)
        efficiency_pct = st.slider("Efficiency (%)", min_value=50, max_value=100, value=80, step=1)
        asp = st.slider("Average Selling Price ($/sf SFA)", min_value=1000, max_value=50000, value=2600, step=100)

    with col_costs:
        st.subheader("Development Costs")
        unit_const_cost = st.slider("Construction Cost ($/sf GFA)", min_value=1000, max_value=20000, value=5000,
                                    step=100)
        prof_fee_pct = st.slider("Professional Fees (%)", min_value=1, max_value=15, value=6, step=1)
        sm_fee_pct = st.slider("Sales & Marketing (%)", min_value=1, max_value=15, value=6, step=1)
        dev_profit_pct = st.slider("Developer Profit (%)", min_value=5, max_value=40, value=20, step=1)

    with col_finance:
        st.subheader("Financing")
        interest_rate_pct = st.slider("Interest Rate (%)", min_value=1.0, max_value=15.0, value=4.0, step=0.1)
        loan_period = st.slider("Loan Period (Years)", min_value=1.0, max_value=10.0, value=3.0, step=0.5)

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
        "Residual Land Value (HKD)": [residual_value]
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

        # Metrics formatted with full commas (e.g., 13,000,000,000)
        res_col1