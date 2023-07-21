import os
import sys
import pytest
from pytest_mock import mocker

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
import pytest
import app
from app import chatBot

@pytest.fixture
def chatbot():
    return chatBot()


def test_init_state(mocker, chatbot):
    #streamlit mock
    mocker.patch('app.st.session_state')

    chatbot.init_state()

    #the following variables shoudl be set
    expected_calls = [
        mocker.call.__setitem__('generated', []),
        mocker.call.__setitem__('past', []),
        mocker.call.__setitem__('messages', [{"role": "system", "content": "You are a helpful assistant named Simon"}]),
        mocker.call.__setitem__('temperature', []),
        mocker.call.__setitem__('model_name', []),
        mocker.call.__setitem__('cost', []),
        mocker.call.__setitem__('total_tokens', []),
        mocker.call.__setitem__('total_cost', 0.0)

    ]

    app.st.session_state.__setitem__.assert_has_calls(expected_calls, any_order=True)


def test_set_model(chatbot):
    assert chatbot.set_model("GPT-3.5") == chatbot.engine_v35
    assert chatbot.set_model("GPT-4 (under development)") == chatbot.engine_v40






