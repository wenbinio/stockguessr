"""
LLM interaction module for stock price predictions.
Handles communication with LLM APIs with date-restricted information.
"""

import os
from typing import Optional, Dict, Any
from datetime import datetime
from openai import OpenAI


class LLMPredictor:
    """Handles LLM-based stock price predictions with date restrictions."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """
        Initialize the LLM predictor.
        
        Args:
            api_key: OpenAI API key (uses env var if not provided)
            model: Model to use for predictions
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key not provided and OPENAI_API_KEY env var not set")
        
        self.model = model
        self.client = OpenAI(api_key=self.api_key)
    
    def predict_stock_price(
        self,
        ticker: str,
        target_date: str,
        cutoff_date: str,
        historical_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Predict stock price using LLM with information restricted to cutoff date.
        
        Args:
            ticker: Stock ticker symbol
            target_date: Date to predict price for
            cutoff_date: Information cutoff date (LLM can only use data before this)
            historical_context: Historical data up to cutoff date
            
        Returns:
            Dictionary with prediction and metadata
        """
        # Create the prompt with date restriction
        prompt = self._create_prediction_prompt(
            ticker, target_date, cutoff_date, historical_context
        )
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a financial analyst. Today's date is {cutoff_date}. "
                                   f"You have no knowledge of events after {cutoff_date}. "
                                   f"Provide stock price predictions based only on information available up to {cutoff_date}."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            prediction_text = response.choices[0].message.content
            
            # Try to extract a numerical prediction
            predicted_price = self._extract_price_from_response(prediction_text)
            
            return {
                'ticker': ticker,
                'target_date': target_date,
                'cutoff_date': cutoff_date,
                'predicted_price': predicted_price,
                'full_response': prediction_text,
                'model': self.model,
                'success': predicted_price is not None
            }
            
        except Exception as e:
            return {
                'ticker': ticker,
                'target_date': target_date,
                'cutoff_date': cutoff_date,
                'predicted_price': None,
                'error': str(e),
                'success': False
            }
    
    def _create_prediction_prompt(
        self,
        ticker: str,
        target_date: str,
        cutoff_date: str,
        historical_context: Dict[str, Any]
    ) -> str:
        """Create a prompt for the LLM to predict stock price."""
        context_str = f"""
Based on the following historical data for {ticker} (as of {cutoff_date}):
- Current price: ${historical_context.get('latest_close', 'N/A'):.2f}
- 90-day average: ${historical_context.get('average_close', 'N/A'):.2f}
- 90-day high: ${historical_context.get('high', 'N/A'):.2f}
- 90-day low: ${historical_context.get('low', 'N/A'):.2f}
- Price change (90 days): {historical_context.get('price_change_pct', 'N/A'):.2f}%
- Volatility (std dev): ${historical_context.get('volatility', 'N/A'):.2f}

Predict the closing price for {ticker} on {target_date}.

Important: Remember that today is {cutoff_date}. You should not use any information from after {cutoff_date}.

Please provide:
1. Your predicted price (provide a specific number)
2. Brief reasoning for your prediction

Format your price prediction clearly as: "Predicted Price: $XXX.XX"
"""
        return context_str
    
    def _extract_price_from_response(self, response_text: str) -> Optional[float]:
        """
        Extract numerical price from LLM response.
        
        Args:
            response_text: The LLM's response text
            
        Returns:
            Extracted price or None if not found
        """
        import re
        
        # Look for patterns like "Predicted Price: $123.45" or "$123.45"
        patterns = [
            r'Predicted Price:\s*\$?([\d,]+\.?\d*)',
            r'prediction.*?\$?([\d,]+\.?\d*)',
            r'\$\s*([\d,]+\.?\d*)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response_text, re.IGNORECASE)
            if match:
                try:
                    price_str = match.group(1).replace(',', '')
                    return float(price_str)
                except (ValueError, IndexError):
                    continue
        
        return None
