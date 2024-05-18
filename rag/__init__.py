import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.document_loaders import UnstructuredHTMLLoader
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
import faiss

import logging




from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By

from utils import scrape_site
from transformers import AutoTokenizer, AutoModel
from bs4 import BeautifulSoup
import torch

import numpy as np


# Enable logging for debugging
logging.basicConfig(level=logging.INFO)

class RAG:
    
    def __init__(self, url: str, google_api_key: str, resource_type: str="Website Single Page", recursive_count: int=5):

        self.current_status = "idle"

        self.recursive_count = recursive_count

        self.url = url

        if(resource_type == "Website Single Page"):
            self.retriever = self.read_website() 

        if(resource_type == "Website Multiple Pages"):
            self.retriever = self.read_website_recursive()

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
        
        options = Options()

        options.add_argument('--headless')

        driver = webdriver.Firefox(options=options)

        # From here its Selenium as usual, example:
        driver.get(self.url)

        text_html = driver.page_source
        
        # extract body text
        text = driver.find_element(By.TAG_NAME, "body").text

        with open("page.html", "w") as file:
            file.write(text_html)

        driver.close()

        loader = UnstructuredHTMLLoader('page.html')
        # load the text from variable
        # loader = Document(page_content=text, metadata={"source": self.url})

        # Split the text
        text_documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        documents = text_splitter.split_documents(text_documents)

        # documents = [Document(page_content="Raymond Brownell was a senior officer in the Royal Australian Air Force and a World War I flying ace", metadata={"source": "https://en.wikipedia.org/wiki/Raymond_Brownell"})]

        # Create and fill the FAISS index
        try:
            embedder = HuggingFaceEmbeddings()
        except Exception as e:
            logging.error(f"Failed to initialize embeddings model: {e}")
        
        db = FAISS.from_documents(documents, embedder)

        # Setup the retriever
        retriever = db.as_retriever()
        # faiss.write_index(retriever.index, "index.faiss")
        # print(f'retriever = {retriever}')
        return retriever
    
    def read_website_recursive(self):
        
        options = Options()
        options.add_argument('--headless')
        driver = webdriver.Firefox(options=options)


        data = scrape_site(driver, self.url)
        # print(f'data = {data}')

        def html_to_text(html_content):
            soup = BeautifulSoup(html_content, 'html.parser')
            return soup.get_text()


        documents = []
        for url, html_content in data.items():
            for url, html_content in data.items():
                text_content = html_to_text(html_content)
                doc = Document(page_content=text_content, metadata={"source": url})
                documents.append(doc)


        try:
            logging.info("Initializing HuggingFace Embeddings model...")      
            embeddings_model = HuggingFaceEmbeddings(force_download=True)
            logging.info("Model initialized successfully.")
        except Exception as e:
            logging.error(f"Failed to initialize embeddings model: {e}")
            raise
        # Initialize the HuggingFace Embeddings

        # Convert documents to embeddings
        texts = [doc.text for doc in documents]
        embeddings = embeddings_model.embed_documents(texts)

        # Create a FAISS index and add embeddings
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings)

        metadata = list(data.keys())
        with open('metadata.txt', 'w') as f:
            for item in metadata:
                f.write(f"{item}\n")

        faiss_retriever = FAISS(index=index, metadata=metadata, embeddings=embeddings_model)

        return faiss_retriever

        
        
        

    def get_response(self, question: str):
        retrieval_chain = create_retrieval_chain(self.retriever, self.document_chain)
        result = retrieval_chain.invoke({"input": question})
        # print(f'get_response = {question}, {result}')
        return result['answer']