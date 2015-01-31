__author__ = 'ddutta'

from datetime import datetime
from elasticsearch import Elasticsearch


class Search(object):
    def __init__(self):
        self.es = Elasticsearch()

    def insert(self, doc):
        self.es.index(index="master", doc_type="logs", body=doc)


    def search(self, query, jsoninput):
        res = self.es.search(index="master",
                             body={"query": {"match_all": jsoninput}})

        results = []
        if res['hits']['total']>0:
            # we got hits
            for hit in res['hits']['hits']:
                print("%(postDate)s %(user)s: %(message)s" % hit["_source"])
                results = results + hit["_source"]
        return results