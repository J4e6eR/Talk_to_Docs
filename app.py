from langchain.document_loaders import PyPDFLoader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.embeddings import HuggingFaceBgeEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores  import Chroma
# from customLLM import CustomLLM, MyHandler
from customLLM import CustomLLM, Role_type
from frontend import file_path, uploaded_file
import tokens
import app

# loader = PyPDFLoader("https://arxiv.org/pdf/2303.18223.pdf")
# documents = loader.load_and_split()

# for i in range(len(pages)):
#     print(pages[i].page_content)

# print("Pages = ", len(pages))






# vector_store = Chroma(persist_directory='.\chromadb', embedding_function=embedding_func)
# query = "Which is most recent LLM"

# response = vector_store.similarity_search(query=query)
# print("Vectorstore = ", vector_store)
# print("Response =", response)


# print("Pages =",pages[0].page_content)

def docsReader_PDF(file_location_url:str):
    loader = PyPDFLoader(file_location_url)
    documents = loader.load_and_split()

    #Splitting the text characterwise  
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    docs = text_splitter.split_documents(documents)
    return docs

# Embedding model from HuggingFace. Currently only hugging face model is supported.
def embedding_model_init(model_name:str,
                         model_kwargs:dict,
                         encode_kwargs:dict,
                         cache_folder:str
                         ):
    embedding_func = HuggingFaceBgeEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs,
    cache_folder= cache_folder
)
    return embedding_func

# Convert the documents to vector store and save them locally on chroma db
def vector_store(docs,
                 embedding_function : HuggingFaceBgeEmbeddings = None, 
                 save_locally :bool = False, 
                 persist_directory :str = None,
                 ):
    
    db = Chroma.from_documents(docs, embedding=embedding_function, persist_directory=persist_directory)
    if save_locally:
        print("TO BE SAVED LOCALLY")
        db.persist()
    print("Vector embeddings =", db)
    return db

# load already existing vector store.
def vector_load(persist_directory :str,
                embedding_function :HuggingFaceBgeEmbeddings, 
                ):
    data_base = Chroma(persist_directory=persist_directory, embedding_function=embedding_function)
    return data_base

# Initialises the model
def model_init(access_token: str):
    # The model should be initialized at the start of the session
    llm = CustomLLM(access_token= access_token)
    return llm


# Generates the very output but in unformatted manner.
def generate_output(query:str, database, llm, conversation_id: str = None):
    print("Query =", query)
    prompt = database.similarity_search(query=query)
    print("Prompt = ", prompt)
    question ="'temperature 0.01' \n" + prompt[0].page_content + '\n Give me a summary in context to the question and print only the summary\n' + query #We wil have to think of a better option to pick out relevant documents instead of the very first one
    # llm = model_init(config)
    llm._call(prompt=question,role=Role_type.USER.value, conversation_id=conversation_id)
    
    # The output needs to be formatted as it would include a lot of information of no use to the User
    return llm.response['message'] 


# if __name__ == '__main__' and uploaded_file:
    
    
#     print("The llm is initialized")

    