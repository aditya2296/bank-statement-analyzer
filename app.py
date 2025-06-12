import streamlit as st
from utils.analyzer import summary_stats, inflow_outflow_chart
from utils.parser import extract_transactions
from login import login

# Check login status
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    login()
    st.stop()
st.set_page_config("HDFC Statement Analyzer", layout="wide")
st.title("🏦 HDFC Account Statement Analyzer")

uploaded_file = st.file_uploader(
    label="",
    type="csv",
    label_visibility="collapsed",  # Hide default label
    accept_multiple_files=False
)

if uploaded_file:

    # Set default widget values if not present in session
    if "filter_type" not in st.session_state:
        st.session_state["filter_type"] = "All Transactions"

    if "narration" not in st.session_state:
        st.session_state["narration"] = ""

    if "start_date" not in st.session_state:
        st.session_state["start_date"] = None

    if "end_date" not in st.session_state:
        st.session_state["end_date"] = None

    if "min_dep" not in st.session_state:
        st.session_state["min_dep"] = 0.0

    if "min_wd" not in st.session_state:
        st.session_state["min_wd"] = 0.0

    with st.form("filters_form"):
        # Initialize session state for reset
        if "reset" not in st.session_state:
            st.session_state.reset = False
        # Transaction Type Radio Buttons
        filter_type = st.radio(
            label="Select Transaction Type",
            options=["All Transactions", "Only Deposits", "Only Withdrawals"],
            index=["All Transactions", "Only Deposits", "Only Withdrawals"].index(st.session_state["filter_type"]),
            horizontal=True,
            label_visibility="collapsed",
            key="filter_type"
        )

        # Narration search and date range
        with st.expander("🔎 Advanced Filters"):
            search_narration = st.text_input("🔍 Narration Contains", placeholder="e.g. ATM, NEFT, Salary", key="narration", value=st.session_state["narration"])

            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("📅 Start Date", value=st.session_state["start_date"], key="start_date")
            with col2:
                end_date = st.date_input("📅 End Date", value=st.session_state["end_date"], key="end_date")

            # Amount filters based on type
            col3, col4 = st.columns(2)
            with col3:
                if filter_type in ["Only Deposits", "All Transactions"]:
                    min_deposit_amount = st.number_input("⬆️ Minimum Deposit Amount (₹)", min_value=0.0, value=st.session_state["min_dep"], step=1000.0, key="min_dep")
                else:
                    min_deposit_amount = None

            with col4:
                if filter_type in ["Only Withdrawals", "All Transactions"]:
                    min_withdrawl_amount = st.number_input("⬇️ Minimum Withdrawal Amount (₹)", min_value=0.0, value=st.session_state["min_wd"], step=1000.0, key="min_wd")
                else:
                    min_withdrawl_amount = None

        # Set filter flags
        filter_deposits = filter_type == "Only Deposits"
        filter_withdrawls = filter_type == "Only Withdrawals"

        # Normalize values
        if filter_type == "All Transactions":
            min_deposit_amount = min_deposit_amount or None
            min_withdrawl_amount = min_withdrawl_amount or None
        # Buttons
        col_submit, col_reset = st.columns(2)
        with col_reset:
            reset_clicked = st.form_submit_button("🔄 Reset Filters")
        with col_submit:
            submitted = st.form_submit_button("✅ Apply Filters")

        if reset_clicked:
            for key in ["filter_type", "narration", "start_date", "end_date", "min_dep", "min_wd"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    try:
        df = extract_transactions(
            uploaded_file,
            filter_deposits_only=filter_deposits,
            filter_withdrawl_only=filter_withdrawls,
            min_deposit_amount=min_deposit_amount,
            min_withdrawl_amount=min_withdrawl_amount,
            search_narration=search_narration,
            start_date=start_date,
            end_date=end_date
        )

        with st.expander("📋Transaction Table"):
            st.dataframe(df[['S.No', 'Date', 'Narration', 'Withdrawal Amt.', 'Deposit Amt.', 'Closing Balance']], 
                use_container_width=True,
                hide_index=True)

        debit, credit, balance = summary_stats(df)
        c1, c2, c3 = st.columns(3)
        c1.metric("⬇️ Total Debits", f"{debit:,.2f}")
        c2.metric("⬆️ Total Credits", f"{credit:,.2f}")
        c3.metric("💼 Latest Balance", f"{balance:,.2f}")

        st.plotly_chart(inflow_outflow_chart(df), use_container_width=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 🔻 Top 10 Withdrawals")
            top_withdrawals = df[df['Withdrawal Amt.'].notna()].nlargest(10, 'Withdrawal Amt.')
            st.dataframe(top_withdrawals[['Date', 'Narration', 'Withdrawal Amt.']], use_container_width=True, hide_index=True)

        with col2:
            st.markdown("### 🔺 Top 10 Deposits")
            top_deposits = df[df['Deposit Amt.'].notna()].nlargest(10, 'Deposit Amt.')
            st.dataframe(top_deposits[['Date', 'Narration', 'Deposit Amt.']], use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
else:
    st.info("Please upload your bank statement in CSV format.")
