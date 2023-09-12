# The frontend of the application written in streamlit
# import streamlit as st
# TODO: TO include the platform dependent implementation of ngrok and add asynchronous support for tunneling so we can handle streamlit responses  
# The filepath at 46 line is creating problem, will have to solve it.

import streamlit as st
import app
import tokens
from ngrok_ import async_tasks
from pathlib import Path
import os


file_path = None
uploaded_file = None
file = Path.cwd()

def main():
    print('Entered the main function')
    global file_path
    global uploaded_file

    # Uploading the file complete
    st.title("Talk to your Documents")
    uploaded_file = st.file_uploader("Upload a document", type=["pdf", "docx", "txt"])
    # file_path = file + '\\docs\\' + 'dummyfile.pdf'
    config={
            "access_token": f"{tokens.load_verified_token('GPT_ACCESS_TOKEN')}",
            "conversation_id": '34e32a56-66f7-4955-bd40-526f78937ee8',
    }
    llm = app.model_init(config)
    
    if uploaded_file is not None:
        st.write("You uploaded:", uploaded_file.name)
        folder_path = file / 'docs' 
        file_path =  folder_path / str(uploaded_file.name) 

        if os.path.exists(folder_path):
            print("The file path already exists")
        else:
            print('The file path does not exist and will be created using os.makedirs()')
            os.makedirs(folder_path)

        print("File path = ", file_path)

        with open(file_path, "wb") as temp_file:
            temp_file.write(uploaded_file.read())
        print("You uploaded the file", uploaded_file, 'file path = ', file_path)
                # Initializing the LLM model
    
        # Passing the doc to slit it into chunks 
        docs = app.docsReader_PDF(str(file_path))
        print("The docs successfully splitted into chunks ")
        # INitializing the embedding function
        embedding_function = app.embedding_model_init(model_name = "BAAI/bge-large-en",
                                                        model_kwargs = {'device': 'cpu'},
                                                        encode_kwargs = {'normalize_embeddings': True,},
                                                        cache_folder='.\\hugging_face_model\\')
        
        print("Embedding function initialized", embedding_function)

        # Converting the documents to vector store
        db = app.vector_store(docs, embedding_function, save_locally=True, persist_directory='.\chromadb')
        print("Convertomg the doc into vector store", db)

        # config={
        #     "access_token": f"{tokens.load_verified_token('GPT_ACCESS_TOKEN')}",
        #     "conversation_id": '34e32a56-66f7-4955-bd40-526f78937ee8',
        # }
        # llm = app.model_init(config)
        summary = app.generate_output(input_value,db, llm)
        print("The summary generated", summary)

        # Display the input value
        st.write("AI model:", summary)
        print("You entered ", summary)
    
    # Create a TextInput field
    input_value = st.text_input("Enter your query:", value="", key="text_input_field", help="Enter your input text here.")
        
    
    async_tasks()

if __name__ == "__main__":
    # Create a thread to run the Streamlit app
    # thread = threading.Thread(target=main)
    
    # Start the thread
    # thread.start()
    main()
