# TODO: How can we get database from the uploaded file

from langchain.document_loaders import PyPDFLoader
from langchain.llms.huggingface_pipeline import HuggingFacePipeline
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.embeddings import HuggingFaceBgeEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores.chroma  import Chroma
from llama_cpp import Llama
# from customLLM import CustomLLM, Role_type
# from frontend import uploaded_file
import tokens, app, tempfile, tqdm, contextlib, time
import os
from pathlib import Path

file = Path.cwd()
hugging_face_dir = file / 'hugging_face_models'
chroma_db_dir = file / 'chroma_db_embed'
pdf_file_upload_location = file / 'docs'
os.environ['TRANSFORMERS_CACHE'] = str(hugging_face_dir)

# loader = PyPDFLoader("https://arxiv.org/pdf/2303.18223.pdf")
# documents = loader.load_and_split()

# for i in range(len(pages)):
#     print(pages[i].page_content)

# print("Pages = ", len(pages))

import contextlib, time

class Timing(contextlib.ContextDecorator):
  def __init__(self, prefix="", on_exit=None, enabled=True): self.prefix, self.on_exit, self.enabled = prefix, on_exit, enabled
  def __enter__(self): self.st = time.perf_counter_ns()
  def __exit__(self, *exc):
    self.et = time.perf_counter_ns() - self.st
    if self.enabled: print(f"{self.prefix}{self.et*1e-6:.2f} ms"+(self.on_exit(self.et) if self.on_exit else ""))




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
    return HuggingFaceBgeEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs,
    cache_folder= cache_folder
)

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
                ): return Chroma(persist_directory=persist_directory, embedding_function=embedding_function)

# Initialises the model
def model_init(model_path: str, device_:str = 'cuda', using_hugging_face:bool = True):

    if device_ == 'cuda' :device_ = 0
    else: device_ = -1
    if using_hugging_face:
      return HuggingFacePipeline.from_model_id(
        model_id="facebook/bart-large-cnn",
        task="summarization",
        device = device_,
        pipeline_kwargs={"max_new_tokens": 200},
    )
    else:
       check_model_download() 
       return Llama(model_path="/workspace/tmp/Talk_to_Docs/hugging_face_models/phi_2/phi-2.Q5_K_M.gguf", n_gpu_layers=30, n_ctx=2048)

# Checks whether the model is downloaded or not and downlaods if not
def check_model_download(model_path: str = str(file / 'hugging_face_models/phi_2')):
   if os.path.exists(model_path): pass
   else : 
      print('Downlaoding the file')
      os.mkdir(model_path)
      download_file("https://huggingface.co/TheBloke/phi-2-GGUF/resolve/main/phi-2.Q5_K_M.gguf", model_path + '/phi-2.Q5_K_M.gguf')
  #  download_file()

# Generates the very output but in unformatted manner.
def generate_output(query:str, database, llm, conversation_id: str = None):
    print("Query =", query)
    prompt = database.similarity_search(query=query)
    print("Prompt = ", prompt)
    return llm(prompt[0].page_content + '\n Give me a summary in context to the question and print only the summary\n' + query, max_tokens = 1000) #We wil have to think of a better option to pick out relevant documents instead of the very first one

# Can enable downloading for teh pdfs from any website
def download_file(url, fp, skip_if_exists=True):
  import requests, os, pathlib
  if skip_if_exists and os.path.isfile(fp) and os.stat(fp).st_size > 0:
    return
  r = requests.get(url, stream=True)
  assert r.status_code == 200
  # progress_bar = tqdm(total=int(r.headers.get('content-length', 0)), unit='B', unit_scale=True, desc=url)
  print("Parent =", pathlib.Path(fp).parent)
  with tempfile.NamedTemporaryFile(dir=pathlib.Path(fp).parent, delete=False) as f:
    for chunk in r.iter_content(chunk_size=16384):
      f.write(chunk)
    f.close()
    os.rename(f.name, fp)

# if __name__ == '__main__' and uploaded_file:
    
    
#     print("The llm is initialized")

    