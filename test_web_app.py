import unittest
from unittest.mock import patch

from web_app import app, calculate_score


class TestWebApp(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_calculate_score_bounds(self):
        self.assertEqual(calculate_score(100.0, 100.0), 5000)
        self.assertEqual(calculate_score(300.0, 100.0), 1)

    def test_index_get_renders_form(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Market Cap Challenge", response.data)

    @patch('web_app.get_stock_game_data')
    def test_post_displays_score(self, mock_get_stock_game_data):
        mock_get_stock_game_data.return_value = ({
            'price_at_date': 120.0,
            'actual_market_cap': 1_000_000_000.0,
            'actual_market_cap_display': '$1.00B',
            'related_prices': {'1 day before': 119.0},
            'context': {
                'latest_close': 120.0,
                'average_close': 118.0,
                'high': 125.0,
                'low': 110.0,
                'price_change_pct': 5.0,
            },
        }, None)

        response = self.client.post('/', data={
            'ticker': 'AAPL',
            'target_date': '2024-01-02',
            'guess_market_cap': '950000000',
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Score:", response.data)
        self.assertIn(b"Stock price on 2024-01-02", response.data)


if __name__ == '__main__':
    unittest.main()
