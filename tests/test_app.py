import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from pytest_mock import mocker
import pytest
import app
from app import chatBot

@pytest.fixture
def chatbot():
    return chatBot()


### initialization tests
def test_init_vars(chatbot):  
    ''' test initialization of the variables''' 
    #types
    assert isinstance(chatbot.engine_v35, str)
    assert isinstance(chatbot.engine_v40, str)
    assert isinstance(chatbot.msg_system, dict)
    #msg_system should have the following keys
    assert 'role' in chatbot.msg_system, "msg_system should have the 'role' key"
    assert 'content' in chatbot.msg_system, "msg_system should have the 'content' key"

def test_init_st(mocker):
    ''' test initialization streamlit components'''
    #patch streamlit   
    mocker.patch('app.st')
    cb = chatBot()     

    assert app.st.set_page_config.called_once(), "set_page_config should be called to set page_title"
    assert app.st.markdown.called_once(), "markdown should be called to display title"
    assert app.st.sidebar.title.called_once(), "sidebar.title should set"
    assert app.st.sidebar.empty.called_once(), "sidebar empty container as placeholder for costs"
    assert app.st.container.call_count == 2, "containers for chat history and text box"

def test_init_state_called(mocker, chatbot):
    ''' test if init_state was called during initialization '''
    mocker.patch.object(chatbot, 'init_state')
    assert chatbot.init_state.called_once()
 
def test_init_state(mocker, chatbot):
    ''' test if all vars were reset during initialization'''    
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


### chat tests
def test_clear(mocker, chatbot):
    ''' clear should call clear_state'''
    mocker.patch.object(chatbot, 'clear')
    mocker.patch.object(chatbot, 'clear_state')

    chatbot.clear()
    assert chatbot.clear_state.called_once()

def clear_state(mocker, chatbot):
    #streamlit mock
    mocker.patch('app.st.session_state')
    chatbot.clear_state()

    #the following variables should be cleared
    expected_calls = [
        mocker.call.__setitem__('generated', []),
        mocker.call.__setitem__('past', []),
        mocker.call.__setitem__('messages', [{"role": "system", "content": "You are a helpful assistant named Simon"}]),
        mocker.call.__setitem__('temperature', []),
        mocker.call.__setitem__('model_name', []),
        mocker.call.__setitem__('cost', []),
        mocker.call.__setitem__('total_tokens', []),
        mocker.call.__setitem__('total_cost', 0.0),
        mocker.call.__setitem__('number_tokens', [])
    ]
    app.st.session_state.__setitem__.assert_has_calls(expected_calls, any_order=True)



