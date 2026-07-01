import streamlit as st

# ---------- Configuration ----------
st.set_page_config(page_title="Residual Land Valuation", layout="centered")


def main():
    # --- Custom CSS for layout spacing ---
    st.markdown("""
        <style>
        .stMetric { text-align: center; }
        hr { margin-top: 10px !important; margin-bottom: 20px !important; }
        </style>
    """, unsafe_allow_html=True)

    # --- Header ---
    st.title("Land Valuation Model")
    st.caption("Residual Value Valuation Method")

    # --- Top Metrics Row ---
    col1, col2 = st.columns(2)
    with col1:
        gross_rev_metric = st.empty()
    with col2:
        dev_net_metric = st.empty()

    st.write("")

    col3, col4, col5 = st.columns([1, 2, 1])
    with col4:
        mtrc_take_metric = st.empty()

    st.divider()

    # --- Inputs (Sliders) ---
    st.subheader("Assumptions")

    # Static area assumptions for the model
    total_gfa = 5_000_000
    total_sfa = 4_000_000  # Assuming 80% efficiency

    # Updated label to $/sf SFA
    sfa_price = st.slider("$/sf SFA", min_value=0, max_value=5000, value=2600, step=100)
    construction_cost = st.slider("Construction Cost (HKD M)", min_value=0, max_value=10000, value=5000, step=100)
    land_premium = st.slider("Land Premium (HKD M)", min_value=0, max_value=15000, value=8000, step=100)
    upfront_lump_sum = st.slider("Upfront Lump Sum (HKD M)", min_value=0, max_value=5000, value=2000, step=100)
    mtrc_profit_share_pct = st.slider("MTRC Profit Share (%)", min_value=0, max_value=100, value=25, step=1)

    # --- Calculations ---
    # Calculate GDV using Saleable Floor Area
    gross_revenue_b = (sfa_price * total_sfa) / 1_000_000_000

    total_costs_b = (construction_cost + land_premium + upfront_lump_sum) / 1000
    gross_profit_b = gross_revenue_b - total_costs_b

    mtrc_profit_share_b = (gross_profit_b * (mtrc_profit_share_pct / 100)) if gross_profit_b > 0 else 0

    developer_net_b = gross_profit_b - mtrc_profit_share_b
    mtrc_total_take_b = (upfront_lump_sum / 1000) + mtrc_profit_share_b

    # --- Update Metrics ---
    gross_rev_metric.metric(label="Gross Revenue", value=f"HKD {gross_revenue_b:.2f}B")
    dev_net_metric.metric(label="Developer Net", value=f"HKD {developer_net_b:.2f}B")
    mtrc_take_metric.metric(label="MTRC Total Take", value=f"HKD {mtrc_total_take_b:.2f}B")


if __name__ == "__main__":
    main()