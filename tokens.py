import pickle
import os

global token 
token = dict()

# Adding a new token!!
def load_tokens(access_key:str = None):
    #  global user_set
    print("Entered the load pickle")
    infile = open('tokenList.pkl', 'rb')
    user_set = pickle.load(infile)
    infile.close()
    print("Access key =", type(access_key))
    for i in user_set.keys():
        if i != access_key: 
            print("Sucessfully loaded the pickle file\n", user_set.keys())
            return None
        else:
            return user_set[access_key]


'''
Key =  string, the name of the token 
token_to_add = Actual token
'''
def dump_tokens(key:str,token_to_add:str):
    # global user_set
    outfile = open('tokenList.pkl', 'wb')
    token[key] = token_to_add
    pickle.dump(token, outfile)
    outfile.close()

curr_dir = os.getcwd()
token_path = curr_dir + '\\tokenList.pkl' 

# We should call this method which takes care of the access tokens
def load_verified_token(access_key:str ):    
    if os.path.exists(token_path) and load_tokens(access_key) != None:
        return load_tokens(access_key)
    else:
        # print(requests.get('https://chat.openai.com/api/auth/session', headers=headers).content) #To get the response of access token
        access_token = input("Enter the access token from the following URL \nhttps://chat.openai.com/api/auth/session\nSearch for this URL after logging in to your ChatGPT account and copy the access token(Only the value of token): ")
        dump_tokens('GPT_ACCESS_TOKEN', access_token)

if __name__ == "__main__":
    # dump_tokens("HUGGING_FACE_testing_prompt_engineering","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")
    # print(type(load_tokens("HUGGING_FACE_testing_prompt_engineering")))
    # print(load_tokens())
    if(load_tokens("GPT_ACCESS_TOKE") == None):
        print("Entered ")
    


    