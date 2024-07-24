from fastapi import APIRouter, HTTPException, Request, Depends
from app.models.item_models import TemplateWithMetaItem
from typing import List
from app.libs import extract_data
from typing import List
from app.utils.elastic_search import get_es_client
from elasticsearch import Elasticsearch

user_router = APIRouter()

# Function to test Elasticsearch connection
def test_elasticsearch_connection():
    try:
        es = get_es_client()
        es.ping()  
        return True
    except ConnectionError:
        return False
    
if test_elasticsearch_connection():
    print("Connected to Elasticsearch successfully!")
else:
    print("Failed to connect to Elasticsearch.")
