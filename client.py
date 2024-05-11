import streamlit as st
from chatbot import CreateChatBot
import os
from dotenv import load_dotenv

load_dotenv('.env')

def main():
    st.title('Website RAG')

    website_url = st.text_input('Enter URL')
    question = st.text_area('Enter your question')
    api_key = st.text_input('Enter API Key')

    if(st.button('Submit')):
        st.write('Fetching response...')
        if(api_key == ''):
            api_key = os.getenv('GOOGLE_API_KEY')
        chatbot = CreateChatBot(website_url, api_key)
        response = chatbot.get_response(question)
        st.write(response)

if __name__ == '__main__':
    main()