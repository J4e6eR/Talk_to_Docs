# The frontend of the application written in streamlit
# import streamlit as st

import streamlit as st
import os
import app
import tokens

file_path = None
uploaded_file = None
file = os.getcwd()

def main():
    global file_path
    global uploaded_file

    # Uploading the file complete
    st.title("Talk to your Documents")
    file_path = file + '\\docs\\' + 'dummyfile.pdf'
    uploaded_file = st.file_uploader("Upload a document", type=["pdf", "docx", "txt"])
    if uploaded_file is not None:
        st.write("You uploaded:", uploaded_file.name)
        file_path = file +'\\docs\\' + str(uploaded_file.name)  
        with open(file_path, "wb") as temp_file:
            temp_file.write(uploaded_file.read())
        print("You uploaded the file", uploaded_file, 'file path = ', file_path)
    
     # Create a TextInput field
    input_value = st.text_input("Enter your query:", value="", key="text_input_field", help="Enter your input text here.")
    
    # Initializing the LLM model
    config={
  "access_token": f"{tokens.load_verified_token('GPT_ACCESS_TOKEN')}",
  "conversation_id": '34e32a56-66f7-4955-bd40-526f78937ee8',
}
    llm = app.model_init(config)
   
     # Passing the doc to slit it into chunks 
    docs = app.docsReader_PDF(file_path)
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

   
    
    summary = app.generate_output(input_value, llm)
    print("The summary generated", summary)

    # Display the input value
    st.write("AI model:", summary)
    print("You entered ", summary)

if __name__ == "__main__":
    main()
