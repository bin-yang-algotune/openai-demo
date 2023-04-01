import requests
import json


def call_rest_api():
    api_url = "https://openai-wb-demo.herokuapp.com/ask"
    headers = {"Content-Type": "application/json"}
    todo = {'role': '', 'content': 'what do you think about bank failure'}
    response = requests.post(api_url, data=json.dumps(todo), headers=headers)
    print(response)
    # response.json()
