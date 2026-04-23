import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

st.set_page_config(page_title="Advanced IT Calculator", page_icon="💰", layout="wide")

# ---------------- SIDEBAR CONFIGURATION ----------------
st.sidebar.header("⚙️ Configuration")

fy = st.sidebar.selectbox(
    "Select Financial Year:",
    ["FY 2025-26 (Latest)", "FY 2024-25"]
)

regime = st.sidebar.radio("Select Tax Regime:", ["New Regime", "Old Regime"])

income = st.sidebar.number_input("Annual Gross Salary (₹)", min_value=0, value=1500000, step=50000)

# Standard Deduction Logic
# FY 25-26: ₹75,000 | Old Regime: ₹50,000
std_deduction = 75000 if regime == "New Regime" else 50000
taxable_income = max(0, income - std_deduction)

# ---------------- SLAB LOGIC ----------------
def get_slabs(regime, fy):
    if regime == "New Regime":
        if fy == "FY 2025-26 (Latest)":
            # Budget 2025 Update: Slabs change every 4L
            return [(0, 400000, 0), (400000, 800000, 0.05), (800000, 1200000, 0.10), 
                    (1200000, 1600000, 0.15), (1600000, 2000000, 0.20), (2000000, 2400000, 0.25),
                    (2400000, float("inf"), 0.30)]
        else:
            # FY 2024-25 Slabs
            return [(0, 300000, 0), (300000, 700000, 0.05), (700000, 1000000, 0.10), 
                    (1000000, 1200000, 0.15), (1200000, 1500000, 0.20), (1500000, float("inf"), 0.30)]
    else:
        return [(0, 250000, 0), (250000, 500000, 0.05), (500000, 1000000, 0.20), (1000000, float("inf"), 0.30)]

def calculate_tax(income, slabs):
    tax = 0
    breakdown = []
    for lower, upper, rate in slabs:
        if income > lower:
            applicable_amount = min(income, upper) - lower
            slab_tax = applicable_amount * rate
            tax += slab_tax
            label = f"₹{lower//1000}k - {('∞' if upper==float('inf') else f'{int(upper//1000)}k')}"
            if slab_tax >= 0:
                breakdown.append({"Slab": label, "Rate": f"{int(rate*100)}%", "Tax Amount": slab_tax})
    return tax, breakdown

# --- Calculations ---
current_slabs = get_slabs(regime, fy)
tax_before_rebate, breakdown_data = calculate_tax(taxable_income, current_slabs)

# Rebate 87A Logic
rebate = 0
if regime == "New Regime":
    limit = 1200000 if fy == "FY 2025-26 (Latest)" else 700000
    if taxable_income <= limit:
        rebate = tax_before_rebate
elif regime == "Old Regime" and taxable_income <= 500000:
    rebate = min(tax_before_rebate, 12500)

tax_after_rebate = max(0, tax_before_rebate - rebate)
cess = tax_after_rebate * 0.04
total_tax = tax_after_rebate + cess
take_home = income - total_tax

# ---------------- UI DISPLAY ----------------
st.title(f"🇮🇳 Income Tax Calculator ({fy})")

m1, m2, m3 = st.columns(3)
m1.metric("Taxable Income", f"₹{taxable_income:,.0f}")
m2.metric("Total Tax Payable", f"₹{total_tax:,.0f}", delta=f"{(total_tax/income*100 if income > 0 else 0):.1f}% Effective Rate", delta_color="inverse")
m3.metric("Monthly Take-Home", f"₹{take_home/12:,.0f}")

st.markdown("---")

# ---------------- VISUALIZATION ----------------
left_col, right_col = st.columns([3, 2])

with left_col:
    st.subheader("📊 Tax Breakdown by Slab")
    plot_data = [d for d in breakdown_data if d['Tax Amount'] > 0]
    if plot_data:
        labels = [f"{d['Slab']} ({d['Rate']})" for d in plot_data]
        values = [d['Tax Amount'] for d in plot_data]

        fig, ax = plt.subplots(figsize=(10, 5))
        bars = ax.barh(labels, values, color='#2ecc71', edgecolor='#27ae60')
        
        # Add labels to the end of bars
        for bar in bars:
            width = bar.get_width()
            ax.text(width + (max(values)*0.02), bar.get_y() + bar.get_height()/2,
                    f'₹{width:,.0f}', va='center', fontweight='bold')

        ax.set_xlabel("Tax Amount (₹)")
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        st.pyplot(fig)
    else:
        st.success("✨ Your income is within the tax-free limit!")

with right_col:
    st.subheader("💰 Net Income Overview")
    fig2, ax2 = plt.subplots()
    ax2.pie([total_tax, take_home], labels=['Tax', 'Take-home'], 
            autopct='%1.1f%%', startangle=140, colors=['#e74c3c', '#1abc9c'], explode=(0.1, 0))
    st.pyplot(fig2)

# ---------------- LEAD GENERATION FORM ----------------
st.markdown("---")
st.subheader("📩 Professional Consultation")
st.info("💡 **Contact CA Dishika Agrawal for more details regarding your tax planning and compliance.**")

with st.form("consultation_form"):
    c1, c2 = st.columns(2)
    with c1:
        name = st.text_input("Full Name")
        contact = st.text_input("Phone Number / Email")
    with c2:
        consult_type = st.selectbox(
            "Type of Consultation:",
            [
                "Income Tax Return (ITR) Filing",
                "Tax Planning & Saving Advice",
                "Capital Gains Consultation",
                "Business Taxation & GST",
                "Notice Response & Litigation"
            ]
        )
        msg = st.text_area("Briefly describe your query (Optional)")
    
    submitted = st.form_submit_button("Book Consultation")
    
    if submitted:
        if name and contact:
            st.success(f"✅ Thank you {name}! Your request for '{consult_type}' has been sent to CA Dishika Agrawal.")
        else:
            st.error("⚠️ Please provide your name and contact details.")