from flask import current_app
from elasticsearch_dsl import Search


def add_to_index(index, model):
    if not current_app.elasticsearch:
        return
    payload = {}
    for field in model.__searchable__:
        payload[field] = getattr(model, field)
    current_app.elasticsearch.index(index=index, doc_type=index, id=model.id, body=payload)


def remove_from_index(index, model):
    if not current_app.elasticsearch:
        return
    current_app.elasticsearch.delete(index=index, doc_type=index, id=model.id)


def query_index(index, query, page, per_page):
    if not current_app.elasticsearch:
        return [], 0
    s = Search(using=current_app.elasticsearch, index=index)\
        .query('multi_match', query=query, fields=['*'])\
        .execute()
    ids = [int(hit['_id']) for hit in s['hits']['hits']]
    return ids, s['hits']['total']
