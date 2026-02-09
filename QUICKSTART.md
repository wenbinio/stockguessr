# Quick Start Guide

## Prerequisites

- Python 3.8 or higher
- pip package manager
- API key for an LLM provider (OpenAI, Groq, Mistral, Together AI, etc.)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/wenbinio/stockguessr.git
cd stockguessr
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your API key:
```bash
cp .env.example .env
# Edit .env and add your LLM provider API key:
# OPENAI_API_KEY=sk-your-actual-key-here
# Or for other providers, e.g.:
# GROQ_API_KEY=your-groq-key-here
```

## Quick Demo

Run the demo with mock data (no API key needed):
```bash
python demo.py
```

This will show you how the system works without making actual API calls.

## Running Real Tests

1. Edit `config.json` to set your test parameters:
```json
{
  "tickers": ["AAPL", "MSFT"],
  "cutoff_date": "2024-01-01",
  "target_date": "2024-06-01",
  "lookback_days": 90,
  "model": "gpt-3.5-turbo",
  "api_base_url": null,
  "api_key_env_var": "OPENAI_API_KEY"
}
```

2. Run the test:
```bash
python main.py
```

3. For verbose output:
```bash
python main.py --verbose
```

## Understanding the Configuration

- **tickers**: Stock symbols to test (e.g., AAPL for Apple, MSFT for Microsoft)
- **cutoff_date**: The date when LLM's knowledge is restricted to
- **target_date**: The future date to predict prices for
- **lookback_days**: How many days of historical data to provide (default: 90)
- **model**: Which LLM model to use (depends on your provider)
- **api_base_url**: Custom API base URL for non-OpenAI providers (null for OpenAI)
- **api_key_env_var**: Environment variable name for your API key (default: OPENAI_API_KEY)

## Example Use Cases

### Test Recent Predictions
```json
{
  "tickers": ["TSLA", "NVDA"],
  "cutoff_date": "2024-01-01",
  "target_date": "2024-03-01",
  "lookback_days": 30
}
```

### Compare Different Time Gaps
Create multiple configs with the same cutoff but different target dates:
- `config_1month.json`: target 1 month after cutoff
- `config_3month.json`: target 3 months after cutoff  
- `config_6month.json`: target 6 months after cutoff

### Test Different Market Conditions
- Bull market: Use dates during market upswings
- Bear market: Use dates during market downturns
- Volatile periods: Use dates around major events

## Tips

1. **Start small**: Test with 1-2 tickers first to save on API costs
2. **Use GPT-3.5-turbo**: It's cheaper and often sufficient for this task
3. **Check date ranges**: Ensure target_date is after cutoff_date
4. **Trading days only**: Predictions work best for actual trading days (Mon-Fri)
5. **Save results**: Copy the output to a file for later analysis

## Cost Estimation

LLM API costs vary by provider (approximate per prediction):
- OpenAI GPT-3.5-turbo: ~$0.01-0.02
- OpenAI GPT-4: ~$0.10-0.20
- Groq (Llama 3): Free tier available
- Together AI: ~$0.01-0.05
- Ollama (local): Free

For a test with 5 stocks:
- GPT-3.5-turbo: ~$0.05-0.10
- GPT-4: ~$0.50-1.00

## Troubleshooting

**"API key not provided"**
- Make sure you have a `.env` file with the correct API key (e.g., `OPENAI_API_KEY=your-key`)
- If using a different provider, set `api_key_env_var` in config to match your env var name

**"No data found for ticker"**
- Check that the ticker symbol is correct
- Ensure dates are in YYYY-MM-DD format
- Try a different date range

**"Could not fetch actual price"**
- The target date might be a weekend/holiday
- Yahoo Finance might be temporarily unavailable
- Check your internet connection

## Next Steps

After running your first test:
1. Try different models and providers (OpenAI, Groq, Mistral, etc.)
2. Vary the time gap between cutoff and target dates
3. Test with different types of stocks (tech, value, growth)
4. Compare results across multiple runs
5. Analyze patterns in prediction errors

## Getting Help

- Check the main README.md for detailed documentation
- Review the code comments for implementation details
- Open an issue on GitHub for bugs or questions
