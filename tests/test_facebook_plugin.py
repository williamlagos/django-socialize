"""Test FacebookSocialPlugin class."""

import json
import datetime
import unittest

from unittest.mock import patch
from socialize.integrations.facebook import FacebookSocialPlugin


class TestFacebookSocialPlugin(unittest.TestCase):
    """Test FacebookSocialPlugin class."""

    def setUp(self):
        self.token = 'fake_token'
        self.plugin = FacebookSocialPlugin(self.token)

    @patch('socialize.integrations.facebook.FacebookSocialPlugin.graph_request')
    def test_update_status(self, mock_graph_request):
        """Test update_status method."""
        mock_graph_request.return_value = json.dumps({'id': '12345'})
        response = self.plugin.update_status('Hello World')
        self.assertEqual(
            response, 'Published posting successfully on Facebook')
        mock_graph_request.assert_called_once_with(
            '/me/feed', {'message': 'Hello World'.encode('utf-8')})

    @patch('socialize.integrations.facebook.FacebookSocialPlugin.graph_request')
    def test_send_event(self, mock_graph_request):
        """Test send_event method."""
        mock_graph_request.return_value = json.dumps({'id': '12345'})
        response = self.plugin.send_event(
            'Event Name', '01/01/2023', 'Event Description', 'Event Location', 'http://ticket.uri')
        self.assertEqual(response, '12345')
        mock_graph_request.assert_called_once()

    @patch('socialize.integrations.facebook.FacebookSocialPlugin.graph_request')
    def test_send_event_cover(self, mock_graph_request):
        """Test send_event_cover method."""
        mock_graph_request.return_value = json.dumps({'id': '12345'})
        response = self.plugin.send_event_cover('12345', 'http://photo.url')
        self.assertEqual(
            response, 'Published image cover on event successfully on Facebook')
        mock_graph_request.assert_called_once_with(
            '12345', {'cover_url': 'http://photo.url'})

    def test_convert_datetime(self):
        """Test convert_datetime method."""
        date_str = '01/01/2023'
        expected_datetime = datetime.datetime(2023, 1, 1)
        result = self.plugin.convert_datetime(date_str)
        self.assertEqual(result, expected_datetime)
