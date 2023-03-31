import requests
import json


def call_rest_api():
    api_url = "http://localhost:5001/ask"
    headers = {"Content-Type": "application/json"}
    todo = {'question_text': ''}
    response = requests.post(api_url, data=json.dumps(todo), headers=headers)
    print(response)
    # response.json()
