 #!/usr/bin/env python3 
#-*- coding: utf-8 -*- 

"""
Created on Wed Dec 25 12:47:44 2019
@author: Amal Htait
"""

from elasticsearch import Elasticsearch, helpers 
import os, uuid, json
import common as c


# Generator to push bulk data from a JSON file into an Elasticsearch index / that function is changed according to files content
def bulkJsonData(json_file, _index,whatStuff):
	json_list = c.getDataFromFile(json_file)
	for doc in json_list:
		# use a 'yield' generator so that the data isn't loaded into memory
		if '{"index"' not in doc:

			json_doc = json.loads(doc)

			# add load_type, used later for filter
			json_doc.update([ ("load_type", whatStuff) ]) 
			json_doc.update([ ("source_type", "twitter") ]) 
			new_doc = str(json_doc).replace("'", '"')
			#print (new_doc)

			yield {
				"_index": _index,
				"_id": uuid.uuid4(),
				 "_source": new_doc
			}


def fct():
	elastic = Elasticsearch(hosts=[{'host':'localhost','port':9200}])

	# the Schema, used to force specific types and to add alias/ it is changed according to files content
	schema = {      
	    "settings": {
	      "analysis": {
	        "analyzer": {
	          "my_english_analyzer": {"type": "standard","stopwords": "_english_"}
		       }
		     }
		   }, 
		  "mappings":{
		    "properties":{   
	    		"createdAt":   { "type":"date", "format":"yyyy-MM-dd'T'HH:mm:ss.SSSXXX"},
	    		"created_at": { "type": "alias", "path": "createdAt" },
	    		"all_text": { "type": "text", "analyzer": "my_english_analyzer", "fields": {"keyword": { "type": "keyword"}}, "fielddata": True}
				
		    } 
		  }
		}

	# Create index with a schema
	c.createIndex('dfp_tw_msg', schema, elastic)


	inputFolder = "dataSource/json-twitter_data"
	for loadType in ["direct-message"]: # direct-message-group to do !!!!!!!!
		whatFile = os.path.join(inputFolder, loadType+'_fixed.json')
		try:
			response = helpers.bulk(elastic, bulkJsonData(whatFile, "dfp_tw_msg",loadType))
		except:
			print ("Error in "+ whatFile)
			pass

	print ("Insert Twitter Messages")
	 