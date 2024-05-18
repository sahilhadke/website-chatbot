import streamlit as st
from rag import RAG
from dotenv import load_dotenv
from streamlit.components.v1 import html

if 'data_loaded' not in st.session_state:
    st.session_state['data_loaded'] = False

if 'resource_processor' not in st.session_state:
    st.session_state['resource_processor'] = None

st.title("Resource Augmented Generation (RAG)")

# Dropdown to choose the type of RAG
resource_type = st.selectbox(
    
    "Select Resource Type",
    ("Website Single Page", "Website Multiple Pages", "PDF File", "DOC File", "CSV File")
)

# Conditional input fields based on the selected resource type
if resource_type == "Website Single Page" or resource_type == "Website Multiple Pages":
    website_url = st.text_input("Enter website URL")
    api_key = st.text_input("Enter Google API Key")
    if st.button("Load Website"):
        st.session_state['resource_processor'] = RAG(website_url, api_key)
        st.session_state['data_loaded'] = True
        st.success("Website data loaded successfully")

elif resource_type == "PDF File" or resource_type == "DOC File" or resource_type == "CSV File":
    file_upload = st.file_uploader("Upload File", type=["pdf", "doc", "docx", "csv"])
    if file_upload is not None and st.button("Load File"):
        # Assuming you have some method to handle these files
        # You might need a different approach or handler for files than for web pages
        # st.session_state['resource_processor'] = FileProcessor(file_upload)
        st.session_state['data_loaded'] = True
        st.success(f"{resource_type.split(' ')[0]} loaded successfully")

# Handling questions or queries based on the loaded data
if st.session_state['data_loaded']:
    question = st.text_input("Enter your question")
    if st.button("Get Answer"):
        if st.session_state['resource_processor']:
            response = st.session_state['resource_processor'].get_response(question)
            st.write(response)
        else:
            st.error("No resource processor available.")