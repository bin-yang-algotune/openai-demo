from typing import Dict, List

import openai

from wb_chatbot import get_training_data_final
from wb_embedding import find_relevant_topics

CHAT_COMPLETIONS_MODEL = "gpt-3.5-turbo"


class WBChatBot:
    def __init__(self, initial_prompt: str = None):
        self.chat_history = []
        if initial_prompt is None:
            self.initial_prompt = """You are [WARREN BUFFETT] and therefore need to answer the question in first-person.
            You need to answer the question as truthfully as possible using the provided context text as a guidance. 
            If the answer is not contained within the context text, use best of your knowledge to answer.
            If you are having problem coming up with answers, say "I don't know".
            Provide longer explanation whenever possible.
            """
        else:
            self.initial_prompt = initial_prompt
        self.chat_history.append({'role': 'system', 'content': self.initial_prompt})

    def chat_all(self, message_list: List[Dict[str, str]]):
        pass

    def chat(self, msg_question: str, top_n: int = 1, summarize_context: bool = False, include_ref: bool = True):
        """
        create a single question function which takes the chat history into consideration
        :param include_ref:
        :param msg_question:
        :param top_n:
        :param summarize_context:
        :return:
        Usage:
        >>> self = WBChatBot()
        >>> msg_question = 'what do you think about bank failure'
        >>> self.chat(msg_question)

        >>> msg_question = "what do you think about investing in tech companies"
        >>> top_n = 1
        >>> summarize_context = False
        >>> self.chat(msg_question)

        >>> msg_question = "but you have invested in some tech companies didn't you?"
        >>> self.chat(msg_question)

        >>> msg_question = "i see, are there specific attributes in a tech company that may make you change your mind?"
        >>> self.chat(msg_question)

        >>> msg_question = "even if you might miss out alot of potential alphas for berkshire hathway?"
        >>> self.chat(msg_question)
        """
        input_data = get_training_data_final()
        result = find_relevant_topics(msg_question, input_data, top_n=top_n)
        result = result.loc[result['similarity_score'] > 0.8]
        if summarize_context:
            context_str = ''
            ref_text = ''
        else:
            ref_text = '\n'.join(result['source'])
            context_str = '\n'.join(result['content'])

        new_system_msg = {'role': 'user',
                          'content': """context: {}
                          reference:{}
                          Q:{}
                          A:""".format(context_str, ref_text, msg_question)
                          }
        self.chat_history.append(new_system_msg)
        result_msg = {}
        try:
            completion = openai.ChatCompletion.create(
                model=CHAT_COMPLETIONS_MODEL,
                messages=self.chat_history,
                temperature=0.1
            )
            if completion is not None and len(completion['choices']) > 0:
                result_msg = completion['choices'][0]['message'].to_dict()
        except Exception as e:
            result_msg = {'role': 'assistant', 'content': f'Request failed with exception {e}'}
        # due to token size issue, we want to include context for the latest question only,
        # this may impact the quality of the results, but allow us to keep the conversation going longer
        self.chat_history.pop()
        new_system_msg = {'role': 'user',
                          'content': """Q:{}
                                  A:""".format(msg_question)
                          }
        self.chat_history.append(new_system_msg)

        if len(result_msg) > 0:
            if include_ref:
                result_msg['reference'] = ref_text
            self.chat_history.append(result_msg)
        return result_msg

    def chat_reset(self):
        self.chat_history = []
        self.chat_history.append({'role': 'system', 'content': self.initial_prompt})
