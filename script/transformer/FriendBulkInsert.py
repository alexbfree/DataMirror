#!/usr/bin/env python3 
#-*- coding: utf-8 -*- 

from elasticsearch import Elasticsearch, helpers 
import os, uuid, json
import common as c


# Generator to push bulk data from a JSON file into an Elasticsearch index / that function is changed according to files content
def bulkJsonData(json_file, _index,whatStuff):
	json_list = c.getDataFromFile(json_file)
	for doc in json_list:
		# use a 'yield' generator so that the data isn't loaded into memory
		if '{"index"' not in doc:
			
			yield {
				"_index": _index,
				"_id": uuid.uuid4(),
				 "_source": doc
			}



elastic = Elasticsearch(hosts=[{'host':'localhost','port':9200}])

# the Schema, used to force specific types and to add alias/ it is changed according to files content

schema = {      
	  "mappings":{
	    "properties":{   
	      "name": { "type":"keyword"},
	      "screen_name": { "type":"text"},
	      "tags": { "type":"number"},
	      "type": { "type":"text"}
	    } 
	  }
	}



# Create index with a schema
c.createIndex('dfp_friend', schema, elastic)


inputFolder = '../../vegaStuff/'

for r, d, f in os.walk(inputFolder):
	for file in f:
		if file.endswith("friends.json"):
			whatFile = os.path.join(inputFolder, file)
			#try:
			file_part=file.split(".")[0]
			response = helpers.bulk(elastic, bulkJsonData(whatFile, "dfp_friend",file_part))
			print ("Insert Friends")
			#except:
			#	print ("Error in "+ whatFile)
			#	pass


