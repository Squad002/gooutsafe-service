from flask import current_app

import logging

logger = logging.getLogger("monolith")


def add(index_name, model):
    if not current_app.elasticsearch:
        return

    body = dict()
    for attribute in model.__searchable__:
        body[attribute] = getattr(model, attribute)

    current_app.elasticsearch.index(index=index_name, id=model.id, body=body)


def remove(index_name, model):
    if not current_app.elasticsearch:
        return

    current_app.elasticsearch.delete(index=index_name, id=model.id)


def query(index_name, query, page, per_page):
    if not current_app.elasticsearch:
        logger.warning("Trying to search without an instance of Elasticsearch")
        return [], 0

    search = current_app.elasticsearch.search(
        index=index_name,
        body={
            "query": {"multi_match": {"query": query, "fields": ["*"]}},
            "from": (page - 1) * per_page,
            "size": per_page,
        },
    )

    ids = [int(hit["_id"]) for hit in search["hits"]["hits"]]
    return ids, search["hits"]["total"]["value"]
