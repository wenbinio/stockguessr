"""
Demo script showing StockGuessr functionality with mock data.
This demonstrates the flow without requiring API keys or network access.
"""

from evaluator import StockPredictionEvaluator


class MockStockDataFetcher:
    """Mock stock data fetcher for demo purposes."""
    
    def get_historical_context(self, ticker, cutoff_date, lookback_days=90):
        """Return mock historical context."""
        mock_data = {
            'AAPL': {'ticker': 'AAPL', 'cutoff_date': cutoff_date, 'lookback_days': lookback_days,
                     'latest_close': 185.50, 'average_close': 180.25, 'high': 195.00,
                     'low': 170.00, 'volatility': 5.25, 'price_change_pct': 8.5},
            'MSFT': {'ticker': 'MSFT', 'cutoff_date': cutoff_date, 'lookback_days': lookback_days,
                     'latest_close': 375.00, 'average_close': 365.00, 'high': 390.00,
                     'low': 355.00, 'volatility': 8.50, 'price_change_pct': 5.2},
            'GOOGL': {'ticker': 'GOOGL', 'cutoff_date': cutoff_date, 'lookback_days': lookback_days,
                      'latest_close': 140.00, 'average_close': 135.00, 'high': 145.00,
                      'low': 128.00, 'volatility': 4.20, 'price_change_pct': 7.8}
        }
        return mock_data.get(ticker, {})
    
    def get_price_at_date(self, ticker, date):
        """Return mock actual price."""
        mock_prices = {
            'AAPL': 192.25,
            'MSFT': 385.50,
            'GOOGL': 145.30
        }
        return mock_prices.get(ticker, None)


class MockLLMPredictor:
    """Mock LLM predictor for demo purposes."""
    
    def __init__(self):
        pass
    
    def predict_stock_price(self, ticker, target_date, cutoff_date, historical_context):
        """Return mock prediction."""
        # Simulate simple prediction: current price + random change
        mock_predictions = {
            'AAPL': 188.75,
            'MSFT': 380.25,
            'GOOGL': 143.50
        }
        
        predicted_price = mock_predictions.get(ticker, 100.0)
        
        return {
            'ticker': ticker,
            'target_date': target_date,
            'cutoff_date': cutoff_date,
            'predicted_price': predicted_price,
            'full_response': f"Based on historical trends, I predict {ticker} will be around ${predicted_price:.2f}",
            'model': 'mock-gpt',
            'success': True
        }


def run_demo():
    """Run a demonstration of the StockGuessr system."""
    
    print("=" * 60)
    print("StockGuessr Demo - Mock Data Simulation")
    print("=" * 60)
    
    # Initialize mock components
    stock_fetcher = MockStockDataFetcher()
    llm_predictor = MockLLMPredictor()
    evaluator = StockPredictionEvaluator()
    
    # Configuration
    tickers = ['AAPL', 'MSFT', 'GOOGL']
    cutoff_date = '2024-01-01'
    target_date = '2024-06-01'
    lookback_days = 90
    
    print(f"\nConfiguration:")
    print(f"  Cutoff Date: {cutoff_date}")
    print(f"  Target Date: {target_date}")
    print(f"  Tickers: {', '.join(tickers)}")
    print(f"  Lookback Period: {lookback_days} days\n")
    
    # Run predictions for each ticker
    for ticker in tickers:
        print(f"\n--- Testing {ticker} ---")
        
        # Get historical context
        print(f"Fetching historical data up to {cutoff_date}...")
        historical_context = stock_fetcher.get_historical_context(
            ticker, cutoff_date, lookback_days
        )
        
        print(f"Historical Context:")
        print(f"  Latest Close: ${historical_context['latest_close']:.2f}")
        print(f"  90-day Average: ${historical_context['average_close']:.2f}")
        print(f"  90-day High: ${historical_context['high']:.2f}")
        print(f"  90-day Low: ${historical_context['low']:.2f}")
        print(f"  Volatility: ${historical_context['volatility']:.2f}")
        print(f"  Price Change: {historical_context['price_change_pct']:.2f}%")
        
        # Get LLM prediction
        print(f"\nGetting LLM prediction for {target_date}...")
        prediction_result = llm_predictor.predict_stock_price(
            ticker, target_date, cutoff_date, historical_context
        )
        
        print(f"LLM Prediction: ${prediction_result['predicted_price']:.2f}")
        print(f"LLM Reasoning: {prediction_result['full_response']}")
        
        # Get actual price
        print(f"\nFetching actual price for {target_date}...")
        actual_price = stock_fetcher.get_price_at_date(ticker, target_date)
        print(f"Actual Price: ${actual_price:.2f}")
        
        # Evaluate
        eval_result = evaluator.evaluate_prediction(
            prediction_result['predicted_price'],
            actual_price,
            ticker,
            target_date
        )
        
        print(f"\nEvaluation:")
        print(f"  Absolute Error: ${eval_result['absolute_error']:.2f}")
        print(f"  Percentage Error: {eval_result['percentage_error']:.2f}%")
    
    # Print summary
    print("\n" + "=" * 60)
    evaluator.print_results(verbose=False)
    print("=" * 60)
    
    print("\n✓ Demo completed successfully!")
    print("\nNote: This demo uses mock data. In production:")
    print("  - Stock data would be fetched from Yahoo Finance (yfinance)")
    print("  - Predictions would come from OpenAI GPT models")
    print("  - Requires OPENAI_API_KEY in .env file")
    print("\nRun 'python main.py' with proper configuration for real testing.")


if __name__ == '__main__':
    run_demo()
