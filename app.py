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
        interest_rate_pct = st.slider("Interest Rate (%)", min_value=