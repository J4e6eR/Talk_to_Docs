# Pay attention to Horovods, we can sue distributed GPU for infercing, worth a try
import torch
from transformers import GPT2Tokenizer, GPTJForCausalLM, Conversation, pipeline
from timing import Timing
import torch
from flask import Flask, request, redirect
from pathlib import Path
import app

app = Flask(__name__)
file = Path.cwd()
hugging_face_dir = file / 'hugging_face_models'
chroma_db_dir = file / 'chroma_db_embed'

# Used for embedding function initialization
def embedding_function_init(pdf_name:str = 'pdf_.pdf', uploaded_file=None, url=None, load_vector = False):
    embedding_func = app.embedding_model_init(
        model_name="BAAI/bge-large-en",
        model_kwargs={'device': 'cuda'},
        encode_kwargs={'normalize_embeddings': True},
        cache_folder=str(hugging_face_dir)
    )

    if url: app.download_file(url=url, fp=f'docs/{pdf_name}')
    elif uploaded_file:
        with open(f'docs/{pdf_name}', 'wb') as file: file.write(uploaded_file.read())

    docs = app.docsReader_PDF(f'docs/{pdf_name}')
    if load_vector: db = app.vector_load(str(chroma_db_dir), embedding_func)
    else: db = app.vector_store(docs, embedding_func, save_locally=True, persist_directory = str(chroma_db_dir))
    return embedding_func, db

model_name = "/home/coeai/temporary/model"
def load_tokenizer(model_name: str = 'gpt2'):return GPT2Tokenizer.from_pretrained(model_name)
def load_model(model_name_or_path :str , device: str): return GPTJForCausalLM.from_pretrained(pretrained_model_name_or_path = model_name_or_path, cache_dir = model_name_or_path, pad_token_id=tokenizer.eos_token_id).to(torch.device(device)) 

def inference(tokenizer, model, prompt):
    try:
        tokenizer.pad_token = tokenizer.eos_token
        gen_tokens = model.generate(tokenizer([prompt], return_tensors="pt", padding=True).input_ids, do_sample=True, temperature=0.9, max_length=100,)        
        return tokenizer.batch_decode(gen_tokens)[0]
    except Exception as e: print("The exception is", e); return f'<p>{e}</p>'

def gen_summary(input_value, db, llm, conversation_id=None):
    if input_value: return f'{"AI model: " + str(app.generate_output(input_value, db, llm, conversation_id=conversation_id))}'

@app.route('/upload' ,methods=['GET', 'POST'])
def upload_file():
    return '<form action="http://localhost:5000/upload" method="post" enctype="multipart/form-data">\
        <input type="file" name="file">\
        <button type="submit">Upload</button>\
    </form>' 

@app.route('/' ,methods=['GET', 'POST'])
def human_resp(): 
     if request.form.get('prompt') :print(request.form.get('prompt'));return redirect(f'/response/{request.form.get("prompt")}', code=302)
     return '<form action="/" method="post">\
      <label for="prompt">Enter the prompt:</label>\
      <input type="text" id="prompt" name="prompt" required><br>\
     </form>'

@app.route('/response/<prompt>' ,methods=['GET', 'POST'])
def machine_resp(prompt:str):
     with Timing("Inference completed"):
        inference_ = inference(tokenizer, model, prompt)
        if inference_ : return f'<p>Machine: {inference_}</p>'  


if __name__ == '__main__':
    # torch.cuda.empty_cache()
    with Timing("Loading the tokenizer: "):
        tokenizer = load_tokenizer()
    with Timing("Loading the model: "):
        model = load_model("/home/coeai/temporary/model", 'cpu')
        # model = load_model("/home/coeai/temporary/model", 'cuda')
    app.run()
