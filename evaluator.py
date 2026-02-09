"""
Evaluation module for comparing LLM predictions to actual stock prices.
"""

from typing import Dict, Any, List
import statistics


class StockPredictionEvaluator:
    """Evaluates LLM stock price predictions against actual prices."""
    
    def __init__(self):
        """Initialize the evaluator."""
        self.results = []
    
    def evaluate_prediction(
        self,
        predicted_price: float,
        actual_price: float,
        ticker: str,
        target_date: str
    ) -> Dict[str, Any]:
        """
        Evaluate a single prediction.
        
        Args:
            predicted_price: LLM's predicted price
            actual_price: Actual closing price
            ticker: Stock ticker symbol
            target_date: Date of prediction
            
        Returns:
            Dictionary with evaluation metrics
        """
        if predicted_price is None or actual_price is None:
            return {
                'ticker': ticker,
                'target_date': target_date,
                'error': 'Missing price data',
                'valid': False
            }
        
        # Calculate error metrics
        absolute_error = abs(predicted_price - actual_price)
        percentage_error = (absolute_error / actual_price) * 100
        
        result = {
            'ticker': ticker,
            'target_date': target_date,
            'predicted_price': predicted_price,
            'actual_price': actual_price,
            'absolute_error': absolute_error,
            'percentage_error': percentage_error,
            'valid': True
        }
        
        self.results.append(result)
        return result
    
    def get_summary_statistics(self) -> Dict[str, Any]:
        """
        Get summary statistics for all evaluations.
        
        Returns:
            Dictionary with summary metrics
        """
        if not self.results:
            return {'error': 'No valid results to summarize'}
        
        valid_results = [r for r in self.results if r.get('valid', False)]
        
        if not valid_results:
            return {'error': 'No valid results to summarize'}
        
        absolute_errors = [r['absolute_error'] for r in valid_results]
        percentage_errors = [r['percentage_error'] for r in valid_results]
        
        return {
            'num_predictions': len(valid_results),
            'mean_absolute_error': statistics.mean(absolute_errors),
            'median_absolute_error': statistics.median(absolute_errors),
            'mean_percentage_error': statistics.mean(percentage_errors),
            'median_percentage_error': statistics.median(percentage_errors),
            'min_percentage_error': min(percentage_errors),
            'max_percentage_error': max(percentage_errors),
            'std_percentage_error': statistics.stdev(percentage_errors) if len(percentage_errors) > 1 else 0
        }
    
    def print_results(self, verbose: bool = False):
        """
        Print evaluation results.
        
        Args:
            verbose: If True, print detailed results for each prediction
        """
        if verbose:
            print("\n=== Detailed Results ===")
            for result in self.results:
                if result.get('valid', False):
                    print(f"\n{result['ticker']} on {result['target_date']}:")
                    print(f"  Predicted: ${result['predicted_price']:.2f}")
                    print(f"  Actual: ${result['actual_price']:.2f}")
                    print(f"  Error: ${result['absolute_error']:.2f} ({result['percentage_error']:.2f}%)")
        
        print("\n=== Summary Statistics ===")
        summary = self.get_summary_statistics()
        
        if 'error' in summary:
            print(f"Error: {summary['error']}")
            return
        
        print(f"Number of predictions: {summary['num_predictions']}")
        print(f"Mean Absolute Error: ${summary['mean_absolute_error']:.2f}")
        print(f"Median Absolute Error: ${summary['median_absolute_error']:.2f}")
        print(f"Mean Percentage Error: {summary['mean_percentage_error']:.2f}%")
        print(f"Median Percentage Error: {summary['median_percentage_error']:.2f}%")
        print(f"Min Percentage Error: {summary['min_percentage_error']:.2f}%")
        print(f"Max Percentage Error: {summary['max_percentage_error']:.2f}%")
        if summary['num_predictions'] > 1:
            print(f"Std Dev Percentage Error: {summary['std_percentage_error']:.2f}%")
