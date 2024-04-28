import yfinance as yf
import matplotlib.pyplot as plt
import streamlit as st

# Define available stock analysis functions
def get_stock_price(ticker):
    """
    Retrieves the latest closing price for a given stock ticker from Yahoo Finance.
    """
    try:
        data = yf.download(tickers=ticker, period='1d')['Close'].iloc[-1]
        return f"The latest closing price for {ticker} is ${data:.2f}"
    except:
        return "Sorry, couldn't find data for that ticker."

def calculate_SMA(ticker, window):
    """
    Calculates the Simple Moving Average (SMA) for a stock price over a specified window.
    """
    try:
        data = yf.download(tickers=ticker, period=f"{window}d")['Close']
        return f"The {window}-day SMA for {ticker} is ${data.mean():.2f}"
    except:
        return "Sorry, couldn't find data for that ticker or invalid window."

def calculate_EMA(ticker, window):
    """
    Calculates the Exponential Moving Average (EMA) for a stock price over a specified window.
    """
    try:
        data = yf.download(tickers=ticker, period=f"{window}d")['Close']
        ema = data.ewm(span=window, adjust=False).mean().iloc[-1]
        return f"The {window}-day EMA for {ticker} is ${ema:.2f}"
    except:
        return "Sorry, couldn't find data for that ticker or invalid window."

def calculate_RSI(ticker):
    """
    Calculates the Relative Strength Index (RSI) for a stock using its price history.
    """
    try:
        data = yf.download(tickers=ticker, period='1y')['Close']
        delta = data.diff()
        up = delta.clip(lower=0)
        down = -1 * delta.clip(upper=0)
        ema_up = up.ewm(com=14 - 1, adjust=False).mean()
        ema_down = down.ewm(com=14 - 1, adjust=False).mean()
        rs = ema_up / ema_down
        rsi = 100 - (100 / (1 + rs)).iloc[-1]
        return f"The RSI for {ticker} is {rsi:.2f}"
    except:
        return "Sorry, couldn't find data for that ticker."

def calculate_MACD(ticker):
    """
    Calculates the Moving Average Convergence Divergence (MACD) for a stock using its price history.
    """
    try:
        data = yf.download(tickers=ticker, period='1y')['Close']
        short_EMA = data.ewm(span=12, adjust=False).mean()
        long_EMA = data.ewm(span=26, adjust=False).mean()
        MACD = short_EMA - long_EMA
        signal = MACD.ewm(span=9, adjust=False).mean()
        MACD_histogram = MACD - signal
        return f"The MACD for {ticker} is: MACD = {MACD.iloc[-1]:.2f}, Signal Line = {signal.iloc[-1]:.2f}, Histogram = {MACD_histogram.iloc[-1]:.2f}"
    except:
        return "Sorry, couldn't find data for that ticker."

def plot_stock_price(ticker):
    """
    Generates a plot of the stock price for the last year.
    """
    try:
        data = yf.download(tickers=ticker, period='1y')
        plt.figure(figsize=[10, 5])
        plt.plot(data.index, data['Close'])
        plt.title(f'{ticker} Stock Price Over Last Year')
        plt.xlabel('Date')
        plt.ylabel('Stock Price ($)')
        plt.grid(True)
        st.pyplot()
    except:
        st.text("Sorry, couldn't find data for that ticker or unable to plot the chart.")

# Streamlit App Interface
st.title('Stock Analysis Assistant')

user_input = st.text_input('Enter your request (e.g., Get price for AAPL, Calculate 50-day SMA for MSFT):')

if user_input:
    tokens = user_input.lower().split()
    action = tokens[0]
    ticker = None
    if action == 'get':
        if len(tokens) >= 4 and tokens[2] == 'for':
            ticker = tokens[3].upper()
        else:
            st.write("Invalid input format. Please specify 'get price for [ticker]' for stock price.")
    elif action == 'calculate':
        if len(tokens) >= 6 and tokens[1].isdigit() and tokens[3] in ['sma', 'ema', 'rsi', 'macd'] and tokens[4] == 'for':
            ticker = tokens[5].upper()
        else:
            st.write("Invalid input format. Please specify 'calculate [window] [indicator] for [ticker]' for calculating indicators.")
    elif action == 'plot':
        if len(tokens) >= 3 and tokens[1] == 'for':
            ticker = tokens[2].upper()
        else:
            st.write("Invalid input format. Please specify 'plot for [ticker]' for plotting.")

    window = int(tokens[1]) if action == 'calculate' and len(tokens) >= 3 and tokens[1].isdigit() else None  # Optional window for moving averages

    if action in ['get', 'show']:
        if ticker:
            response = get_stock_price(ticker)
        else:
            response = "Invalid input format. Please specify 'get price' or 'show price' for stock price."
    elif action == 'calculate':
        if window and ticker:
            if tokens[3] == 'sma':
                response = calculate_SMA(ticker, window)
            elif tokens[3] == 'ema':
                response = calculate_EMA(ticker, window)
            elif tokens[3] == 'rsi':
                response = calculate_RSI(ticker)
            elif tokens[3] == 'macd':
                response = calculate_MACD(ticker)
            else:
                response = "Invalid indicator. Please specify 'SMA', 'EMA', 'RSI', or 'MACD'."
        else:
            response = "Invalid input format. Please specify 'calculate' followed by window (number) and indicator (SMA, EMA, RSI, MACD)."
    elif action == 'plot':
        if ticker:
            plot_stock_price(ticker)
            response = None  # Don't display a text response for plot
        else:
            response = "Invalid input format. Please specify 'plot' followed by the stock ticker symbol."
    else:
        response = "Sorry, I don't understand your request. Please try again using proper keywords (get price, calculate indicator, plot)."

    # Display the response
    st.write(response)
