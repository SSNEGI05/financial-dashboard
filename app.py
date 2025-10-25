# --- IMPORTS (from all our steps) ---
import streamlit as st
import yfinance as yf
import pandas as pd
import datetime # New import for dates
import pandas_datareader.data as web # New import for FRED data

# --- STEP 10 BONUS: Set Page Layout ---
# This MUST be the first 'st' command in your app
# This makes your app use the full width of the screen
st.set_page_config(layout="wide")

# --- STEP 8: THE SIDEBAR ---
st.sidebar.title("Shubh's Analyst Toolkit")
st.sidebar.write("Navigation")

# We have added "Macro Dashboard" to this list
page = st.sidebar.radio(
    "Select a Tool:",
    ("Welcome Page", "Stock Analysis Tool", "Stock Comparator", "Simple DCF Calculator", "Macro Dashboard")
)

# ==============================================================================
# --- PAGE 1: WELCOME PAGE ---
# ==============================================================================
if page == "Welcome Page":
    
    st.title("Welcome to your Analyst Dashboard")
    st.write("Use the navigation on the left to select a tool.")
    st.write("This application is built entirely in Python using Streamlit.")
    st.markdown("---") 

    st.header("My First Interactive Tool")
    user_name = st.text_input("What is your name?")
    
    if st.button("Click Me", key="welcome_button"):
        st.success(f"Hello, {user_name}! Welcome to your dashboard.")
    else:
        st.info("Please type your name and click the button.")

# ==============================================================================
# --- PAGE 2: STOCK ANALYSIS TOOL ---
# ==============================================================================
elif page == "Stock Analysis Tool":
    
    st.header("Stock Analysis Tool")
    
    ticker_symbol = st.text_input("Enter Stock Ticker", "AAPL") 
    
    if st.button("Get Stock Info", key="stock_info_button"):
        try:
            stock = yf.Ticker(ticker_symbol)
            info = stock.info
            st.subheader(f"{info['longName']} ({ticker_symbol.upper()})")
            
            hist = stock.history(period="1y") 
            st.subheader("1-Year Price Chart")
            st.line_chart(hist['Close'])
            
            st.subheader("Business Summary")
            st.write(info['longBusinessSummary'])
            
            st.subheader("Quarterly Income Statement")
            st.dataframe(stock.quarterly_financials)
            
        except Exception as e:
            st.error(f"Could not retrieve data for {ticker_symbol}. Is it a valid ticker?")
            st.write(f"Error details: {e}")

# ==============================================================================
# --- PAGE 3: STOCK COMPARATOR ---
# ==============================================================================
elif page == "Stock Comparator":
    st.header("Stock Comparison Tool")
    
    default_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA']
    selected_tickers = st.multoselect(
        "Select stocks to compare (2 or more):",
        options=default_tickers,
        default=['AAPL', 'MSFT']
    )
    
    if len(selected_tickers) > 1:
        metrics_list = []
        price_data_list = []
        
        for ticker in selected_tickers:
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                metrics_list.append({
                    'Ticker': ticker,
                    'Company Name': info.get('shortName', 'N_A'),
                    'P/E Ratio': f"{info.get('trailingPE', 0):.2f}",
                    'Fwd P/E': f"{info.get('forwardPE', 0):.2f}",
                    'Div. Yield (%)': f"{info.get('dividendYield', 0) * 100:.2f}"
                })
                hist = stock.history(period="1y")['Close']
                hist.name = ticker
                price_data_list.append(hist)
            except Exception as e:
                st.warning(f"Could not retrieve data for {ticker}. Skipping. Error: {e}")
        
        if metrics_list:
            st.subheader("Key Metrics Comparison")
            metrics_df = pd.DataFrame(metrics_list)
            st.dataframe(metrics_df.set_index('Ticker'))
        
        if price_data_list:
            st.subheader("1-Year Normalized Price Performance")
            price_df = pd.concat(price_data_list, axis=1)
            normalized_df = price_df / price_df.iloc[0]
            st.line_chart(normalized_df)
    else:
        st.info("Please select at least two stocks to compare.")

