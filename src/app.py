import os
import openai
import streamlit as st
from streamlit_chat import message

## Initialization
#Azure openai details
openai.api_type = "azure"
openai.api_base = os.getenv("OPENAI_ENDPOINT") 
openai.api_version = "2023-05-15"
openai.api_key = os.getenv("OPENAI_API_KEY")


class chatBot():
    def __init__(self):
        #Azure openai engine
        self.engine_v35='custom-chatgpt-model'
        self.engine_v40='custom-chatgpt-model'
        self.msg_system = {"role": "system", "content": "You are a assistant named Simon who only talks about cycling"}
        
        # Initialise streamlit and set page title
        st.set_page_config(page_title="LVE Chatbot", page_icon=":robot_face:")

        # Initialise state
        self.init_state()

        # Setting  header and sidebar static properties
        st.markdown("<h1 style='text-align: center;'>AIncompetence </h1>", unsafe_allow_html=True)
        st.sidebar.title("Sidebar")
        self.counter_placeholder = st.sidebar.empty()


    def init_state(self):
        # Initialise session state variables
        if 'generated' not in st.session_state:
            st.session_state['generated'] = []
        if 'past' not in st.session_state:
            st.session_state['past'] = []
        if 'messages' not in st.session_state:
            st.session_state['messages'] = [
                self.msg_system
            ]
        if 'model_name' not in st.session_state:
            st.session_state['model_name'] = []
        if 'cost' not in st.session_state:
            st.session_state['cost'] = []
        if 'total_tokens' not in st.session_state:
            st.session_state['total_tokens'] = []
        if 'total_cost' not in st.session_state:
            st.session_state['total_cost'] = 0.0




    def clear_state(self):
        st.session_state['generated'] = []
        st.session_state['past'] = []
        st.session_state['messages'] = [
            self.msg_system
            # {"role": "system", "content": "You are a helpful assistant."}
        ]
        st.session_state['number_tokens'] = []
        st.session_state['model_name'] = []
        st.session_state['cost'] = []
        st.session_state['total_cost'] = 0.0
        st.session_state['total_tokens'] = []

    def set_model(self, model_name):
        if model_name == "GPT-3.5":
            engine = self.engine_v35
        else:
            engine = self.engine_v35 
        return engine
    
    def clear(self):
        self.clear_state
        self.counter_placeholder.write(f"Total cost of this conversation: ${st.session_state['total_cost']:.5f}")
    
    
    def generate_response(self,prompt, engine):
        st.session_state['messages'].append({"role": "user", "content": prompt})

        completion = openai.ChatCompletion.create(
            engine=engine,
            messages=st.session_state['messages']
        )
        response = completion.choices[0].message.content
        st.session_state['messages'].append({"role": "assistant", "content": response})

        # print(st.session_state['messages'])
        total_tokens = completion.usage.total_tokens
        prompt_tokens = completion.usage.prompt_tokens
        completion_tokens = completion.usage.completion_tokens
        return response, total_tokens, prompt_tokens, completion_tokens
    

    def run(self):
        # ## Sidebar
        # let user choose model, show total cost of current conversation, and let user clear the current conversation     
        self.counter_placeholder.write(f"Total cost of this conversation: ${st.session_state['total_cost']:.5f}")
        clear_button = st.sidebar.button("Clear Conversation", key="clear")

        # Map model names to Deployment id's, only 3.5 is available on Azure
        model_name = st.sidebar.radio("Choose a model:", ("GPT-3.5", "GPT-4 (under development)"))
        engine = self.set_model(model_name)

        # reset everything
        if clear_button:
            self.clear()

        # container for chat history and text box
        container = st.container()
        response_container = st.container()  

        with container:
            with st.form(key='my_form', clear_on_submit=True):
                user_input = st.text_area("You:", key='input', height=100)
                submit_button = st.form_submit_button(label='Send')

            #submit with enter: https://discuss.streamlit.io/t/capture-enter-key-press-event-in-text-input/5862/3
            if submit_button and user_input:
                output, total_tokens, prompt_tokens, completion_tokens = self.generate_response(user_input, engine)
                st.session_state['past'].append(user_input)
                st.session_state['generated'].append(output)
                st.session_state['model_name'].append(model_name)
                st.session_state['total_tokens'].append(total_tokens)

                # from https://openai.com/pricing#language-models
                if model_name == "GPT-3.5":
                    cost = total_tokens * 0.002 / 1000
                else:
                    cost = (prompt_tokens * 0.03 + completion_tokens * 0.06) / 1000

                st.session_state['cost'].append(cost)
                st.session_state['total_cost'] += cost

        if st.session_state['generated']:
            with response_container:
                for i in range(len(st.session_state['generated'])):
                    message(st.session_state["past"][i], is_user=True, key=str(i) + '_user')
                    message(st.session_state["generated"][i], key=str(i))
                    st.write(
                        f"Model used: {st.session_state['model_name'][i]}; Number of tokens: {st.session_state['total_tokens'][i]}; Cost: ${st.session_state['cost'][i]:.5f}")
                    self.counter_placeholder.write(f"Total cost of this conversation: ${st.session_state['total_cost']:.5f}")


if __name__ == '__main__':
    cb = chatBot()
    cb.run()