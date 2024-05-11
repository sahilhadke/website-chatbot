import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain

from selenium.webdriver.common.by import By

from selenium import webdriver
from selenium.webdriver.firefox.options import Options


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
        
        options = Options()

        options.add_argument('--headless')

        driver = webdriver.Firefox(options=options)

        # From here its Selenium as usual, example:
        driver.get(self.url)

        # get body text
        elem = driver.find_element(By.TAG_NAME, 'body')

        text = elem.text

        with open("text.txt", "w") as file:
            file.write(text)

        driver.close()

        loader = TextLoader('text.txt')

        # Split the text
        text_documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        documents = text_splitter.split_documents(text_documents)

        # Create and fill the FAISS index
        embedder = HuggingFaceEmbeddings()
        db = FAISS.from_documents(documents, embedder)

        # Setup the retriever
        retriever = db.as_retriever()
        # faiss.write_index(retriever.index, "index.faiss")
        # print(f'retriever = {retriever}')
        return retriever
        

    def get_response(self, question: str):
        retrieval_chain = create_retrieval_chain(self.retriever, self.document_chain)
        result = retrieval_chain.invoke({"input": question})
        # print(f'get_response = {question}, {result}')
        return result['answer']
