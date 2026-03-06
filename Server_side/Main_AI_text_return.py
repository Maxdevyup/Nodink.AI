
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from transformers import AutoTokenizer, AutoModelForCausalLM, TextIteratorStreamer
import torch
from threading import Thread

app = Flask(__name__)
CORS(app)


#Token management
TokenAvailable = 100
TokenUsed = 0
AI_Role = "You are a helpful assistant."
# Load the model and tokenizer
model_id = "Qwen/Qwen3-0.6B" #get a fast model to test
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id, dtype=torch.float16)

#One chunk system
@app.route('/API', methods=['POST'])
def response_send():
    #question input
    asked_question = request.json["message"]
    #Create the message
    messages = [
        {"role": "system", "content": AI_Role},
        {"role": "user", "content": asked_question}
    ]

    #Create the input for the model
    Input_text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    TokenizeInput = tokenizer(Input_text, return_tensors="pt")

    #Generate the response
    with torch.no_grad():
        outputs = model.generate(
            **TokenizeInput,
            max_new_tokens=200,
            temperature=0.7,
            do_sample=True
        )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(response)
    print("Request Complete")
    response = response.split("</think>")[-1].strip()
    return jsonify({"reponse": response})

@app.route("/API/Streamer", methods =["POST"])
def Stream_Response():
     #question input
    asked_question = request.json["message"]
    #Create the message
    messages = [
        {"role": "system", "content": AI_Role},
        {"role": "user", "content": asked_question}
    ]
    
    Input_text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    TokenizeInput = tokenizer(Input_text, return_tensors="pt")
    streamer = TextIteratorStreamer(tokenizer, skip_prompt=True, skip_special_tokens=False)

    thread = Thread(target=model.generate, kwargs={
        **TokenizeInput,
        "max_new_tokens": 700,
        "temperature": 0.7,
        "do_sample": True,
        "streamer": streamer
    })
    thread.start()
    def generer():
        for token in streamer:
            yield f" {token}\n\n"

    return Response(generer(), mimetype="text/event-stream")


    #Launch Server
if __name__ == "__main__":
    app.run(port=5000, debug=False)
    
        