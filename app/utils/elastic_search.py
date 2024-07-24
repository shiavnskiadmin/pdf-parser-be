from app.configs.elastic_connection import connections
from elasticsearch import Elasticsearch

def get_es_client() -> Elasticsearch:
    return connections.elasticsearch_client
