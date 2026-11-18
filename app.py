
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# Page settings
st.set_page_config(
    page_title="Stock Analyzer",
    page_icon="📈",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
.stApp {
    background-color: #0b1120;
    color: white;
}
[data-testid="stMetric"] {
    background-color: #151f32;
    padding: 20px;
    border-radius: 12px;
}
h1, h2, h3 {
    color: #60a5fa;
}
</style>
""", unsafe_allow_html=True)

# Header
st.title("📈 STOCK ANALYZER")
st.caption("Real-time stock research powered by Yahoo Finance")

st.divider()

# Search
col1, col2 = st.columns([4, 1])

with col1:
    ticker = st.text_input(
        "Enter Stock Symbol",
        placeholder="Example: AAPL, NVDA, TSLA, RELIANCE.NS"
    ).strip().upper()

with col2:
    st.write("")
    st.write("")
    search = st.button("Analyze Stock", use_container_width=True)

# Format numbers
def format_number(value):
    if value is None or pd.isna(value):
        return "N/A"

    if abs(value) >= 1e12:
        return f"{value / 1e12:.2f} T"
    elif abs(value) >= 1e9:
        return f"{value / 1e9:.2f} B"
    elif abs(value) >= 1e6:
        return f"{value / 1e6:.2f} M"
    else:
        return f"{value:,.2f}"

# Analyze
if search and ticker:

    with st.spinner("Fetching stock data..."):

        try:
            stock = yf.Ticker(ticker)

            info = stock.info
            history = stock.history(period="1y")

            if not info or history.empty:
                st.error("Stock not found or data unavailable.")
                st.stop()

            # Company details
            st.subheader(
                info.get("longName", ticker)
            )

            st.write(
                info.get("longBusinessSummary",
                         "Company description unavailable.")
            )

            st.divider()

            # Price
            current_price = info.get("currentPrice")
            if current_price is None:
                current_price = info.get("regularMarketPrice")

            currency = info.get("currency", "")

            st.subheader("📊 Stock Overview")

            c1, c2, c3, c4 = st.columns(4)

            c1.metric(
                "Current Price",
                f"{currency} {current_price:,.2f}"
                if current_price is not None else "N/A"
            )

            c2.metric(
                "Market Cap",
                format_number(info.get("marketCap"))
            )

            c3.metric(
                "Trailing P/E",
                format_number(info.get("trailingPE"))
            )

            c4.metric(
                "Forward P/E",
                format_number(info.get("forwardPE"))
            )

            # Financial metrics
            st.subheader("💰 Financial Metrics")

            c1, c2, c3, c4 = st.columns(4)

            c1.metric(
                "EPS",
                format_number(info.get("trailingEps"))
            )

            c2.metric(
                "Revenue",
                format_number(info.get("totalRevenue"))
            )

            c3.metric(
                "Net Income",
                format_number(info.get("netIncomeToCommon"))
            )

            c4.metric(
                "Dividend Yield",
                f"{info.get('dividendYield') * 100:.2f}%"
                if info.get("dividendYield") is not None
                else "N/A"
            )

            # Valuation and risk
            st.subheader("📌 Valuation & Risk")

            c1, c2, c3, c4 = st.columns(4)

            c1.metric(
                "52 Week High",
                format_number(info.get("fiftyTwoWeekHigh"))
            )

            c2.metric(
                "52 Week Low",
                format_number(info.get("fiftyTwoWeekLow"))
            )

            c3.metric(
                "Beta",
                format_number(info.get("beta"))
            )

            c4.metric(
                "Price to Book",
                format_number(info.get("priceToBook"))
            )

            st.divider()

            # Historical chart
            st.subheader("📈 Historical Price Chart")

            period = st.selectbox(
                "Select Time Period",
                ["1mo", "3mo", "6mo", "1y", "2y", "5y"]
            )

            chart_data = stock.history(period=period)

            if not chart_data.empty:

                fig = go.Figure()

                fig.add_trace(go.Scatter(
                    x=chart_data.index,
                    y=chart_data["Close"],
                    mode="lines",
                    name="Closing Price",
                    line=dict(color="#38bdf8", width=2)
                ))

                fig.update_layout(
                    template="plotly_dark",
                    height=450,
                    xaxis_title="Date",
                    yaxis_title=f"Price ({currency})",
                    paper_bgcolor="#0b1120",
                    plot_bgcolor="#151f32",
                    hovermode="x unified"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            # Company information
            st.subheader("🏢 Company Information")

            c1, c2 = st.columns(2)

            with c1:
                st.write("**Sector:**", info.get("sector", "N/A"))
                st.write("**Industry:**", info.get("industry", "N/A"))
                st.write("**Country:**", info.get("country", "N/A"))

            with c2:
                st.write("**Employees:**", format_number(
                    info.get("fullTimeEmployees")
                ))
                st.write("**Website:**", info.get("website", "N/A"))
                st.write("**Exchange:**", info.get("exchange", "N/A"))

            st.success("Stock analysis completed!")

        except Exception as e:
            st.error(f"Unable to fetch stock data: {e}")

elif search:
    st.warning("Please enter a stock symbol.")

st.divider()

st.caption(
    "Data source: Yahoo Finance via yfinance. "
    "Data may be delayed or unavailable. "
    "For educational and research purposes only."
)
