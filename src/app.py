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
        self.engine_v35='gpt-4o-mini'
        self.engine_v40='gpt-4o-mini'
        self.msg_system = {"role": "system", "content": "You are a helpful assistant named Simon"}
        
        # Initialise streamlit and set page title
        st.set_page_config(page_title="LVE Chatbot", page_icon=":robot_face:")

        # Initialise state
        self.init_state()

        # Setting  header and sidebar static properties
        st.markdown("<h1 style='text-align: center;'> LVE Custom ChatGPT </h1>", unsafe_allow_html=True)
        st.sidebar.title("Sidebar")
        self.counter_placeholder = st.sidebar.empty()
                    
        # containers for chat history and text box
        self.response_container = st.container()  
        self.container = st.container()


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
        if 'temperature' not in st.session_state:
            st.session_state['temperature'] = []
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
        ]
        st.session_state['temperature'] = []
        st.session_state['number_tokens'] = []
        st.session_state['model_name'] = []
        st.session_state['cost'] = []
        st.session_state['total_cost'] = 0.0
        st.session_state['total_tokens'] = []

    def set_model(self, model_name):
        if model_name == "GPT-3.5":
            engine = self.engine_v35
        else:
            engine = self.engine_v40 
        return engine
    
    def clear(self):
        self.clear_state()
        self.counter_placeholder.write(f"Total cost of this conversation: €{st.session_state['total_cost']:.5f}")
    
    
    def generate_response(self,prompt, engine):
        st.session_state['temperature']=0.4
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
    

    def fetch_sidebar_input(self):        
        # let user choose model, show total cost of current conversation, and let user clear the current conversation  
        self.counter_placeholder.write(f"Total cost of this conversation: €{st.session_state['total_cost']:.5f}")        

        # Map model names to Deployment id's, only 3.5 is available on Azure
        model_name = st.sidebar.radio("Choose a model:", ("GPT-3.5", "GPT-4 (under development)"))
        engine = self.set_model(model_name)
        st.text("")
        #set temperature with slider
        temp_slider = st.sidebar.slider("Temperature", min_value=0.1, max_value=2.0, value=0.4, step=0.1)
        st.text("")
        # files
        uploaded_files = st.sidebar.file_uploader(
            'Upload files to be searched', 
            type="pdf", 
            accept_multiple_files=True)
        if uploaded_files is not None:
            pass

        return model_name, engine, temp_slider
    
   
    def fetch_main_input(self, model_name, temp_slider, engine):
        user_input = st.chat_input("You:", key='input')
        if user_input:
            output, total_tokens, prompt_tokens, completion_tokens = self.generate_response(user_input, engine)
            st.session_state['past'].append(user_input)
            st.session_state['generated'].append(output)
            st.session_state['model_name'].append(model_name)
            st.session_state['total_tokens'].append(total_tokens)
            st.session_state['temperature'] = temp_slider

            # from https://openai.com/pricing#language-models
            if model_name == "GPT-3.5":
                cost = total_tokens * 0.001835 / 1000
            else:
                cost = (prompt_tokens * 0.028 + completion_tokens * 0.056) / 1000
            st.session_state['cost'].append(cost)
            st.session_state['total_cost'] += cost


    def update_chat(self):
        for i in range(len(st.session_state['generated'])):
            message(st.session_state["past"][i], is_user=True, key=str(i) + '_user')
            message(st.session_state["generated"][i], key=str(i))


    def run(self):
        ## Sidebar
        # fetch user input from sidebar
        clear_button = st.sidebar.button("Clear Conversation", key="clear")  
        model_name, engine, temp_slider = self.fetch_sidebar_input()

        # reset everything
        if clear_button:
            self.clear()
 
        ## Main screen
        # Collect prompt
        with self.container:            
            self.fetch_main_input(model_name, temp_slider, engine)

        # display generated answer
        if st.session_state['generated']:
            with self.response_container:
                self.update_chat()
    


if __name__ == '__main__':
    cb = chatBot()
    cb.run()