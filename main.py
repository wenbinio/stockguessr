"""
Main script for testing LLM stock price predictions.
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from dotenv import load_dotenv

from stock_data import StockDataFetcher
from llm_predictor import LLMPredictor
from evaluator import StockPredictionEvaluator


def load_config(config_file: str) -> dict:
    """Load configuration from JSON file."""
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Config file '{config_file}' not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error parsing config file: {e}")
        sys.exit(1)


def run_stock_prediction_test(config: dict, verbose: bool = False):
    """
    Run the stock prediction test based on configuration.
    
    Args:
        config: Configuration dictionary
        verbose: Whether to print verbose output
    """
    # Load environment variables
    load_dotenv()
    
    # Initialize components
    stock_fetcher = StockDataFetcher()
    evaluator = StockPredictionEvaluator()
    
    # Get configuration
    api_key = os.getenv('OPENAI_API_KEY')
    model = config.get('model', os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo'))
    
    try:
        llm_predictor = LLMPredictor(api_key=api_key, model=model)
    except ValueError as e:
        print(f"Error: {e}")
        print("Please set OPENAI_API_KEY in .env file or environment")
        sys.exit(1)
    
    # Get test parameters
    tickers = config.get('tickers', ['AAPL'])
    cutoff_date = config.get('cutoff_date')
    target_date = config.get('target_date')
    lookback_days = config.get('lookback_days', 90)
    
    if not cutoff_date or not target_date:
        print("Error: cutoff_date and target_date are required in config")
        sys.exit(1)
    
    print(f"=== Stock Price Prediction Test ===")
    print(f"Model: {model}")
    print(f"Cutoff Date: {cutoff_date}")
    print(f"Target Date: {target_date}")
    print(f"Tickers: {', '.join(tickers)}")
    print(f"Lookback Period: {lookback_days} days\n")
    
    # Run predictions for each ticker
    for ticker in tickers:
        print(f"\n--- Testing {ticker} ---")
        
        # Get historical context up to cutoff date
        print(f"Fetching historical data up to {cutoff_date}...")
        historical_context = stock_fetcher.get_historical_context(
            ticker, cutoff_date, lookback_days
        )
        
        if not historical_context:
            print(f"Warning: Could not fetch historical data for {ticker}")
            continue
        
        if verbose:
            print(f"Historical context: {json.dumps(historical_context, indent=2)}")
        
        # Get LLM prediction
        print(f"Getting LLM prediction for {target_date}...")
        prediction_result = llm_predictor.predict_stock_price(
            ticker, target_date, cutoff_date, historical_context
        )
        
        if not prediction_result['success']:
            print(f"Error getting prediction: {prediction_result.get('error', 'Unknown error')}")
            continue
        
        print(f"LLM Prediction: ${prediction_result['predicted_price']:.2f}")
        
        if verbose:
            print(f"\nFull LLM Response:\n{prediction_result['full_response']}\n")
        
        # Get actual price at target date
        print(f"Fetching actual price for {target_date}...")
        actual_price = stock_fetcher.get_price_at_date(ticker, target_date)
        
        if actual_price is None:
            print(f"Warning: Could not fetch actual price for {ticker} on {target_date}")
            continue
        
        print(f"Actual Price: ${actual_price:.2f}")
        
        # Evaluate prediction
        eval_result = evaluator.evaluate_prediction(
            prediction_result['predicted_price'],
            actual_price,
            ticker,
            target_date
        )
        
        if eval_result.get('valid', False):
            print(f"Absolute Error: ${eval_result['absolute_error']:.2f}")
            print(f"Percentage Error: {eval_result['percentage_error']:.2f}%")
    
    # Print summary
    print("\n" + "=" * 50)
    evaluator.print_results(verbose=verbose)
    print("=" * 50)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Test LLM stock price predictions with date-restricted information'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config.json',
        help='Path to configuration file (default: config.json)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Print verbose output'
    )
    
    args = parser.parse_args()
    
    config = load_config(args.config)
    run_stock_prediction_test(config, verbose=args.verbose)


if __name__ == '__main__':
    main()
