import streamlit as st
from utils.analyzer import summary_stats, inflow_outflow_chart
from utils.parser import extract_transactions

st.set_page_config("HDFC Bank Analyzer", layout="wide")
st.title("🏦 HDFC Bank Statement Analyzer")

uploaded_file = st.file_uploader("Upload your HDFC Bank CSV Statement", type="csv")

if uploaded_file:
    filter_type = st.radio(
        "Filter Type",
        options=["All Transactions", "Only Deposits", "Only Withdrawals"],
        index=0,
        horizontal=True
    )

    search_narration = st.text_input("🔍 Search Narration (optional)", placeholder="e.g. ATM, NEFT, Salary")

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("📅 Start Date", value=None)
    with col2:
        end_date = st.date_input("📅 End Date", value=None)

    # Set flags based on radio choice
    filter_deposits = filter_type == "Only Deposits"
    filter_withdrawls = filter_type == "Only Withdrawals"
    if filter_deposits or filter_type == "All Transactions":
        min_deposit_amount = st.number_input("Minimum Deposit Amount (₹)", min_value=0.0, value=0.0, step=1000.0) # ✅ New: User can enter a minimum deposit amount
    else:
        min_deposit_amount = None
    if filter_withdrawls or filter_type == "All Transactions":
        min_withdrawl_amount = st.number_input("Minimum Withdrawl Amount (₹)", min_value=0.0, value=0.0, step=1000.0) # ✅ New: User can enter a minimum withdrawl amount
    else:
        min_withdrawl_amount = None
    if filter_type == "All Transactions":
        if min_deposit_amount == 0.0:
            min_deposit_amount = None
        if min_withdrawl_amount == 0.0:
            min_withdrawl_amount = None
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

        st.subheader("📌 Summary")
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
