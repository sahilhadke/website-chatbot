import streamlit as st
from rag import SingleWebPage
import os
from dotenv import load_dotenv
from streamlit.components.v1 import html

load_dotenv('.env')

def main():
    st.title('Website RAG')

    website_url = st.text_input('Enter URL')
    question = st.text_area('Enter your question')
    api_key = st.text_input('Enter API Key')
    progress_text = st.empty()

    if(st.button('Get Answer')):

        if(api_key == ''):
            st.error('Please enter a valid API Key')
            return
        if(website_url == ''):
            st.error('Please enter a valid URL')
            return
        if(question == ''):
            st.error('Please enter a valid question')
            return

        progress_text.write(f'Fetching data from {website_url} and storing to vectordb')
        chatbot = SingleWebPage(website_url, api_key)
        progress_text.write(f'Using LLM to query the vectordb for the question: {question}')
        response = chatbot.get_response(question)
        progress_text.write(f'Answer: {response}')

if __name__ == '__main__':
    main()