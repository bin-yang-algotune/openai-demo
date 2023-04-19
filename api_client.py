import requests
import json


def call_rest_api():
    # api_url = "https://openai-wb-demo.herokuapp.com/chat_all"
    api_url = "http://127.0.0.1:5000/chat_all"
    headers = {"Content-Type": "application/json"}
    msg_list = [{'role': 'user', 'content': 'what do you think about bank failure'}]
    response = requests.post(api_url, data=json.dumps(msg_list), headers=headers)
    print(response)
