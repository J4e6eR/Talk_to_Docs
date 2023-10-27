# # The frontend of the application written in streamlit
# # TODO: Refactor the code for better experience

import streamlit as st
import app
import tokens
from pathlib import Path
import os

uploaded_file = None
file = Path.cwd()
hugging_face_dir = file / 'hugging_face_models'
chroma_db_dir = file / 'chroma_db_embed'

def main():
    st.title("Talk to Docs")
    st.sidebar.header("Options")
    
    process_new_file = st.sidebar.button("Process New File")
    process_with_url = st.sidebar.button("Process New File with URL")
    process_existing_file = st.sidebar.button("Process Existing File")

    if process_new_file:
        upload_file()

    if process_with_url:
        upload_file_with_url()

    if process_existing_file:
        process_existing_files()

def upload_file():
    global uploaded_file
    st.header("Upload a Document")
    uploaded_file = st.file_uploader("Upload a document", type=["pdf", "docx", "txt"])
    
    if uploaded_file:
        pdf_name = uploaded_file.name
        st.write(f"Uploaded file: {pdf_name}")
        embedding_func, db = embedding_function_init(pdf_name, uploaded_file)
        
        if embedding_func and db:
            prompt = st.text_input("Enter your query:")
            if prompt:
                llm = init_summarization_model()
                gen_summary(prompt, db, llm, 'c6f6fb09-6981-48c9-b4a8-2c77822fc691')


def process_file(embedding_function):
    return app.vector_load(persist_directory=str(chroma_db_dir), embedding_function=embedding_function)

def upload_file_with_url():
    st.header("Upload a Document via URL")
    input_value = st.text_input("Enter the URL of the pdf file")
    pdf_name = st.text_input("Enter the name of the pdf file:")
    
    if input_value and pdf_name:
        embedding_func, db = embedding_function_init(pdf_name, None, url=input_value)

        if embedding_func and db:
            prompt = st.text_input("Enter your query:")
            if prompt:
                llm = init_summarization_model()
                gen_summary(prompt, db, llm, 'c6f6fb09-6981-48c9-b4a8-2c77822fc691')

def process_existing_files():
    st.header("Process Existing Files")
    if os.path.exists('docs'):
        st.write("List of all files: ", os.listdir('docs'))
    process_file()

def embedding_function_init(pdf_name:str = 'pdf_.pdf', uploaded_file=None, url=None, load_vector = False):
    embedding_func = app.embedding_model_init(
        model_name="BAAI/bge-large-en",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True},
        cache_folder=str(hugging_face_dir)
    )

    
    if url:
        app.download_file(url=url, fp=f'docs/{pdf_name}')
    elif uploaded_file:
        pdf_path = f'docs/{pdf_name}'
        with open(pdf_path, 'wb') as file:
            file.write(uploaded_file.read())

    docs = app.docsReader_PDF(f'docs/{pdf_name}')
    if load_vector:
        db = app.vector_load(str(chroma_db_dir), embedding_func)
    else:
        db = app.vector_store(docs, embedding_func, save_locally=True, persist_directory = str(chroma_db_dir))
    return embedding_func, db

def gen_summary(input_value, db, llm, conversation_id=None):
    if input_value:
        summary = app.generate_output(input_value, db, llm, conversation_id=conversation_id)
        st.subheader("Generated Text:")
        st.write("AI model:", summary)

def init_summarization_model():
    return app.model_init(access_token=tokens.load_verified_token('GPT_ACCESS_TOKEN'))

if __name__ == "__main__":
    main()
