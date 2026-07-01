import streamlit as st

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
    st.title("General Land Valuation Model")
    st.caption("Based on the HKIS Residual Method of Valuation")
    st.divider()

    # --- Inputs Layout ---
    # We use columns to organize the inputs neatly
    col_revenue, col_costs, col_finance = st.columns(3)

    with col_revenue:
        st.subheader("Scale & Revenue")
        gfa = st.number_input("Total GFA (sq ft)", min_value=100_000, max_value=10_000_000, value=5_000_000,
                              step=100_000)
        efficiency_pct = st.slider("Efficiency (%)", min_value=50, max_value=100, value=80, step=1)
        asp = st.slider("ASP ($/sf SFA)", min_value=1000, max_value=50000, value=2600, step=100)

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

    st.divider()

    # --- Interim Calculations ---
    # 1. Areas and Revenue
    sfa = gfa * (efficiency_pct / 100)
    gdv = sfa * asp

    # 2. Hard & Soft Costs
    const_cost = unit_const_cost * gfa
    prof_fee = const_cost * (prof_fee_pct / 100)
    sm_fee = gdv * (sm_fee_pct / 100)
    dev_profit = gdv * (dev_profit_pct / 100)

    # 3. Finance (Converting percentages to decimals)
    interest_rate = interest_rate_pct / 100

    # --- Main Calculation (Algebraic Solution) ---
    # Calculate interest specifically on construction (drawn down over time, hence 50%)
    const_interest = const_cost * 0.5 * interest_rate * loan_period

    # Sum all fixed costs
    fixed_costs = const_cost + prof_fee + sm_fee + dev_profit + const_interest

    # Solve for Residual Value (Land Value)
    residual_value = (gdv - fixed_costs) / (1 + (interest_rate * loan_period))

    # Calculate the land interest now that we know the Residual Value
    land_interest = residual_value * 1.0 * interest_rate * loan_period
    total_interest = const_interest + land_interest

    # --- formatting for UI display (Convert to Billions) ---
    gdv_b = gdv / 1_000_000_000
    residual_value_b = residual_value / 1_000_000_000
    total_costs_b = (fixed_costs + land_interest) / 1_000_000_000

    # --- Outputs ---
    st.subheader("Valuation Results")
    res_col1, res_col2, res_col3 = st.columns(3)

    with res_col1:
        st.metric(label="Gross Development Value (GDV)", value=f"HKD {gdv_b:.2f}B")
    with res_col2:
        st.metric(label="Total Development Costs", value=f"HKD {total_costs_b:.2f}B")
    with res_col3:
        st.metric(label="Residual Land Value", value=f"HKD {residual_value_b:.2f}B")


if __name__ == "__main__":
    main()