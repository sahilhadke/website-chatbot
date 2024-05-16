from rag import SingleWebPage
import os
from dotenv import load_dotenv

load_dotenv('.env')

website_url = "https://sahil.hadke.in/"
question = "Who is Sahil Hadke?"

chatbot = SingleWebPage(website_url, os.getenv('GOOGLE_API_KEY'))
response = chatbot.get_response(question)
print(response)