# ==============================================================================
# --- PAGE 4: DCF CALCULATOR ---
# ==============================================================================
elif page == "Simple DCF Calculator":

    st.header("Simple 2-Stage DCF Calculator")
    st.write("This tool calculates intrinsic value based on your assumptions.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Assumptions")
        fcf = st.number_input("Last 12M Free Cash Flow ($M)", min_value=0, value=1000, key="dcf_fcf")
        g_short = st.number_input("Short-Term Growth (Yrs 1-5) (%)", value=10.0, step=0.5, key="dcf_g_short")
    with col2:
        st.subheader("Rates")
        wacc = st.number_input("Discount Rate (WACC) (%)", value=8.0, step=0.25, key="dcf_wacc")
        g_long = st.number_input("Perpetual Growth Rate (%)", value=2.5, step=0.1, key="dcf_g_long")

    if st.button("Calculate DCF Value", key="dcf_calc_button"):
        g_short_dec = g_short / 100
        wacc_dec = wacc / 100
        g_long_dec = g_long / 100

        if wacc_dec <= g_long_dec:
            st.error("Error: Discount Rate (WACC) must be greater than Perpetual Growth Rate.")
        else:
            # ... (Rest of DCF logic is unchanged) ...
            pv_fcf_list = []
            current_fcf = fcf
            for i in range(1, 6):
                future_fcf = current_fcf * (1 + g_short_dec)
                pv_fcf = future_fcf / ((1 + wacc_dec) ** i)
                pv_fcf_list.append(pv_fcf)
                current_fcf = future_fcf 
            sum_pv_fcf = sum(pv_fcf_list)
            
            fcf_terminal_year = current_fcf * (1 + g_long_dec)
            terminal_value = fcf_terminal_year / (wacc_dec - g_long_dec)
            pv_terminal_value = terminal_value / ((1 + wacc_dec) ** 5)
            
            total_intrinsic_value = sum_pv_fcf + pv_terminal_value
            
            st.subheader("Result")
            st.success(f"Calculated Intrinsic Value: ${total_intrinsic_value:,.2f} M")
            st.write(f"PV of 5-Year FCFs: ${sum_pv_fcf:,.2f} M")
            st.write(f"PV of Terminal Value: ${pv_terminal_value:,.2f} M")

# ==============================================================================
# --- PAGE 5: MACRO DASHBOARD (OUR NEW STEP 11) ---
# ==============================================================================
elif page == "Macro Dashboard":
    st.header("Macroeconomic Dashboard")
    st.write("Data sourced from FRED (Federal Reserve Economic Data)")

    # 1. Define the metrics we want
    # These are the official FRED ticker symbols
    METRICS = {
        "10-Year Treasury (DGS10)": "DGS10",
        "Yield Curve (T10Y2Y)": "T10Y2Y",
        "CPI Inflation (CPIAUCSL_PC1)": "CPIAUCSL_PC1", # % Change from 1 Year Ago
        "Unemployment Rate (UNRATE)": "UNRATE"
    }
    
    # 2. Set a start date for our charts
    start_date = datetime.datetime(2010, 1, 1)
    end_date = datetime.date.today()
    
    # 3. Create columns for layout
    col1, col2 = st.columns(2)
    
    # We will alternate between col1 and col2 for a nice 2x2 grid
    columns_to_use = [col1, col2, col1, col2]
    
    st.info("Loading data... This may take a moment.")
    
    # 4. Loop through our metrics, download data, and plot
    # 'zip' lets us loop through two lists at the same time
    for (metric_name, metric_ticker), col in zip(METRICS.items(), columns_to_use):
        try:
            # 'web.DataReader' is the new command we're using
            data = web.DataReader(
                metric_ticker, 
                "fred", # The data source
                start_date, 
                end_date
            )
            
            # Use the 'with col:' to put the chart in the correct column
            with col:
                st.subheader(metric_name)
                # Plot the data
                st.line_chart(data)

        except Exception as e:
            st.error(f"Could not load data for {metric_name}. Error: {e}")
