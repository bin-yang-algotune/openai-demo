import itertools
import os

import pandas as pd
from pymilvus import connections, utility
from pymilvus import Collection, DataType, FieldSchema, CollectionSchema
import uuid

from wb_embedding import get_embeddding


def db_search(question_text: str, top_n: int = 1) -> pd.DataFrame:
    """
    based on a question text search milvus database
    :param top_n:
    :param question_text:
    Usage:
    >>> question_text = 'what do you think about tech companies'
    >>> top_n = 3
    >>> db_search(question_text, top_n)
    """
    q_embedding = get_embeddding(question_text)
    milvus_uri = os.getenv('MILVUS_URI')
    user = os.getenv('MILVUS_USER')
    password = os.getenv('MILVUS_PASS')
    connections.connect("default",
                        uri=milvus_uri,
                        user=user,
                        password=password,
                        secure=True)

    collection = Collection("wb_convo")
    search_params = {"metric_type": "L2"}
    results = collection.search([q_embedding],
                                anns_field='openai_embedding',
                                param=search_params,
                                limit=top_n)
    result_df = pd.DataFrame()
    if len(results) > 0:
        id_list = [x.ids for x in results]
        dis_list = [x.distances for x in results]
        merged_list = list(itertools.chain(*id_list))
        merged_dis_list = list(itertools.chain(*dis_list))
        res_entities = collection.query(
            expr="convo_id in [{}]".format(','.join(['\"{}\"'.format(x) for x in merged_list])),
            output_fields=["category", "content", 'source', 'token_count'],
            consistency_level="Strong"
        )
        result_df = pd.DataFrame(res_entities)
        result_df['distance'] = merged_dis_list
    connections.disconnect('default')
    return result_df


def insert_data_to_milvus_only(input_data: pd.DataFrame):
    milvus_uri = os.getenv('MILVUS_URI')
    user = os.getenv('MILVUS_USER')
    password = os.getenv('MILVUS_PASS')
    connections.connect("default",
                        uri=milvus_uri,
                        user=user,
                        password=password,
                        secure=True)
    print(f"Connecting to DB: {milvus_uri}")

    # Check if the collection exists
    collection_name = "wb_convo"
    collection = Collection(name=collection_name)
    input_data['convo_id'] = [str(uuid.uuid4()) for x in range(len(input_data))]
    input_entities = [
        input_data['convo_id'].tolist(),
        input_data['category'].tolist(),
        input_data['content'].tolist(),
        input_data['source'].tolist(),
        input_data['token_count'].tolist(),
        input_data['openai_embedding'].tolist()
    ]
    ins_resp = collection.insert(input_entities)
    return ins_resp


def insert_data_to_milvus(input_data: pd.DataFrame):
    """

    :param input_data:
    usage:
    >>> from wb_chatbot import get_training_data_final
    >>> input_data = get_training_data_final()
    >>> insert_data_to_milvus(input_data)
    """
    milvus_uri = os.getenv('MILVUS_URI')
    user = os.getenv('MILVUS_USER')
    password = os.getenv('MILVUS_PASS')
    connections.connect("default",
                        uri=milvus_uri,
                        user=user,
                        password=password,
                        secure=True)
    print(f"Connecting to DB: {milvus_uri}")

    # Check if the collection exists
    collection_name = "wb_convo"
    check_collection = utility.has_collection(collection_name)
    if check_collection:
        utility.drop_collection(collection_name)
    print("Success!")

    input_data['convo_id'] = [str(uuid.uuid4()) for x in range(len(input_data))]
    convo_id = FieldSchema(name="convo_id", dtype=DataType.VARCHAR, max_length=100, is_primary=True)
    category = FieldSchema(name="category", dtype=DataType.VARCHAR, max_length=1000)
    content = FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=40000)
    source = FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=1000)
    token_count = FieldSchema(name="token_count", dtype=DataType.INT64)
    openai_embedding = FieldSchema(name="openai_embedding", dtype=DataType.FLOAT_VECTOR, dim=1536)
    schema = CollectionSchema(fields=[convo_id, category, content, source, token_count, openai_embedding],
                              auto_id=False,
                              description="wb_convo_collection")
    print(f"Creating example collection: {collection_name}")
    collection = Collection(name=collection_name, schema=schema)
    print(f"Schema: {schema}")
    print("Success!")

    input_entities = [
        input_data['convo_id'].tolist(),
        input_data['category'].tolist(),
        input_data['content'].tolist(),
        input_data['source'].tolist(),
        input_data['token_count'].tolist(),
        input_data['openai_embedding'].tolist()
    ]
    ins_resp = collection.insert(input_entities)
    print("Insert Success!")

    index_params = {"index_type": "AUTOINDEX", "metric_type": "L2", "params": {}}
    collection.create_index(field_name=openai_embedding.name, index_params=index_params)
    print("Index creation Success!")
    collection.load()
    connections.disconnect("default")
