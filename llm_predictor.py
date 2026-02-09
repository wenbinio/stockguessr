"""
LLM interaction module for stock price predictions.
Handles communication with LLM APIs with date-restricted information.
Supports multiple providers: OpenAI, Anthropic (Claude), and OpenAI-compatible APIs.
"""

import os
from typing import Optional, Dict, Any
from datetime import datetime
from openai import OpenAI
import anthropic

# Provider constants
PROVIDER_OPENAI = "openai"
PROVIDER_ANTHROPIC = "anthropic"

# Default environment variable names per provider
DEFAULT_ENV_VARS = {
    PROVIDER_OPENAI: "OPENAI_API_KEY",
    PROVIDER_ANTHROPIC: "ANTHROPIC_API_KEY",
}

# Default models per provider
DEFAULT_MODELS = {
    PROVIDER_OPENAI: "gpt-3.5-turbo",
    PROVIDER_ANTHROPIC: "claude-sonnet-4-20250514",
}


class LLMPredictor:
    """Handles LLM-based stock price predictions with date restrictions."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        provider: str = PROVIDER_OPENAI,
        api_base_url: Optional[str] = None,
        api_key_env_var: Optional[str] = None,
    ):
        """
        Initialize the LLM predictor.
        
        Args:
            api_key: API key (uses env var if not provided)
            model: Model to use for predictions (defaults per provider)
            provider: LLM provider - "openai", "anthropic", or any OpenAI-compatible provider
            api_base_url: Custom API base URL (for OpenAI-compatible APIs)
            api_key_env_var: Environment variable name for the API key
        """
        self.provider = provider.lower()
        self.model = model or DEFAULT_MODELS.get(self.provider, "gpt-3.5-turbo")
        self.api_base_url = api_base_url
        
        # Resolve API key
        env_var = api_key_env_var or DEFAULT_ENV_VARS.get(self.provider, "OPENAI_API_KEY")
        self.api_key = api_key or os.getenv(env_var)
        if not self.api_key:
            raise ValueError(
                f"API key not provided and {env_var} env var not set. "
                f"Provider: {self.provider}"
            )
        
        # Initialize the appropriate client
        if self.provider == PROVIDER_ANTHROPIC:
            self.client = anthropic.Anthropic(api_key=self.api_key)
        else:
            client_kwargs = {"api_key": self.api_key}
            if self.api_base_url:
                client_kwargs["base_url"] = self.api_base_url
            self.client = OpenAI(**client_kwargs)
    
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
        system_message = (
            f"You are a financial analyst. Today's date is {cutoff_date}. "
            f"You have no knowledge of events after {cutoff_date}. "
            f"Provide stock price predictions based only on information available up to {cutoff_date}."
        )
        
        try:
            if self.provider == PROVIDER_ANTHROPIC:
                prediction_text = self._call_anthropic(system_message, prompt)
            else:
                prediction_text = self._call_openai(system_message, prompt)
            
            # Try to extract a numerical prediction
            predicted_price = self._extract_price_from_response(prediction_text)
            
            return {
                'ticker': ticker,
                'target_date': target_date,
                'cutoff_date': cutoff_date,
                'predicted_price': predicted_price,
                'full_response': prediction_text,
                'model': self.model,
                'provider': self.provider,
                'success': predicted_price is not None
            }
            
        except Exception as e:
            return {
                'ticker': ticker,
                'target_date': target_date,
                'cutoff_date': cutoff_date,
                'predicted_price': None,
                'error': str(e),
                'model': self.model,
                'provider': self.provider,
                'success': False
            }
    
    def _call_openai(self, system_message: str, user_prompt: str) -> str:
        """Call OpenAI or OpenAI-compatible API."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            max_tokens=500,
        )
        return response.choices[0].message.content
    
    def _call_anthropic(self, system_message: str, user_prompt: str) -> str:
        """Call Anthropic Claude API."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            system=system_message,
            messages=[
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.content[0].text
    
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
