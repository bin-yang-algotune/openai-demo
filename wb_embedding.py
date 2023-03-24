from typing import List
import pprint
import numpy as np
import openai
import os
from transformers import GPT2TokenizerFast
import pandas as pd

from wb_chatbot import get_training_data_wb_transcript, get_training_data_final

EMBEDDING_MODEL = 'text-embedding-ada-002'
COMPLETIONS_MODEL = "text-davinci-003"

openai.api_key = os.getenv("OPENAI_API_KEY")

tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")


def count_tokens(input_text: str) -> int:
    """count the number of token given an input text
    :param input_text:
    :return:

    Usage:
    >>>

    """
    return len(tokenizer.encode(input_text))


def add_token_count_to_wb_transcript():
    train_data_df = get_training_data_wb_transcript()
    if 'token_count' not in train_data_df.columns:
        result_list = []
        for idx, row in train_data_df.iterrows():
            print('processing [{}]'.format(row['category']))
            input_text = row['content']
            result_list.append(count_tokens(input_text))
        train_data_df['token_count'] = result_list
        train_data_df.to_pickle('wb_train_data_full_transcript.pkl')


def get_embeddding(input_text: str,
                   openai_model: str = EMBEDDING_MODEL):
    """

    :param input_text:
    :param openai_model:
    :return:

    Usage:
    >>> input_text = 'how does inflation impact the returns of stocks?'
    >>> openai_model = EMBEDDING_MODEL
    """
    result = openai.Embedding.create(
        model=openai_model,
        input=input_text
    )

    return result["data"][0]["embedding"]


def add_embedding_to_wb_transcript():
    """
    add embeddings to the passages from annual meeting
    """
    train_data_df = get_training_data_final()
    if 'openai_embedding' not in train_data_df.columns:
        result_list = []
        for idx, row in train_data_df.iterrows():
            print('processing [{}]'.format(row['category']))
            input_text = row['content']
            if row['token_count'] <= 8100:
                embedding_data = get_embeddding(input_text)
            else:
                embedding_data = None
            result_list.append(embedding_data)
        train_data_df['openai_embedding'] = result_list
        train_data_df = train_data_df.dropna()
        train_data_df.to_pickle('wb_train_data_full_transcript.pkl')


def combine_embedding_completion(question_text: str, context_text: str):
    """

    :param question_text:
    :param context_text:
    Usage:

    """

    prompt = """Answer the question as truthfully as possible using the provided text as a guidance, 
    provide longer explanation if possible 
    and if the answer is not contained within the text below, say "I don't know"

    Context:
    {}


    Q: {}
    A:""".format(context_text, question_text)

    result = openai.Completion.create(
        prompt=prompt,
        temperature=0,
        max_tokens=2000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        model=COMPLETIONS_MODEL
    )["choices"][0]["text"]
    return result


def calc_vector_similarity(input_x: List[float], input_y: List[float]):
    """

    :param input_x:
    :param input_y:
    :return:
    """
    return np.dot(np.array(input_x),
                  np.array(input_y))


def find_relevant_topics(question_text: str,
                         input_data: pd.DataFrame,
                         top_n: int = 10):
    """

    :param question_text:
    :param input_data:
    :param top_n:
    Usage:
    >>> question_text = 'what do you think about technology companies, is it investible?'
    >>> input_data = get_training_data_final()
    >>> top_n = 2
    >>> find_relevant_topics(question_text, input_data, top_n)
    """
    q_embedding = get_embeddding(question_text)
    similarity_result_list = []
    for idx, row in input_data.iterrows():
        section_embedding = row['openai_embedding']
        similarity_score = calc_vector_similarity(q_embedding, section_embedding)
        similarity_result_list.append(similarity_score)
    out_data = input_data.copy()
    out_data['similarity_score'] = similarity_result_list
    out_data = out_data.sort_values('similarity_score', ascending=False)
    out_data = out_data.iloc[:top_n]
    return out_data


def ask_wb_question(question_text: str, top_n: int = 1):
    """

    :param top_n:
    :param question_text:
    Usage:
    >>> question_text = 'what do you think about bank failures'
    >>> top_n = 1
    >>> ask_wb_question(question_text)

    """
    input_data = get_training_data_final()
    result = find_relevant_topics(question_text, input_data, top_n=top_n)
    context_str = '\n'.join(result['content'])
    result = combine_embedding_completion(
        question_text,
        context_str
    )
    return result
