import pytest
from unittest.mock import patch, MagicMock
from src.output.slack_server import handle_review_command, handle_action_done, start_slack_server

def test_handle_review_command():
    mock_ack = MagicMock()
    mock_respond = MagicMock()
    command = {"user_id": "U123", "text": "monthly skip"}
    
    with patch('src.output.slack_server.threading.Thread') as mock_thread:
        handle_review_command(mock_ack, command, mock_respond, None)
        
        mock_ack.assert_called_once()
        mock_respond.assert_called_once()
        assert "monthly" in mock_respond.call_args[0][0]
        assert "スキップ" in mock_respond.call_args[0][0]
        mock_thread.assert_called_once()
        mock_thread.return_value.start.assert_called_once()

def test_handle_review_command_others():
    mock_ack = MagicMock()
    mock_respond = MagicMock()
    
    with patch('src.output.slack_server.threading.Thread'):
        handle_review_command(mock_ack, {"user_id": "U", "text": "y"}, mock_respond, None)
        assert "yearly" in mock_respond.call_args[0][0]
        
        mock_respond.reset_mock()
        handle_review_command(mock_ack, {"user_id": "U", "text": "q"}, mock_respond, None)
        assert "quarterly" in mock_respond.call_args[0][0]
        
        mock_respond.reset_mock()
        handle_review_command(mock_ack, {"user_id": "U", "text": ""}, mock_respond, None)
        assert "weekly" in mock_respond.call_args[0][0]

@patch('src.output.slack_server.app')
def test_handle_action_done(mock_app):
    mock_ack = MagicMock()
    mock_logger = MagicMock()
    body = {
        "user": {"id": "U123"},
        "actions": [{"value": "TEST: desc"}]
    }
    
    handle_action_done(mock_ack, body, mock_logger)
    
    mock_ack.assert_called_once()
    mock_app.client.chat_postMessage.assert_called_once()

@patch('src.output.slack_server.SocketModeHandler')
def test_start_slack_server(mock_handler):
    mock_instance = MagicMock()
    mock_handler.return_value = mock_instance
    with patch('src.output.slack_server.SLACK_APP_TOKEN', 'xapp-123'):
        start_slack_server()
        mock_instance.start.assert_called_once()

def test_start_slack_server_no_token():
    with patch('src.output.slack_server.SLACK_APP_TOKEN', None):
        start_slack_server()
    with patch('src.output.slack_server.SLACK_APP_TOKEN', ''):
        start_slack_server()
