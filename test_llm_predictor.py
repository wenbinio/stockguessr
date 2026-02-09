"""
Tests for the LLM predictor module with multi-provider support.
"""

import os
import unittest
from unittest.mock import patch, MagicMock

from llm_predictor import LLMPredictor, PROVIDER_OPENAI, PROVIDER_ANTHROPIC


class TestLLMPredictorInit(unittest.TestCase):
    """Test LLMPredictor initialization for different providers."""

    def test_openai_provider_default(self):
        predictor = LLMPredictor(api_key="test-key")
        self.assertEqual(predictor.provider, "openai")
        self.assertEqual(predictor.model, "gpt-3.5-turbo")

    def test_openai_provider_explicit(self):
        predictor = LLMPredictor(api_key="test-key", provider="openai", model="gpt-4")
        self.assertEqual(predictor.provider, "openai")
        self.assertEqual(predictor.model, "gpt-4")

    def test_anthropic_provider(self):
        predictor = LLMPredictor(api_key="test-key", provider="anthropic")
        self.assertEqual(predictor.provider, "anthropic")
        self.assertEqual(predictor.model, "claude-sonnet-4-20250514")

    def test_anthropic_provider_custom_model(self):
        predictor = LLMPredictor(api_key="test-key", provider="anthropic", model="claude-opus-4-20250514")
        self.assertEqual(predictor.model, "claude-opus-4-20250514")

    def test_custom_provider_with_base_url(self):
        predictor = LLMPredictor(
            api_key="test-key",
            provider="custom",
            model="local-model",
            api_base_url="http://localhost:8000/v1",
        )
        self.assertEqual(predictor.provider, "custom")
        self.assertEqual(predictor.api_base_url, "http://localhost:8000/v1")
        self.assertEqual(predictor.model, "local-model")

    def test_env_var_openai(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "env-key"}):
            predictor = LLMPredictor(provider="openai")
            self.assertEqual(predictor.api_key, "env-key")

    def test_env_var_anthropic(self):
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "env-key"}):
            predictor = LLMPredictor(provider="anthropic")
            self.assertEqual(predictor.api_key, "env-key")

    def test_custom_env_var(self):
        with patch.dict(os.environ, {"MY_CUSTOM_KEY": "custom-key"}):
            predictor = LLMPredictor(provider="openai", api_key_env_var="MY_CUSTOM_KEY")
            self.assertEqual(predictor.api_key, "custom-key")

    def test_missing_api_key_raises_error(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError) as ctx:
                LLMPredictor(provider="anthropic")
            self.assertIn("ANTHROPIC_API_KEY", str(ctx.exception))

    def test_provider_case_insensitive(self):
        predictor = LLMPredictor(api_key="test-key", provider="OpenAI")
        self.assertEqual(predictor.provider, "openai")


class TestLLMPredictorPredict(unittest.TestCase):
    """Test predict_stock_price for different providers."""

    def setUp(self):
        self.historical_context = {
            "latest_close": 185.50,
            "average_close": 180.25,
            "high": 195.00,
            "low": 170.00,
            "volatility": 5.25,
            "price_change_pct": 8.5,
        }

    @patch("llm_predictor.OpenAI")
    def test_openai_predict(self, mock_openai_cls):
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Predicted Price: $190.00"
        mock_client.chat.completions.create.return_value = mock_response

        predictor = LLMPredictor(api_key="test-key", provider="openai")
        result = predictor.predict_stock_price(
            "AAPL", "2024-06-01", "2024-01-01", self.historical_context
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["predicted_price"], 190.00)
        self.assertEqual(result["provider"], "openai")
        mock_client.chat.completions.create.assert_called_once()

    @patch("llm_predictor.anthropic")
    def test_anthropic_predict(self, mock_anthropic_mod):
        mock_client = MagicMock()
        mock_anthropic_mod.Anthropic.return_value = mock_client
        mock_response = MagicMock()
        mock_response.content = [MagicMock()]
        mock_response.content[0].text = "Predicted Price: $192.50"
        mock_client.messages.create.return_value = mock_response

        predictor = LLMPredictor(api_key="test-key", provider="anthropic")
        result = predictor.predict_stock_price(
            "AAPL", "2024-06-01", "2024-01-01", self.historical_context
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["predicted_price"], 192.50)
        self.assertEqual(result["provider"], "anthropic")
        mock_client.messages.create.assert_called_once()

    @patch("llm_predictor.OpenAI")
    def test_predict_api_error(self, mock_openai_cls):
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API error")

        predictor = LLMPredictor(api_key="test-key", provider="openai")
        result = predictor.predict_stock_price(
            "AAPL", "2024-06-01", "2024-01-01", self.historical_context
        )

        self.assertFalse(result["success"])
        self.assertIn("API error", result["error"])

    @patch("llm_predictor.OpenAI")
    def test_predict_result_metadata(self, mock_openai_cls):
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Predicted Price: $200.00"
        mock_client.chat.completions.create.return_value = mock_response

        predictor = LLMPredictor(api_key="test-key", provider="openai", model="gpt-4")
        result = predictor.predict_stock_price(
            "MSFT", "2024-06-01", "2024-01-01", self.historical_context
        )

        self.assertEqual(result["ticker"], "MSFT")
        self.assertEqual(result["target_date"], "2024-06-01")
        self.assertEqual(result["cutoff_date"], "2024-01-01")
        self.assertEqual(result["model"], "gpt-4")
        self.assertEqual(result["provider"], "openai")


class TestPriceExtraction(unittest.TestCase):
    """Test price extraction from various LLM response formats."""

    def setUp(self):
        self.predictor = LLMPredictor(api_key="test-key", provider="openai")

    def test_extract_standard_format(self):
        self.assertEqual(
            self.predictor._extract_price_from_response("Predicted Price: $190.50"),
            190.50,
        )

    def test_extract_with_comma(self):
        self.assertEqual(
            self.predictor._extract_price_from_response("Predicted Price: $1,234.56"),
            1234.56,
        )

    def test_extract_dollar_sign(self):
        self.assertEqual(
            self.predictor._extract_price_from_response("I think the price will be $185.00"),
            185.00,
        )

    def test_extract_no_price(self):
        self.assertIsNone(
            self.predictor._extract_price_from_response("I cannot make a prediction")
        )


if __name__ == "__main__":
    unittest.main()
