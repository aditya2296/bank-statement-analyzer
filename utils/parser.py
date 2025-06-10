import pandas as pd

EXPECTED_HEADER = ['Date', 'Narration', 'Chq./Ref.No.', 'Value Dt', 'Withdrawal Amt.', 'Deposit Amt.', 'Closing Balance']

def find_header_row(df):
    """Find the row number that contains the expected headers."""
    for i in range(len(df)):
        row = df.iloc[i].fillna("").astype(str).str.strip().tolist()
        if all(col in row for col in EXPECTED_HEADER):
            return i
    raise ValueError("Header row with expected columns not found.")

def extract_transactions(file, filter_deposits_only, filter_withdrawl_only, min_deposit_amount=None, min_withdrawl_amount=None, search_narration=None, start_date = None, end_date = None):
    raw = pd.read_csv(file, header=None)
    header_row = find_header_row(raw)
    header = raw.iloc[header_row].tolist()
    df = raw.iloc[header_row + 2:].copy()
    df.columns = header
    # Stop at row where all columns contain just asterisks
    stop_index = df[df.apply(lambda row: row.astype(str).str.fullmatch(r"\*+").all(), axis=1)].index
    if not stop_index.empty:
        df = df.loc[:stop_index[0] - 1]

    df.dropna(how='all', inplace=True)

    # Clean and convert columns
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce', dayfirst=True)
    df['Withdrawal Amt.'] = pd.to_numeric(df['Withdrawal Amt.'], errors='coerce')
    df['Deposit Amt.'] = pd.to_numeric(df['Deposit Amt.'], errors='coerce')
    df['Closing Balance'] = pd.to_numeric(df['Closing Balance'], errors='coerce')

    # Add Serial Number
    df.reset_index(drop=True, inplace=True)
    df.insert(0, 'S.No', df.index + 1)

    # Apply filter if requested
    if filter_deposits_only:
        df = df[df['Deposit Amt.'].notna() & (df['Deposit Amt.'] != 0)]

    # Apply withdrawl filter if requested
    if filter_withdrawl_only:
        df = df[df['Withdrawal Amt.'].notna() & (df['Withdrawal Amt.'] != 0)]

    if min_deposit_amount is not None:
        df = df[df['Deposit Amt.'] >= min_deposit_amount]

    if min_withdrawl_amount is not None:
        df = df[df['Withdrawal Amt.'] >= min_withdrawl_amount]
    
    if search_narration:
        df = df[df['Narration'].str.contains(search_narration, case=False, na=False)]
    
    if start_date:
        df = df[df['Date'] >= pd.to_datetime(start_date)]
    if end_date:
        df = df[df['Date'] <= pd.to_datetime(end_date)]

    return df