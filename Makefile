SHELL=/bin/bash -o pipefail
BUILD_PRINT = \e[1;34mSTEP: \e[0m

#-----------------------------------------------------------------------------
# Basic commands
#-----------------------------------------------------------------------------


install:
	@ echo "$(BUILD_PRINT)Installing the requirements"
	@ pip install --upgrade pip
	@ pip install -r requirements.txt
	@ python -m spacy download en_core_web_sm

#	TODO refactor
install-scrapy-dependencies:
	@ echo "$(BUILD_PRINT)Installing Scrapy the requirements"
	@ pip install --upgrade pip
	@ pip install -r eu_action_timeline/requirements.txt

start-splash:
	@ echo -e '$(BUILD_PRINT)(dev) Starting the splash container'
	@ docker-compose --file docker/docker-compose.yml --env-file .env up -d splash

stop-splash:
	@ echo -e '$(BUILD_PRINT)(dev) Starting the splash container'
	@ docker-compose --file docker/docker-compose.yml --env-file .env stop splash

# TODO refactor
create-indexes:
	@ echo "$(BUILD_PRINT)Creating indexes and their respective mappings"
	@ curl -X PUT "http://localhost:9200/ds_pwdb" -H 'Content-Type: application/json' -H "Authorization: Basic ZWxhc3RpYzpjaGFuZ2VtZQ==" -d @resources/elasticsearch/ds_pwdb_mapping.json
	@ curl -X PUT "http://localhost:9200/ds_eu_cellar" -H 'Content-Type: application/json' -H "Authorization: Basic ZWxhc3RpYzpjaGFuZ2VtZQ==" -d @resources/elasticsearch/ds_eu_cellar_mapping.json
	@ curl -X PUT "http://localhost:9200/ds_legal_initiatives" -H 'Content-Type: application/json' -H "Authorization: Basic ZWxhc3RpYzpjaGFuZ2VtZQ==" -d @resources/elasticsearch/ds_legal_initiatives_mapping.json
	@ curl -X PUT "http://localhost:9200/ds_treaties" -H 'Content-Type: application/json' -H "Authorization: Basic ZWxhc3RpYzpjaGFuZ2VtZQ==" -d @resources/elasticsearch/ds_treaties_mapping.json
	@ curl -X PUT "http://localhost:9200/ds_eu_timeline" -H 'Content-Type: application/json' -H "Authorization: Basic ZWxhc3RpYzpjaGFuZ2VtZQ==" -d @resources/elasticsearch/ds_eu_timeline_mapping.json
	@ curl -X PUT "http://localhost:9200/ds_ireland_timeline" -H 'Content-Type: application/json' -H "Authorization: Basic ZWxhc3RpYzpjaGFuZ2VtZQ==" -d @resources/elasticsearch/ds_ireland_timeline_mapping.json

all: install

test:
	@ echo "$(BUILD_PRINT)Running the tests"
	@ pytest -s --html=report.html --self-contained-html

# Getting secrets from Vault
# Testing whether an env variable is set or not
guard-%:
   @ if [ "${${*}}" = "" ]; then \
        echo "Environment variable $* not set"; \
        exit 1; \
   fi
# Testing that vault is installed
vault-installed: #; @which vault1 > /dev/null
   @ if ! hash vault 2>/dev/null; then \
        echo "Vault is not installed, refer to https://www.vaultproject.io/downloads"; \
        exit 1; \
   fi
# Get secrets in dotenv format
vault_secret_to_dotenv: guard-VAULT_ADDR guard-VAULT_TOKEN vault-installed
   @ echo "Writing the mfy/sem-covid secret from Vault to .env"
   @ vault kv get -format="json" mfy/sem-covid | jq -r ".data.data | keys[] as \$$k | \"\(\$$k)=\(.[\$$k])\"" > .env

# Get secrets in dotenv format
vault_experiments_secret_to_dotenv: guard-VAULT_ADDR guard-VAULT_TOKEN vault-installed
   @ echo "Writing the mfy/sem-covid secret from Vault to .env"
   @ vault kv get -format="json" mfy/sem_covid_experiments | jq -r ".data.data | keys[] as \$$k | \"\(\$$k)=\(.[\$$k])\"" > .env
   
# Get secrets in json format
vault_secret_to_json: guard-VAULT_ADDR guard-VAULT_TOKEN vault-installed
   @ echo "Writing the mfy/sem-covid secret from Vault to variables.json"
   @ vault kv get -format="json" mfy/sem-covid | jq -r ".data.data" > variables.json