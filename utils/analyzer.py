import plotly.express as px

def summary_stats(df):
    total_debit = df['Withdrawal Amt.'].sum()
    total_credit = df['Deposit Amt.'].sum()
    latest_balance = df['Closing Balance'].dropna().iloc[-1]
    return total_debit, total_credit, latest_balance

def inflow_outflow_chart(df):
    df_plot = df[['Date', 'Withdrawal Amt.', 'Deposit Amt.']].fillna(0)
    df_plot = df_plot.melt(id_vars='Date', var_name='Type', value_name='Amount')
    fig = px.bar(df_plot, x='Date', y='Amount', color='Type', title='Inflow vs Outflow')
    return fig

