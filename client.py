import streamlit as st
from rag import SingleWebPage
from dotenv import load_dotenv
from streamlit.components.v1 import html

load_dotenv('.env')

if 'data_load' not in st.session_state:
    st.session_state['data_load'] = False

if 'chatbot' not in st.session_state:
    st.session_state['chatbot'] = None

st.title("Website RAG")

# website and api key input fields
website_url = st.text_input("Enter website URL")
api_key = st.text_input("Enter Google API Key")

if(st.button("Load")):
    st.session_state['chatbot'] = SingleWebPage(website_url, api_key)
    st.session_state['data_load'] = True
    st.success("Data loaded successfully")

if(st.session_state['data_load']):
    question = st.text_input("Enter question")
    if(st.button("Get Answer")):
        response = st.session_state['chatbot'].get_response(question)
        st.write(response)
