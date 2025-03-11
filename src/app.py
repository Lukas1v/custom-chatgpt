import os
import toml
import openai
import streamlit as st
from streamlit_chat import message
from pypdf import PdfReader
from vector_store import vectorStore

## Initialization
#load config
with open("src/config.toml", "r") as file:
    config = toml.load(file)

#set (Azure) openai details
openai.api_key = os.getenv("OPENAI_API_KEY")
if config["openai"]["api_type"] == "azure":
    openai.api_base = os.getenv("OPENAI_ENDPOINT") 
    openai.api_type = config["openai"]["api_type"]
    openai.api_version = config["openai"]["api_version"]


def get_pdf_prompt(document: str, ) -> str: 
    pdf_instructions = f"""
            You should answer questions using the document that is provided, the document is between '|||'                
            If you cannot find back the answer in the document, say you cannot find it back with the provided document.
            If you find an answer based on another source, add this as a disclaimer.
            If you are not sure about the answer, admit you are not sure.
            Document: ||| {document} |||
            Say thank you for this document and confirm you are ready for questions.
            """   
    prompt = {"role": "system", "content": pdf_instructions}
    return prompt

class chatBot():
    def __init__(self):

        #Azure openai model
        self.model_v35=config["openai"]["chatgpt3_model"]
        self.model_v40=config["openai"]["chatgpt4_model"]        

      self.msg_system = {"role": "system", "content": "You are a helpful assistant named Simon"}
        
        # Initialise streamlit and set page title
        st.set_page_config(page_title=config["page_title"], page_icon=":robot_face:")

        # Initialise state
        self.init_state()
        self.uploaded_files = None #placeholder

        # Setting  header and sidebar static properties
        st.markdown("<h1 style='text-align: center;'>" + config['title'] +" </h1>", unsafe_allow_html=True)
        st.sidebar.title("Sidebar")
        self.counter_placeholder = st.sidebar.empty()
                    
        # containers for chat history, text box and vector store
        self.response_container = st.container()  
        self.container = st.container()
        self.vector_store = None #placeholder


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
        st.session_state['total_tokens'] = []

    def set_model(self, model_name):
        if model_name == "GPT-3.5":
            model = self.model_v35
        else:
            model = self.model_v40 
        return model
    
    def clear(self):
        self.clear_state()
        self.counter_placeholder.write(f"Total cost of this conversation: €{st.session_state['total_cost']:.5f}")
      

    def fetch_sidebar_settings(self):        
        # let user choose model, show total cost of current conversation, and let user clear the current conversation  
        # self.counter_placeholder.write(f"Total cost of this conversation: €{st.session_state['total_cost']:.5f}")        

        # Map model names to Deployment id's, only 3.5 is available on Azure
        model_name = st.sidebar.radio("Choose a model:", ("o1", "o3 mini"))
        model = self.set_model(model_name)
        st.text("")
        #set temperature with slider
        temp_slider = st.sidebar.slider("Temperature", min_value=0.1, max_value=2.0, value=0.4, step=0.1)
        st.text("")

        return model_name, model, temp_slider
    

    def fetch_sidebar_files(self):   
        # files
        uploaded_files = st.sidebar.file_uploader(
                            "Upload files to be searched", 
                            type="pdf", 
                            accept_multiple_files=True)
        return uploaded_files        

  
    def fetch_main_input(self, model_name, temp_slider, model):
        user_input = st.chat_input("You:", key="input") 
        document = None 
              
        #process user_input
        if user_input is not None:
            prompt = user_input  

            #check if there is a vector store and if it contains docs
            if self.vector_store is not None:
                if self.vector_store.count_docs() > 0:
                    document = self.find_pdf_page(user_input)
                    # pdf_prompt = get_pdf_prompt(document)                     
            
            #process the prompt, enriched with pdf data if provided
            self.process_input(prompt, model, model_name, temp_slider, document)


    def process_input(self,user_prompt, model, model_name, temp_slider, document=None):
        if document is not None:
            #TODO
            pdf_total_tokens, pdf_prompt_tokens, pdf_completion_tokens = self.process_prompt(pdf_prompt, True, model, model_name, temp_slider)
        else:
            pdf_total_tokens, pdf_prompt_tokens, pdf_completion_tokens = 0,0,0

        user_total_tokens, user_prompt_tokens, user_completion_tokens = self.process_prompt(user_prompt, False, model, model_name, temp_slider)
 

    

    def process_prompt(self,prompt, system_prompt, model, model_name, temp_slider):
        output, total_tokens, prompt_tokens, completion_tokens = self.generate_response(prompt, system_prompt, model)
        st.session_state['past'].append(prompt)
        st.session_state['generated'].append(output)
        st.session_state['model_name'].append(model_name)
        st.session_state['total_tokens'].append(total_tokens)
        st.session_state['temperature'] = temp_slider

        return total_tokens, prompt_tokens, completion_tokens
    

    def generate_response(self, prompt, system_prompt, model):
        st.session_state['temperature']=0.4

        if system_prompt:
            st.session_state['messages'].append(prompt) #pdf prompt is a system prompt that has already been constructed #TODO align with user prompt that still has to be constructed
        else:
            st.session_state['messages'].append({"role": "user", "content": prompt})

        # print('debug prompt', st.session_state['messages'])
        completion = openai.ChatCompletion.create(
            model=model,
            messages=st.session_state['messages']
        )
        response = completion.choices[0].message.content
        st.session_state['messages'].append({"role": "assistant", "content": response})

        # print(st.session_state['messages'])
        total_tokens = completion.usage.total_tokens
        prompt_tokens = completion.usage.prompt_tokens
        completion_tokens = completion.usage.completion_tokens
        return response, total_tokens, prompt_tokens, completion_tokens

    
    def parse_files(self):
        #TODO: user smaller chunks than pages
        self.vector_store = vectorStore("test") #TODO: use UUID
        for pdf in self.uploaded_files:            
            reader = PdfReader(pdf)
            n_pages = len(reader.pages)
            for i in range(n_pages):
                doc_id = f"{pdf.name}-p{str(i)}"
                page = reader.pages[i]
                text = page.extract_text()
                self.vector_store.add_document(doc_id, text)
         

    def find_pdf_page(self, query: str):
        result = self.vector_store.query(query)
        return result['documents'][0][0]
    

    def update_chat(self):
        for i in range(len(st.session_state['generated'])):
            message(st.session_state["past"][i], is_user=True, key=str(i) + '_user')
            message(st.session_state["generated"][i], key=str(i))


    def run(self):
        ## Sidebar
        # fetch user settings from sidebar
        clear_button = st.sidebar.button("Clear Conversation", key="clear")  
        model_name, model, temp_slider = self.fetch_sidebar_settings()

         # process pdf content
        uploaded_files = self.fetch_sidebar_files()
        if isinstance(uploaded_files, list) and len(uploaded_files)>0:
            self.uploaded_files = uploaded_files
            # self.clear_state()            
            self.parse_files()

        # reset everything
        if clear_button:
            self.clear()
 
        ## Main screen
        # Collect prompt
        with self.container:            
            self.fetch_main_input(model_name, temp_slider, model)

        # display generated answer
        if st.session_state['generated']:
            with self.response_container:
                self.update_chat()
    


if __name__ == '__main__':
    cb = chatBot()
    cb.run()