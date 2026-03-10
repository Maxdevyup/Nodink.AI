from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from transformers import AutoTokenizer, AutoModelForCausalLM, TextIteratorStreamer
import torch
from threading import Thread

app = Flask(__name__)
CORS(app)

AI_Role = "You are a helpful assistant."
conversation = [
    {"role": "system", "content": AI_Role}
]

model_id = "Qwen/Qwen3-0.6B"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.float16)

@app.route("/API/Streamer", methods=["POST"])
def Stream_Response():
    global conversation
    asked_question = request.json["message"]
    conversation.append({"role": "user", "content": asked_question})

    Input_text = tokenizer.apply_chat_template(conversation, tokenize=False, add_generation_prompt=True)
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
        reponse_complete = ""
        for token in streamer:
            reponse_complete += token
            yield f" {token}\n\n"
        conversation.append({"role": "assistant", "content": reponse_complete})

    return Response(generer(), mimetype="text/event-stream")

if __name__ == "__main__":
    app.run(port=5000, debug=False)
    
        