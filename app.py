import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Golden Cross Strategy", layout="wide")
st.title("📈 Golden Cross Strategy Backtester")

uploaded_file = st.file_uploader("Upload your stock CSV file", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df['DATE'] = pd.to_datetime(df['DATE'])

    # Show available stocks
    stock_list = df.columns[1:]
    selected_stock = st.selectbox("Select a stock", stock_list)

    stock_df = df[['DATE', selected_stock]].dropna().copy()
    stock_df = stock_df.sort_values('DATE')
    stock_df.rename(columns={selected_stock: "Close"}, inplace=True)

    # Calculate moving averages
    stock_df['MA50'] = stock_df['Close'].rolling(window=50).mean()
    stock_df['MA200'] = stock_df['Close'].rolling(window=200).mean()

    # Generate buy/sell signals
    stock_df['Signal'] = 0
    stock_df['Signal'][stock_df['MA50'] > stock_df['MA200']] = 1
    stock_df['Position'] = stock_df['Signal'].diff()

    buy_signals = stock_df[stock_df['Position'] == 1]
    sell_signals = stock_df[stock_df['Position'] == -1]

    # Simulate trades with holding period
    trades = []
    for buy_date in buy_signals.index:
        next_sell = sell_signals[sell_signals.index > buy_date]
        if not next_sell.empty:
            sell_date = next_sell.index[0]

            buy_price = stock_df.loc[buy_date, 'Close']
            sell_price = stock_df.loc[sell_date, 'Close']

            buy_dt = stock_df.loc[buy_date, 'DATE']
            sell_dt = stock_df.loc[sell_date, 'DATE']
            holding_days = (sell_dt - buy_dt).days

            price_change = sell_price - buy_price
            return_pct = (price_change / buy_price) * 100

            trades.append({
                "Buy Date": buy_dt.date(),
                "Exit Date": sell_dt.date(),
                "Buy Price": round(buy_price, 2),
                "Exit Price": round(sell_price, 2),
                "Holding Period (days)": holding_days,
                "Price Change": round(price_change, 2),
                "Return (%)": round(return_pct, 2)
            })

    # Display trade results
    st.subheader("📋 Trade Summary")
    results_df = pd.DataFrame(trades)
    st.dataframe(results_df)

    # Plot price + moving averages
    st.subheader("📉 Price Chart with Moving Averages")
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(stock_df['DATE'], stock_df['Close'], label="Close Price", color='black')
    ax.plot(stock_df['DATE'], stock_df['MA50'], label="50-day MA", color='blue')
    ax.plot(stock_df['DATE'], stock_df['MA200'], label="200-day MA", color='red')
    ax.legend()
    st.pyplot(fig)
