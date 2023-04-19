from flask import Flask, request, jsonify
from flask_cors import CORS

from wb_chat_completion import WBChatBot
from wb_embedding import ask_wb_question

app = Flask(__name__)
CORS(app)
chatbot = WBChatBot()


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


@app.route('/chat', methods=['POST'])
def chat_w_wb():
    request_json = request.get_json()
    user_id = request_json['role']
    if user_id != 'user':
        return request_json
    else:
        question_text = request_json['content']
        print(chatbot.chat_history)
        result_text = chatbot.chat(question_text, include_ref=True)
        return jsonify(result_text)


@app.route('/chat_all', methods=['POST'])
def chat_w_wb_all():
    request_json = request.get_json()
    result_text = chatbot.chat_all(request_json)
    return jsonify(result_text)


@app.route('/reset', methods=['POST'])
def reset_w_wb():
    chatbot.chat_reset()
    return jsonify("SUCCESS")


@app.route('/')
def home():
    return 'Hello, World from WB!'


@app.route('/about')
def about():
    return 'About'


if __name__ == "__main__":
    app.run()
