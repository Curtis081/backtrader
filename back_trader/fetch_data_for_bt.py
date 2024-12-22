import yfinance as yf
import pandas as pd
import backtrader as bt


def fetch_data_from_yahoo(ticker, start_date, end_date):
    # Fetch data from Yahoo Finance
    df = yf.download(ticker, start=start_date, end=end_date)

    # Check if the DataFrame is empty
    if df.empty:
        raise ValueError(f"No data found for ticker {ticker} between {start_date} and {end_date}")

    # Flatten multi-level columns by dropping the 'Ticker' level
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)  # Remove the second level (Ticker)

    # Reset the index and rename 'Date' to 'datetime'
    df.reset_index(inplace=True)
    df.rename(columns={'Date': 'datetime'}, inplace=True)
    df['datetime'] = pd.to_datetime(df['datetime'])  # Ensure datetime format is correct

    # Set 'datetime' as the index
    df.set_index('datetime', inplace=True)

    return df


def convert_to_backtrader_data_format(df):
    # Convert to Backtrader data format
    data = bt.feeds.PandasData(
        dataname=df,
        datetime=None,  # Backtrader will automatically pick the index as datetime
        open='Open',
        high='High',
        low='Low',
        close='Close',
        volume='Volume',
        openinterest=None  # No open interest
    )

    return data


def get_data_from_yahoo(ticker, start_date, end_date):
    df = fetch_data_from_yahoo(ticker, start_date, end_date)
    data = convert_to_backtrader_data_format(df)

    return data
