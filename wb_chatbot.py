import os
import pprint
from typing import Dict, List

import openai
import pandas as pd
import requests
from bs4 import BeautifulSoup, Tag


def run_model():
    openai.api_key = os.getenv("OPENAI_API_KEY")

    prompt = """
  Q: If warren buffett was 20 year old today, how would he invest his money
  A:"""

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.7,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    pp = pprint.PrettyPrinter(indent=4)

    pp.pprint(response['choices'][0]['text'])


def get_training_data() -> List[Dict[str, str]]:
    url = 'https://buffettfaq.com/'
    req = requests.get(url)
    req.encoding = 'UTF-8'
    soup = BeautifulSoup(req.content, 'html.parser')
    all_h3_headings = soup.find_all('h3')
    result_list = []
    for h3 in all_h3_headings:
        # find the end of the paragraph which is a link back to 'question'
        p_element = h3.next_element
        answer_text = ''
        while p_element is not None:
            print(p_element)
            if p_element.name == 'p':
                answer_text += p_element.text + ' '
            next_element = p_element.next_element
            if next_element is not None and \
                    isinstance(next_element, Tag) and \
                    'class' in next_element.attrs.keys() and \
                    next_element.attrs['class'][0] == 'source':
                break
            else:
                p_element = p_element.next_element
        result_list.append({'prompt': h3.text, 'completion': answer_text})
    return result_list


def save_training_file():
    training_data = get_training_data()
    input_df = pd.DataFrame(training_data).iloc[:100]
    input_df.to_json('wb_train_data.json', orient='records', lines=True)
