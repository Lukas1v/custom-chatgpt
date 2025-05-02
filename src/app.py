#sqlite fix for streamlit cloud
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import os
import re
import toml
import openai
import streamlit as st
from streamlit_chat import message
from pypdf import PdfReader
from vector_store import vectorStore

## Initialization
# Load config
with open("src/config.toml", "r") as file:
    config = toml.load(file)

# Initialize OpenAI client
client = openai.OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_ENDPOINT") if config["openai"].get("api_type") == "azure" else None
)

def get_pdf_prompt(document: str) -> dict:
    """
    Generates a system message instructing the chatbot to use the provided document for answering questions.
    """
    pdf_instructions = f"""
        You should answer questions using the document that is provided, the document is between '|||'
        If you cannot find back the answer in the document, say you cannot find it back with the provided document.
        If you find an answer based on another source, add this as a disclaimer.
        If you are not sure about the answer, admit you are not sure.
        Document: ||| {document} |||
        Say thank you for this document and confirm you are ready for questions.
    """
    return {"role": "system", "content": pdf_instructions}

class chatBot:
    def __init__(self):
        """
        Initializes the chatbot with configuration settings, Streamlit UI elements, and session states.
        """
        self.model_v35 = config["openai"]["chatgpt3_model"]
        self.model_v40 = config["openai"]["chatgpt4_model"]
        self.msg_system = {"role": "system", "content": "You are a helpful assistant named Simon"}

        # Set up Streamlit page
        st.set_page_config(page_title=config["page_title"], page_icon=":robot_face:")

        # Initialize session states
        self.init_state()
        self.uploaded_files = None

        # Set header and sidebar
        st.markdown(f"<h1 style='text-align: center;'>{config['title']}</h1>", unsafe_allow_html=True)
        st.sidebar.title("Sidebar")
        self.counter_placeholder = st.sidebar.empty()

        # Containers for UI elements
        self.response_container = st.container()
        self.container = st.container()
        self.vector_store = None  # Placeholder for document storage

    def init_state(self):
        """Initializes session state variables."""
        if 'generated' not in st.session_state:
            st.session_state['generated'] = []
        if 'past' not in st.session_state:
            st.session_state['past'] = []
        if 'messages' not in st.session_state:
            st.session_state['messages'] = [self.msg_system]
        if 'total_cost' not in st.session_state:
            st.session_state['total_cost'] = 0.0

    def clear_state(self):
        """Clears the session state variables."""
        st.session_state.update({
            'generated': [], 'past': [], 'messages': [self.msg_system], 'total_cost': 0.0
        })

    def set_model(self, model_name):
        """Returns the appropriate model based on user selection."""
        return self.model_v35 if model_name == "GPT-3.5" else self.model_v40

    def fetch_sidebar_settings(self):
        """Fetches user-selected model and temperature settings from the sidebar."""
        model_name = st.sidebar.radio("Choose a model:", (config["openai"]["chatgpt3_model"],config["openai"]["chatgpt4_model"]))
        model = self.set_model(model_name)
        temp_slider = st.sidebar.slider("Temperature", min_value=0.1, max_value=2.0, value=0.4, step=0.1)
        return model_name, model, temp_slider

    def fetch_sidebar_files(self):
        """Handles file uploads from the sidebar."""
        return st.sidebar.file_uploader("Upload files to be searched", type="pdf", accept_multiple_files=True)

    def fetch_main_input(self, model_name, temp_slider, model):
        """Processes user input from the main chat interface."""
        user_input = st.chat_input("You:", key="input")
        document = None
        if user_input:
            if self.vector_store and self.vector_store.count_docs() > 0:
                document = self.find_pdf_page(user_input)
            self.process_input(user_input, model, model_name, temp_slider, document)

    def process_input(self, user_prompt, model, model_name, temp_slider, document=None):
        """Processes user input and retrieves responses from OpenAI."""
        if document:
            pdf_prompt = get_pdf_prompt(document)
            self.process_prompt(pdf_prompt, True, model, model_name, temp_slider)
        self.process_prompt(user_prompt, False, model, model_name, temp_slider)

    def process_prompt(self, prompt, system_prompt, model, model_name, temp_slider):
        """Handles prompt processing and appends responses to session state."""
        output, total_tokens = self.generate_response(prompt, system_prompt, model)
        st.session_state['past'].append(prompt if not system_prompt else "System prompt")
        st.session_state['generated'].append(output)
        return total_tokens

    def generate_response(self, prompt, system_prompt, model):
        """Generates response using OpenAI API."""
        st.session_state['messages'].append(prompt if system_prompt else {"role": "user", "content": prompt})
        completion = client.chat.completions.create(
            model=model,
            messages=st.session_state['messages']
        )
        response = completion.choices[0].message.content

        #post processing of response
        if "```" not in response and "def " in response:  # crude heuristic for missing markdown
            response = f"```python\n{response.strip()}\n```"
        st.session_state['messages'].append({"role": "assistant", "content": response})

        return response, completion.usage.total_tokens

    def parse_files(self):
        """Processes uploaded PDF files and extracts text for vector search."""
        self.vector_store = vectorStore("test")
        for pdf in self.uploaded_files:
            reader = PdfReader(pdf)
            for i, page in enumerate(reader.pages):
                doc_id = f"{pdf.name}-p{i}"
                text = page.extract_text()
                self.vector_store.add_document(doc_id, text)

    def find_pdf_page(self, query: str):
        """Finds the relevant PDF page based on the query."""
        return self.vector_store.query(query)['documents'][0][0]

    def update_chat(self):
        """Updates the chat interface with past messages and responses using Streamlit's native chat_message."""
        for i in range(len(st.session_state['generated'])):
            with st.chat_message("user"):
                st.markdown(st.session_state["past"][i])
            with st.chat_message("assistant"):
                st.markdown(st.session_state["generated"][i])

    def run(self):
        """Runs the chatbot application."""
        clear_button = st.sidebar.button("Clear Conversation", key="clear")
        model_name, model, temp_slider = self.fetch_sidebar_settings()
        uploaded_files = self.fetch_sidebar_files()
        if uploaded_files:
            self.uploaded_files = uploaded_files
            self.parse_files()
        if clear_button:
            self.clear_state()
        with self.container:
            self.fetch_main_input(model_name, temp_slider, model)
        if st.session_state['generated']:
            with self.response_container:
                self.update_chat()

if __name__ == '__main__':
    cb = chatBot()
    cb.run()
