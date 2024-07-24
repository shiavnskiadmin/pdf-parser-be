from elasticsearch import Elasticsearch

# es_host = 'localhost'
# es_port = 9200


# def elastic_conn():
#     es = Elasticsearch([f"{es_host}:{es_port}"])
#     return es


class CONFIGURATIONS:
    def elasticsearch_configs(self):
        return {
            "es_host": "localhost",
            "es_port": 9200,
            # "es_user": "your_elasticsearch_username",
            # "es_password": "your_elasticsearch_password"
        }

class CONNECTIONS:
    def __init__(self):
        config = CONFIGURATIONS().elasticsearch_configs()
        self.elasticsearch_client = Elasticsearch(
            hosts=[{"host": config["es_host"], "port": config["es_port"]}]
            # http_auth=(config["es_user"], config["es_password"])
        )

connections = CONNECTIONS()
