"""
Web interface for guessing historical stock market cap.
"""

from datetime import datetime, timedelta

import yfinance as yf
from flask import Flask, render_template_string, request

from stock_data import StockDataFetcher


app = Flask(__name__)
stock_fetcher = StockDataFetcher()

PAGE_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>StockGuessr Market Cap Challenge</title>
</head>
<body>
    <h1>StockGuessr: Market Cap Challenge</h1>
    <p>Guess a stock's market cap on a specific day in history. Score ranges from 1 to 5000.</p>

    <form method="post">
        <label for="ticker">Ticker:</label>
        <input id="ticker" name="ticker" value="{{ ticker }}" required>
        <br><br>
        <label for="target_date">Date (YYYY-MM-DD):</label>
        <input id="target_date" name="target_date" value="{{ target_date }}" required>
        <br><br>
        <label for="guess_market_cap">Your market cap guess (USD):</label>
        <input id="guess_market_cap" name="guess_market_cap" value="{{ guess_market_cap }}" required>
        <br><br>
        <button type="submit">Submit Guess</button>
    </form>

    {% if error %}
        <p style="color: red;">{{ error }}</p>
    {% endif %}

    {% if result %}
        <h2>Result</h2>
        <p><strong>Score:</strong> {{ result.score }} / 5000</p>
        <p><strong>Stock price on {{ target_date }}:</strong> ${{ "%.2f"|format(result.price_at_date) }}</p>
        <p><strong>Actual market cap:</strong> {{ result.actual_market_cap_display }}</p>

        <h3>Helpful historical price context</h3>
        <ul>
            {% for label, price in result.related_prices.items() %}
                <li>{{ label }}: ${{ "%.2f"|format(price) if price is not none else "N/A" }}</li>
            {% endfor %}
        </ul>

        <h3>Recent trend into that date (30-day window)</h3>
        <ul>
            <li>Latest close before date: ${{ "%.2f"|format(result.context.latest_close) }}</li>
            <li>30-day average close: ${{ "%.2f"|format(result.context.average_close) }}</li>
            <li>30-day high: ${{ "%.2f"|format(result.context.high) }}</li>
            <li>30-day low: ${{ "%.2f"|format(result.context.low) }}</li>
            <li>30-day price change: {{ "%.2f"|format(result.context.price_change_pct) }}%</li>
        </ul>
    {% endif %}
</body>
</html>
"""


def calculate_score(guess_market_cap: float, actual_market_cap: float) -> int:
    """Calculate a score from 1-5000 based on relative error."""
    if actual_market_cap <= 0:
        return 1
    error_ratio = abs(guess_market_cap - actual_market_cap) / actual_market_cap
    clamped_error = min(error_ratio, 1.0)
    return max(1, min(5000, int(round(5000 * (1 - clamped_error)))))


def format_market_cap(value: float) -> str:
    """Format market cap with readable units."""
    abs_value = abs(value)
    if abs_value >= 1_000_000_000_000:
        return f"${value / 1_000_000_000_000:.2f}T"
    if abs_value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.2f}B"
    if abs_value >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    return f"${value:.2f}"


def get_stock_game_data(ticker: str, target_date: str):
    """Fetch stock data needed for the guessing interface."""
    price_at_date = stock_fetcher.get_price_at_date(ticker, target_date)
    if price_at_date is None:
        return None, "Could not fetch stock price for the requested date."

    try:
        stock_info = yf.Ticker(ticker).info
        shares_outstanding = stock_info.get('sharesOutstanding') if isinstance(stock_info, dict) else None
    except (AttributeError, KeyError, TypeError, ValueError):
        shares_outstanding = None

    if not shares_outstanding:
        return None, "Could not fetch shares outstanding needed to estimate market cap."

    actual_market_cap = float(price_at_date) * float(shares_outstanding)
    context = stock_fetcher.get_historical_context(ticker, target_date, lookback_days=30)
    if not context:
        return None, "Could not fetch historical context for the requested date."

    target_dt = datetime.strptime(target_date, "%Y-%m-%d")
    related_prices = {
        "1 day before": stock_fetcher.get_price_at_date(ticker, (target_dt - timedelta(days=1)).strftime("%Y-%m-%d")),
        "1 week before": stock_fetcher.get_price_at_date(ticker, (target_dt - timedelta(days=7)).strftime("%Y-%m-%d")),
        "1 month before": stock_fetcher.get_price_at_date(ticker, (target_dt - timedelta(days=30)).strftime("%Y-%m-%d")),
    }

    return {
        'price_at_date': float(price_at_date),
        'actual_market_cap': actual_market_cap,
        'actual_market_cap_display': format_market_cap(actual_market_cap),
        'related_prices': related_prices,
        'context': context,
    }, None


@app.route('/', methods=['GET', 'POST'])
def index():
    """Render and process market cap guessing form."""
    default_date = '2024-01-02'
    ticker = request.form.get('ticker', 'AAPL').upper().strip()
    target_date = request.form.get('target_date', default_date).strip()
    guess_market_cap = request.form.get('guess_market_cap', '').strip()

    result = None
    error = None

    if request.method == 'POST':
        try:
            datetime.strptime(target_date, "%Y-%m-%d")
        except ValueError:
            error = "Invalid date format. Please use YYYY-MM-DD."
        else:
            try:
                guess_value = float(guess_market_cap)
                if guess_value <= 0:
                    raise ValueError
            except ValueError:
                error = "Please provide a valid positive number for your guess."
            else:
                data, error = get_stock_game_data(ticker, target_date)
                if data:
                    data['score'] = calculate_score(guess_value, data['actual_market_cap'])
                    result = data

    return render_template_string(
        PAGE_TEMPLATE,
        ticker=ticker,
        target_date=target_date,
        guess_market_cap=guess_market_cap,
        result=result,
        error=error,
    )


if __name__ == '__main__':
    app.run()
