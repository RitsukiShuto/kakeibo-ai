import pytest
from unittest.mock import patch, MagicMock
from src.output.slack_notifier import SlackNotifier
from src.models import AIAction
from slack_sdk.errors import SlackApiError

@pytest.fixture
def mock_env():
    with patch.dict('os.environ', {'SLACK_BOT_TOKEN': 'xoxb-fake', 'SLACK_USER_ID': 'U12345'}):
        yield

def test_slack_notifier_init(mock_env):
    notifier = SlackNotifier()
    assert notifier.bot_token == 'xoxb-fake'
    assert notifier.user_id == 'U12345'

def test_slack_notifier_init_no_token():
    with patch.dict('os.environ', {'SLACK_BOT_TOKEN': '', 'SLACK_USER_ID': ''}):
        notifier = SlackNotifier()
        assert notifier.client is None

@patch('src.output.slack_notifier.WebClient')
def test_send_notification_success(mock_webclient, mock_env):
    mock_client = MagicMock()
    mock_webclient.return_value = mock_client
    
    notifier = SlackNotifier()
    notifier.client = mock_client
    notifier.send_notification("Test Title", "Test Text")
    
    mock_client.chat_postMessage.assert_called_once()

@patch('src.output.slack_notifier.WebClient')
def test_send_notification_fail(mock_webclient, mock_env):
    mock_client = MagicMock()
    mock_client.chat_postMessage.side_effect = Exception("API Error")
    mock_webclient.return_value = mock_client
    
    notifier = SlackNotifier()
    notifier.client = mock_client
    notifier.send_notification("Test Title", "Test Text")

@patch('src.output.slack_notifier.WebClient')
def test_send_block_kit_success(mock_webclient, mock_env):
    mock_client = MagicMock()
    mock_client.chat_postMessage.return_value = {"ok": True}
    mock_webclient.return_value = mock_client
    
    notifier = SlackNotifier()
    notifier.client = mock_client
    actions = [AIAction(command="TEST", description="test action")]
    notifier.send_block_kit("Test Title", "Test Summary", actions, 80)
    
    mock_client.chat_postMessage.assert_called_once()

@patch('src.output.slack_notifier.WebClient')
def test_send_block_kit_slack_error(mock_webclient, mock_env):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.__getitem__.return_value = "invalid_auth"
    mock_client.chat_postMessage.side_effect = SlackApiError("Error", mock_response)
    mock_webclient.return_value = mock_client
    
    notifier = SlackNotifier()
    notifier.client = mock_client
    notifier.send_block_kit("Test Title", "Test Summary", [], 80)

@patch('src.output.slack_notifier.WebClient')
def test_send_block_kit_not_ok(mock_webclient, mock_env):
    mock_client = MagicMock()
    mock_client.chat_postMessage.return_value = {"ok": False, "error": "some_error"}
    mock_webclient.return_value = mock_client
    
    notifier = SlackNotifier()
    notifier.client = mock_client
    notifier.send_block_kit("Test Title", "Test Summary", [], 50)

@patch('src.output.slack_notifier.WebClient')
@patch('os.path.exists')
def test_upload_file_success(mock_exists, mock_webclient, mock_env):
    mock_exists.return_value = True
    mock_client = MagicMock()
    mock_client.files_upload_v2.return_value = {"ok": True}
    mock_webclient.return_value = mock_client
    
    notifier = SlackNotifier()
    notifier.client = mock_client
    notifier.upload_file("test.png", "Test Title")
    
    mock_client.files_upload_v2.assert_called_once()

@patch('os.path.exists')
def test_upload_file_not_found(mock_exists, mock_env):
    mock_exists.return_value = False
    notifier = SlackNotifier()
    notifier.upload_file("not_exist.png", "Title")

@patch('src.output.slack_notifier.WebClient')
@patch('os.path.exists')
def test_upload_file_api_error(mock_exists, mock_webclient, mock_env):
    mock_exists.return_value = True
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.__getitem__.return_value = "invalid_auth"
    mock_client.files_upload_v2.side_effect = SlackApiError("Error", mock_response)
    mock_webclient.return_value = mock_client
    
    notifier = SlackNotifier()
    notifier.client = mock_client
    notifier.upload_file("test.png", "Test Title")

@patch('src.output.slack_notifier.WebClient')
@patch('os.path.exists')
def test_upload_file_not_ok(mock_exists, mock_webclient, mock_env):
    mock_exists.return_value = True
    mock_client = MagicMock()
    mock_client.files_upload_v2.return_value = {"ok": False, "error": "some_error"}
    mock_webclient.return_value = mock_client
    
    notifier = SlackNotifier()
    notifier.client = mock_client
    notifier.upload_file("test.png", "Test Title")
