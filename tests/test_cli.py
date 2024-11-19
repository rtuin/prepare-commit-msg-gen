import pytest
from unittest.mock import patch, MagicMock
import os
import tempfile
from prepare_commit_msg_gen.cli import get_staged_diff, generate_commit_message, main

@pytest.fixture
def mock_openai_client():
    mock_client = MagicMock()
    mock_completion = MagicMock()
    mock_completion.choices = [
        MagicMock(message=MagicMock(content="feat(auth): add user authentication"))
    ]
    mock_client.chat.completions.create.return_value = mock_completion
    
    with patch('prepare_commit_msg_gen.cli.get_openai_client', return_value=mock_client):
        yield mock_client

@pytest.fixture
def temp_commit_msg_file():
    with tempfile.NamedTemporaryFile(delete=False) as f:
        yield f.name
    os.unlink(f.name)

def test_get_staged_diff_empty():
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(stdout=b'')
        diff = get_staged_diff()
        assert diff == ''
        mock_run.assert_called_once_with(['git', 'diff', '--cached'], stdout=-1)

def test_get_staged_diff_with_changes():
    mock_diff = b'diff --git a/test.py b/test.py\nindex 1234567..890abcd 100644\n--- a/test.py\n+++ b/test.py\n@@ -1,1 +1,2 @@\n+print("test")'
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(stdout=mock_diff)
        diff = get_staged_diff()
        assert diff == mock_diff.decode('utf-8')

def test_generate_commit_message_success(mock_openai_client):
    diff = 'diff --git a/auth.py b/auth.py\n+def authenticate_user():'
    message = generate_commit_message(diff)
    assert message == "feat(auth): add user authentication"
    mock_openai_client.chat.completions.create.assert_called_once()

def test_generate_commit_message_error(mock_openai_client):
    mock_openai_client.chat.completions.create.side_effect = Exception("API Error")
    message = generate_commit_message("some diff")
    assert message is None

def test_main_success(mock_openai_client, temp_commit_msg_file):
    with patch('sys.argv', ['script', temp_commit_msg_file]), \
         patch('prepare_commit_msg_gen.cli.get_staged_diff') as mock_get_diff:
        mock_get_diff.return_value = "some diff"
        assert main() == 0

        with open(temp_commit_msg_file, 'r') as f:
            content = f.read()
            assert content == "feat(auth): add user authentication"

def test_main_no_staged_changes():
    with patch('sys.argv', ['script', 'dummy_file']), \
         patch('prepare_commit_msg_gen.cli.get_staged_diff') as mock_get_diff:
        mock_get_diff.return_value = ""
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0

def test_main_merge_commit():
    with patch('sys.argv', ['script', 'dummy_file', 'merge']):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0

def test_main_invalid_args():
    with patch('sys.argv', ['script']):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1

def test_main_failed_message_generation(mock_openai_client, temp_commit_msg_file):
    with patch('sys.argv', ['script', temp_commit_msg_file]), \
         patch('prepare_commit_msg_gen.cli.get_staged_diff') as mock_get_diff:
        mock_get_diff.return_value = "some diff"
        mock_openai_client.chat.completions.create.side_effect = Exception("API Error")

        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1

def test_main_nonexistent_commit_msg_file(mock_openai_client):
    with patch('sys.argv', ['script', '/nonexistent/file']), \
         patch('prepare_commit_msg_gen.cli.get_staged_diff') as mock_get_diff:
        mock_get_diff.return_value = "some diff"

        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1
