import requests
import json


def call_rest_api():
    api_url = "https://openai-wb-demo.herokuapp.com/ask"
    # api_url = "http://127.0.0.1:8000/ask"
    headers = {"Content-Type": "application/json"}
    todo = {'role': 'user', 'content': 'what do you think about bank failure'}
    response = requests.post(api_url, data=json.dumps(todo), headers=headers)
    print(response)
    # response.json()

    api_url = "https://openai-wb-demo.herokuapp.com/chat"
    # api_url = "http://127.0.0.1:5000/chat"
    headers = {"Content-Type": "application/json"}
    todo = {'role': 'user', 'content': 'what do you think about bank failure'}
    response = requests.post(api_url, data=json.dumps(todo), headers=headers)

    # api_url = "https://openai-wb-demo.herokuapp.com/chat"
    api_url = "http://127.0.0.1:5000/chat"
    headers = {"Content-Type": "application/json"}
    todo = {'role': 'user', 'content': 'what do you think about investing in tech companies'}
    response = requests.post(api_url, data=json.dumps(todo), headers=headers)

    todo = {'role': 'user',
            'content': 'but you have invested in technologies companies before, how do you explain that?'}
    response = requests.post(api_url, data=json.dumps(todo), headers=headers)

    print(response)
