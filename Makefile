BUILD_PRINT = \e[1;34mSTEP: \e[0m

#-----------------------------------------------------------------------------
# Basic commands
#-----------------------------------------------------------------------------

install:
	@ echo "$(BUILD_PRINT)Installing the requirements"
	@ pip install --upgrade pip
	@ pip install -r resources/requirements.txt

create-indexes:
	@ echo "$(BUILD_PRINT)Creating indexes and their respective mappings"
	@ curl -X PUT "http://srv.meaningfy.ws:9200/pwdb-index" -H 'Content-Type: application/json' -H "Authorization: Basic ZWxhc3RpYzpjaGFuZ2VtZQ==" -d @resources/elasticsearch/pwdb_index_mapping.json
	@ curl -X PUT "http://srv.meaningfy.ws:9200/eurlex-index" -H 'Content-Type: application/json' -H "Authorization: Basic ZWxhc3RpYzpjaGFuZ2VtZQ==" -d @resources/elasticsearch/eurlex_index_mapping.json
	@ curl -X PUT "http://srv.meaningfy.ws:9200/treaties-index" -H 'Content-Type: application/json' -H "Authorization: Basic ZWxhc3RpYzpjaGFuZ2VtZQ==" -d @resources/elasticsearch/treaties_index_mapping.json

all: install
