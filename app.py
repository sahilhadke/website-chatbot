from rag import RAG
import os
from dotenv import load_dotenv

load_dotenv('.env')

website_url = "https://degrees.apps.asu.edu/masters-phd/major/ASU00/ESCOMSCMS/computer-science-ms"
question = "what is the deadline for fall semester?"

chatbot = RAG(website_url, os.getenv('GOOGLE_API_KEY'), "Website Single Page")
response = chatbot.get_response(question)
print(response)