import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium import webdriver
from selenium.webdriver.chrome.service import Service

class CreateChatBot:
    
    def __init__(self, url: str, google_api_key: str):
        print(f'CreateChatBot: {url}, {google_api_key}')
        self.url = url

        self.retriever = self.read_website() 

        llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=google_api_key)

        prompt = ChatPromptTemplate.from_template("""
        Act as a chatbot and answer questions about the website. Refer to the following context whenever possible
        <context>
        {context}
        </context>
        ---
        Question: {input}                                                                                                                 
        """)

        self.document_chain = create_stuff_documents_chain(llm, prompt)

    
    def read_website(self):
        print('read_website')


        driverPath = "/opt/homebrew/bin/chromedriver" # Path to ChromeDriver
        service = Service(driverPath)
        options = webdriver.ChromeOptions()

        options.add_argument('--headless')
        options.binary_location = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser" # Path to Brave Browser (this is the default)

        driver = webdriver.Chrome(service=service, options=options)

        # From here its Selenium as usual, example:
        driver.get(self.url)
        text = driver.find_element(By.TAG_NAME, "body").text
        print(text, file=open("text.txt", "w"))
        driver.close()

        # print(html_page)

        loader = TextLoader("text.txt")

        text_documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        # print(f'text_documents = {text_documents}')
        documents = text_splitter.split_documents(text_documents)
        # print(f'documents = {documents}')
        db = FAISS.from_documents(documents, HuggingFaceEmbeddings())
        # print(f'db = {db}')
        retriever = db.as_retriever()
        # print(f'retriever = {retriever}')
        return retriever
        

    def get_response(self, question: str):
        retrieval_chain = create_retrieval_chain(self.retriever, self.document_chain)
        result = retrieval_chain.invoke({"input": question})
        # print(f'get_response = {question}, {result}')
        return result['answer']
