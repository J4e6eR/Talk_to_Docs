# Pay attention to Horovods, we can sue distributed GPU for infercing, worth a try
import torch, os
from transformers import GPT2Tokenizer, GPTJForCausalLM, Conversation, pipeline
from app import Timing, model_init, hugging_face_dir, chroma_db_dir,pdf_file_upload_location, file, generate_output, vector_load, vector_store, docsReader_PDF, embedding_model_init
import torch
from flask import Flask, request, redirect, send_from_directory
from pathlib import Path

app = Flask(__name__)

def process_file(embedding_function, pdf_name:str = 'pdf_.pdf',new_file: bool = False): 
    if new_file: return vector_store(docsReader_PDF(f'docs/{pdf_name}'), embedding_func, save_locally=True, persist_directory = str(chroma_db_dir))
    else: return vector_load(persist_directory=str(chroma_db_dir), embedding_function=embedding_function)

model_name = "/home/coeai/temporary/model"
def load_tokenizer(model_name: str = 'gpt2'):return GPT2Tokenizer.from_pretrained(model_name)
database = None

@app.route('/' ,methods=['GET', 'POST'])
def human_resp():
     global database
     if request.form.get('prompt'):
        if os.path.exists('docs') == False: os.mkdir(str(file / 'docs')) 
        if request.files.get('upload_file').filename == "": print("Processes without new file");database = process_file(embedding_func, request.files.get('upload_file').filename, new_file=False)
        else: request.files.get('upload_file').save(os.path.join(app.config['UPLOAD_FOLDER'], request.files.get('upload_file').filename)); database = process_file(embedding_func, request.files.get('upload_file').filename, new_file=True)
        return redirect(f'/response/{request.form.get("prompt")}', code=302)
     
     return '<form action="/" method="post" enctype="multipart/form-data">\
      <label for="prompt">Enter the prompt:</label>\
        <input type="text" id="prompt" name="prompt" required><br>\
      <label for="upload_file">Upload the file(Please check if the file is already uploaded or not on /show_uploaded_files):</label>\
        <input type="file" id="upload_file" name="upload_file">\
        <button type="submit">Upload</button>\
     </form>'

@app.route('/show_uploaded_files')
def show_uploaded_files():
    if os.path.exists('docs'): return f'<p>List of PDF files = {str(os.listdir("docs"))}</p>'
    else: return '<h1>There are no files to show</p>'

@app.route('/response/<prompt>' ,methods=['GET', 'POST'])
def machine_resp(prompt:str):
     global database
     with Timing("Inference completed"):
        if database:
            inference_ = generate_output(prompt, database=database, llm=model)
            print("INference =", inference_['choices'][0]['text'])
            # if inference_ : return f'<p>Machine: {inference_}</p>'  
            if inference_ : return f'<p>Machine: {inference_["choices"][0]["text"]}</p>'  


if __name__ == '__main__':
    app.config['UPLOAD_FOLDER'] = pdf_file_upload_location 
    torch.cuda.empty_cache()
    with Timing("Loading the embedding function: "):
        embedding_func = embedding_model_init(
        model_name="BAAI/bge-large-en",
        model_kwargs={'device': 'cuda'},
        encode_kwargs={'normalize_embeddings': True},
        cache_folder=str(hugging_face_dir)
    )
    with Timing("Loading the model: "):
        model = model_init(str(hugging_face_dir), using_hugging_face=False)
    app.run()
