
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="Stock Analyzer",
    page_icon="📈",
    layout="wide"
)

# ---------------- CUSTOM CSS ----------------

st.markdown("""
<style>
.stApp {
    background-color: #0b1120;
    color: white;
}
[data-testid="stMetric"] {
    background-color: #151f32;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #26344d;
}
h1, h2, h3 {
    color: #60a5fa;
}
.stButton > button {
    background-color: #2563eb;
    color: white;
    border-radius: 8px;
    border: none;
}
</style>
""", unsafe_allow_html=True)


# ---------------- HEADER ----------------

st.title("📈 STOCK ANALYZER")
st.caption("Smart Stock Research | Powered by Yahoo Finance")
st.divider()


# ---------------- HELPER FUNCTIONS ----------------

def format_number(value):

    if value is None:
        return "N/A"

    try:
        if pd.isna(value):
            return "N/A"

        value = float(value)

        if abs(value) >= 1e12:
            return f"{value / 1e12:.2f} T"

        elif abs(value) >= 1e9:
            return f"{value / 1e9:.2f} B"

        elif abs(value) >= 1e6:
            return f"{value / 1e6:.2f} M"

        return f"{value:,.2f}"

    except (ValueError, TypeError):
        return "N/A"


def get_stock_symbol(query):

    query = query.strip().upper()

    if not query:
        return None

    # First try exact ticker
    try:
        stock = yf.Ticker(query)
        info = stock.info

        if info and info.get("quoteType") == "EQUITY":
            return query

    except Exception:
        pass

    # Try Indian exchanges
    for suffix in [".NS", ".BO"]:

        try:
            symbol = query + suffix
            stock = yf.Ticker(symbol)
            info = stock.info

            if info and info.get("quoteType") == "EQUITY":
                return symbol

        except Exception:
            pass

    # Search by company name
    try:
        results = yf.Search(
            query,
            max_results=10,
            news_count=0
        )

        for item in results.quotes:

            if item.get("quoteType") == "EQUITY":
                return item.get("symbol")

    except Exception:
        pass

    return None


# ---------------- STOCK SEARCH ----------------

st.subheader("🔍 Search Company")

with st.form("stock_search"):

    ticker_input = st.text_input(
        "Company Name or Stock Symbol",
        placeholder="Netflix, Apple, Crizac, AAPL, RELIANCE.NS"
    )

    search = st.form_submit_button(
        "Analyze Stock",
        use_container_width=True
    )


# ---------------- ANALYSIS ----------------

if search:

    if not ticker_input.strip():

        st.warning("Please enter a company name or ticker.")

    else:

        with st.spinner("Searching Yahoo Finance..."):

            symbol = get_stock_symbol(ticker_input)

        if not symbol:

            st.error(
                "Stock not found. Try entering its exact ticker symbol."
            )

        else:

            with st.spinner(f"Fetching data for {symbol}..."):

                try:

                    stock = yf.Ticker(symbol)
                    info = stock.info
                    history = stock.history(period="1y")

                    if not info or history.empty:
                        st.error("Stock data is unavailable.")
                        st.stop()

                    # ---------------- COMPANY DETAILS ----------------

                    company = info.get("longName", symbol)
                    currency = info.get("currency", "")

                    st.success(f"Found: {company} ({symbol})")

                    st.header(company)

                    description = info.get(
                        "longBusinessSummary",
                        "Company description unavailable."
                    )

                    st.write(description)

                    st.divider()

                    # ---------------- PRICE OVERVIEW ----------------

                    st.subheader("📊 Stock Overview")

                    current_price = info.get("currentPrice")

                    if current_price is None:
                        current_price = info.get("regularMarketPrice")

                    previous_close = info.get("previousClose")

                    change = None

                    if current_price is not None and previous_close:
                        change = (
                            (current_price - previous_close)
                            / previous_close
                        ) * 100

                    c1, c2, c3, c4 = st.columns(4)

                    c1.metric(
                        "Current Price",
                        f"{currency} {current_price:,.2f}"
                        if current_price is not None else "N/A",
                        f"{change:.2f}%"
                        if change is not None else None
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

                    # ---------------- FINANCIAL METRICS ----------------

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

                    dividend = info.get("dividendYield")

                    c4.metric(
                        "Dividend Yield",
                        f"{dividend * 100:.2f}%"
                        if dividend is not None else "N/A"
                    )

                    # ---------------- VALUATION ----------------

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

                    # ---------------- HISTORICAL CHART ----------------

                    st.subheader("📈 Historical Stock Price")

                    period = st.selectbox(
                        "Select Time Period",
                        ["1mo", "3mo", "6mo", "1y", "2y", "5y"]
                    )

                    chart_data = stock.history(period=period)

                    if not chart_data.empty:

                        fig = go.Figure()

                        fig.add_trace(
                            go.Scatter(
                                x=chart_data.index,
                                y=chart_data["Close"],
                                mode="lines",
                                name="Closing Price",
                                line=dict(
                                    color="#38bdf8",
                                    width=2
                                )
                            )
                        )

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

                    else:

                        st.warning("Historical data unavailable.")

                    # ---------------- COMPANY INFORMATION ----------------

                    st.subheader("🏢 Company Information")

                    c1, c2 = st.columns(2)

                    with c1:

                        st.write(
                            "**Sector:**",
                            info.get("sector", "N/A")
                        )

                        st.write(
                            "**Industry:**",
                            info.get("industry", "N/A")
                        )

                        st.write(
                            "**Country:**",
                            info.get("country", "N/A")
                        )

                    with c2:

                        st.write(
                            "**Employees:**",
                            format_number(
                                info.get("fullTimeEmployees")
                            )
                        )

                        st.write(
                            "**Website:**",
                            info.get("website", "N/A")
                        )

                        st.write(
                            "**Exchange:**",
                            info.get("exchange", "N/A")
                        )

                    st.success("Analysis completed!")

                except Exception as e:

                    st.error(f"Unable to fetch stock data: {e}")


# ---------------- FOOTER ----------------

st.divider()

st.caption(
    "Data Source: Yahoo Finance via yfinance | "
    "Data may be delayed or unavailable. "
    "For educational and research purposes only."
)
