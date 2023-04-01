from flask import Flask, request, jsonify
from flask_cors import CORS

from wb_embedding import ask_wb_question

app = Flask(__name__)
CORS(app)


@app.route('/ask', methods=['POST'])
def ask_question():
    request_json = request.get_json()
    question_text = request_json['question_text']
    print(question_text)
    result_text = ask_wb_question(question_text)
    return jsonify(result_text)


@app.route('/')
def home():
    return 'Hello, World from WB!'


@app.route('/about')
def about():
    return 'About'
