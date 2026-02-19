# StockGuessr

A testing model for Large Language Models (LLMs) to evaluate how well they can predict stock prices when their information is restricted to a specific date in the past.

## Overview

StockGuessr is a framework designed to test LLM capabilities in financial prediction tasks with temporal constraints. It:

1. **Restricts Information**: Provides the LLM with historical stock data only up to a specified cutoff date
2. **Makes Predictions**: Asks the LLM to predict stock prices for a future target date
3. **Evaluates Accuracy**: Compares predictions against actual historical prices
4. **Measures Performance**: Calculates error metrics to assess prediction quality

This allows researchers to understand how well LLMs can make financial predictions when they don't have access to future information (mimicking real-world prediction scenarios).

## Features

- 📊 Fetch historical stock data using Yahoo Finance API
- 🤖 Integration with OpenAI's GPT models for predictions
- 📅 Configurable date restrictions (cutoff date vs target date)
- 📈 Multiple ticker support
- 🎯 Comprehensive evaluation metrics (absolute error, percentage error, statistics)
- ⚙️ JSON-based configuration
- 📝 Detailed and summary reporting

## Quick Start

See [QUICKSTART.md](QUICKSTART.md) for a quick introduction.

### Try the Demo

Run the demo with mock data (no API key required):
```bash
python demo.py
```

This demonstrates the full workflow without requiring an OpenAI API key or making network requests.

## Installation

1. **Clone the repository**:
```bash
git clone https://github.com/wenbinio/stockguessr.git
cd stockguessr
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**:
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

## Configuration

Create a `config.json` file (or modify the existing one):

```json
{
  "tickers": ["AAPL", "MSFT", "GOOGL"],
  "cutoff_date": "2024-01-01",
  "target_date": "2024-06-01",
  "lookback_days": 90,
  "model": "gpt-3.5-turbo"
}
```

### Configuration Parameters

- `tickers`: List of stock ticker symbols to test (e.g., ["AAPL", "MSFT"])
- `cutoff_date`: Date when the LLM's information is restricted (YYYY-MM-DD)
- `target_date`: Future date to predict stock price for (YYYY-MM-DD)
- `lookback_days`: Number of days of historical data to provide (default: 90)
- `model`: OpenAI model to use (default: "gpt-3.5-turbo", alternatives: "gpt-4", "gpt-4-turbo")

## Usage

### Basic Usage

Run the test with the default configuration:

```bash
python main.py
```

### Web Interface

Run the website interface for guessing market cap on a historical day:

```bash
python web_app.py
```

Then open `http://127.0.0.1:5000` in your browser.

### Custom Configuration

Specify a custom config file:

```bash
python main.py --config my_config.json
```

### Verbose Output

Get detailed output including full LLM responses:

```bash
python main.py --verbose
```

## Example Output

```
=== Stock Price Prediction Test ===
Model: gpt-3.5-turbo
Cutoff Date: 2024-01-01
Target Date: 2024-06-01
Tickers: AAPL, MSFT, GOOGL
Lookback Period: 90 days

--- Testing AAPL ---
Fetching historical data up to 2024-01-01...
Getting LLM prediction for 2024-06-01...
LLM Prediction: $185.50
Fetching actual price for 2024-06-01...
Actual Price: $192.25
Absolute Error: $6.75
Percentage Error: 3.51%

==================================================
=== Summary Statistics ===
Number of predictions: 3
Mean Absolute Error: $5.23
Median Absolute Error: $4.80
Mean Percentage Error: 2.85%
Median Percentage Error: 2.50%
Min Percentage Error: 1.20%
Max Percentage Error: 5.10%
==================================================
```

## How It Works

### 1. Data Fetching
The `stock_data.py` module uses the yfinance library to fetch historical stock data from Yahoo Finance.

### 2. LLM Prediction
The `llm_predictor.py` module:
- Creates a prompt with historical context up to the cutoff date
- Instructs the LLM that it has no knowledge beyond the cutoff date
- Asks for a price prediction for the target date
- Extracts the numerical prediction from the LLM's response

### 3. Evaluation
The `evaluator.py` module:
- Compares predicted prices to actual historical prices
- Calculates error metrics (absolute error, percentage error)
- Provides summary statistics across all predictions

## Project Structure

```
stockguessr/
├── main.py              # Main entry point for running tests
├── stock_data.py        # Stock data fetching using yfinance
├── llm_predictor.py     # LLM interaction and prediction logic
├── evaluator.py         # Evaluation and scoring system
├── demo.py              # Demo script with mock data
├── config.json          # Default configuration
├── config.example.json  # Example configuration
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
├── README.md            # This file
└── QUICKSTART.md        # Quick start guide
```

## Use Cases

- **Research**: Study LLM capabilities in time-constrained prediction tasks
- **Model Comparison**: Test different LLM models (GPT-3.5 vs GPT-4) on the same task
- **Temporal Analysis**: Vary the gap between cutoff and target dates to see how prediction accuracy changes
- **Market Testing**: Test predictions for different market conditions (bull/bear markets)
- **Benchmark Creation**: Create standardized tests for evaluating LLM financial reasoning

## Limitations

- **Historical Data Only**: This tests prediction accuracy on historical data, not real-time predictions
- **LLM Training Data**: LLMs may have seen some of the "future" data during training
- **API Costs**: OpenAI API calls incur costs based on token usage
- **Data Availability**: Stock data availability depends on Yahoo Finance
- **Market Hours**: Predictions are for closing prices on trading days

## Contributing

Contributions are welcome! Feel free to:
- Add support for other LLM providers (Anthropic, Cohere, etc.)
- Implement additional evaluation metrics
- Add visualization capabilities
- Improve price extraction from LLM responses
- Add unit tests

## License

MIT License - feel free to use this project for research and educational purposes.

## Disclaimer

This tool is for research and educational purposes only. It should not be used for actual investment decisions. Stock market predictions are inherently uncertain, and past performance does not guarantee future results.
