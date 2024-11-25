import pytest
from unittest.mock import patch, MagicMock
import os
import tempfile
from prepare_commit_msg_gen.cli import get_staged_diff, generate_commit_message, main
from langchain_core.messages import AIMessage

@pytest.fixture
def mock_llm():
    mock = MagicMock()
    mock.invoke.return_value = AIMessage(content="feat(auth): add user authentication")

    with patch('prepare_commit_msg_gen.cli.get_llm_client', return_value=mock):
        yield mock

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

def test_get_llm_client_openai():
    with patch.dict(os.environ, {
        "PREPARE_COMMIT_MSG_GEN_LLM_PROVIDER": "openai",
        "PREPARE_COMMIT_MSG_GEN_LLM_MODEL": "gpt-4o",
        "OPENAI_API_KEY": "test-key"
    }):
        from prepare_commit_msg_gen.cli import get_llm_client
        from langchain_openai import ChatOpenAI

        llm = get_llm_client()
        assert isinstance(llm, ChatOpenAI)
        assert llm.model_name == "gpt-4o"
        assert llm.temperature == 0.1

def test_get_llm_client_ollama_default():
    with patch.dict(os.environ, {
        "PREPARE_COMMIT_MSG_GEN_LLM_PROVIDER": "ollama",
    }):
        from prepare_commit_msg_gen.cli import get_llm_client
        from langchain_ollama import ChatOllama

        llm = get_llm_client()
        assert isinstance(llm, ChatOllama)
        assert llm.model == "qwen2.5-coder:7b"
        assert llm.temperature == 0.1
        assert llm.base_url == "http://localhost:11434"

def test_get_llm_client_ollama_custom():
    with patch.dict(os.environ, {
        "PREPARE_COMMIT_MSG_GEN_LLM_PROVIDER": "ollama",
        "PREPARE_COMMIT_MSG_GEN_LLM_MODEL": "llama2",
        "PREPARE_COMMIT_MSG_GEN_OLLAMA_BASE_URL": "http://custom-server:11434"
    }):
        from prepare_commit_msg_gen.cli import get_llm_client
        from langchain_ollama import ChatOllama

        llm = get_llm_client()
        assert isinstance(llm, ChatOllama)
        assert llm.model == "llama2"
        assert llm.temperature == 0.1
        assert llm.base_url == "http://custom-server:11434"

def test_get_llm_client_anthropic_default():
    with patch.dict(os.environ, {
        "PREPARE_COMMIT_MSG_GEN_LLM_PROVIDER": "anthropic",
        "ANTHROPIC_API_KEY": "test-key"
    }):
        from prepare_commit_msg_gen.cli import get_llm_client
        from langchain_anthropic import ChatAnthropic

        llm = get_llm_client()
        assert isinstance(llm, ChatAnthropic)
        assert llm.model == "claude-3-5-sonnet-latest"
        assert llm.temperature == 0.1

def test_get_llm_client_anthropic_custom():
    with patch.dict(os.environ, {
        "PREPARE_COMMIT_MSG_GEN_LLM_PROVIDER": "anthropic",
        "PREPARE_COMMIT_MSG_GEN_LLM_MODEL": "claude-3-opus-20240229",
        "ANTHROPIC_API_KEY": "test-key"
    }):
        from prepare_commit_msg_gen.cli import get_llm_client
        from langchain_anthropic import ChatAnthropic

        llm = get_llm_client()
        assert isinstance(llm, ChatAnthropic)
        assert llm.model == "claude-3-opus-20240229"
        assert llm.temperature == 0.1

def test_get_llm_client_invalid_provider():
    with patch.dict(os.environ, {"PREPARE_COMMIT_MSG_GEN_LLM_PROVIDER": "invalid", "OPENAI_API_KEY": "test-key"}):
        from prepare_commit_msg_gen.cli import get_llm_client
        with pytest.raises(ValueError) as exc_info:
            get_llm_client()
        assert str(exc_info.value) == "Unsupported LLM provider: invalid"

def test_generate_commit_message_success(mock_llm):
    diff = 'diff --git a/auth.py b/auth.py\n+def authenticate_user():'
    message = generate_commit_message(diff)
    assert message == "feat(auth): add user authentication"
    mock_llm.invoke.assert_called_once()

def test_generate_commit_message_error(mock_llm):
    mock_llm.invoke.side_effect = Exception("API Error")
    message = generate_commit_message("some diff")
    assert message is None

def test_main_success(mock_llm, temp_commit_msg_file):
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

def test_main_failed_message_generation(mock_llm, temp_commit_msg_file):
    with patch('sys.argv', ['script', temp_commit_msg_file]), \
         patch('prepare_commit_msg_gen.cli.get_staged_diff') as mock_get_diff:
        mock_get_diff.return_value = "some diff"
        mock_llm.invoke.side_effect = Exception("API Error")

        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1

def test_main_nonexistent_commit_msg_file(mock_llm):
    with patch('sys.argv', ['script', '/nonexistent/file']), \
         patch('prepare_commit_msg_gen.cli.get_staged_diff') as mock_get_diff:
        mock_get_diff.return_value = "some diff"

        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1
