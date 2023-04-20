from flask import Flask, request, jsonify
from flask_cors import CORS

from wb_chat_completion import WBChatBot
from wb_embedding import ask_wb_question

app = Flask(__name__)
CORS(app)


@app.route('/ask', methods=['POST'])
def ask_question():
    request_json = request.get_json()
    user_id = request_json['role']
    if user_id != 'user':
        return request_json
    else:
        question_text = request_json['content']
        print(question_text)
        result_text = ask_wb_question(question_text)
        return jsonify(result_text)


@app.route('/chat_all', methods=['POST'])
def chat_w_wb_all():
    chatbot = WBChatBot()
    request_json = request.get_json()
    # if 'reference' is in the request, remove them
    msg_list = []
    for msg in request_json:
        if 'reference' in msg.keys():
            msg.pop('reference')
        msg_list.append(msg)
    result_text = chatbot.chat_all(msg_list)
    return jsonify(result_text)


@app.route('/')
def home():
    return 'Hello, World from WB!'


@app.route('/about')
def about():
    return 'About'


if __name__ == "__main__":
    app.run()
