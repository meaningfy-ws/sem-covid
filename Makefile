SHELL=/bin/bash -o pipefail
BUILD_PRINT = \e[1;34mSTEP: \e[0m

#-----------------------------------------------------------------------------
# Basic commands
#-----------------------------------------------------------------------------


install:
	@ echo "$(BUILD_PRINT)Installing the requirements"
	@ echo "$(BUILD_PRINT)Warning: this setup depends on the Airflow 2.1 constraints. If you upgrade the Airflow version, make sure to adjust the constraint file reference."
	@ pip install --upgrade pip
	@ pip install "apache-airflow==2.1.0" --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2-1/constraints-no-providers-3.8.txt"
#	@ pip install -r requirements.txt --use-deprecated legacy-resolver --constraint "https://github.com/apache/airflow/blob/constraints-2-1/constraints-no-providers-3.8.txt"
	@ pip install -r requirements.txt --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2-1/constraints-no-providers-3.8.txt"
	@ python -m spacy download en_core_web_sm

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
	@ curl -X PUT "http://localhost:9200/ds_finreg_cellar" -H 'Content-Type: application/json' -H "Authorization: Basic ZWxhc3RpYzpjaGFuZ2VtZQ==" -d @resources/elasticsearch/ds_eu_cellar_mapping.json

all: install

test-unit:
	@ echo "$(BUILD_PRINT)Running the unit tests"
	@ py.test --ignore=tests/tests/e2e -s --html=report.html --self-contained-html

test-e2e:
	@ echo "$(BUILD_PRINT)Running the end to end tests"
	@ py.test --ignore=tests/tests/unit -s --html=report.html --self-contained-html

tests:
	@ echo "$(BUILD_PRINT)Running all tests"
	@ py.test -s --html=report.html --self-contained-html



# Getting secrets from Vault

# Testing whether an env variable is set or not
guard-%:
	@ if [ "${${*}}" = "" ]; then \
        echo "$(BUILD_PRINT)Environment variable $* not set"; \
        exit 1; \
	fi

# Testing that vault is installed
vault-installed: #; @which vault1 > /dev/null
	@ if ! hash vault 2>/dev/null; then \
        echo "$(BUILD_PRINT)Vault is not installed, refer to https://www.vaultproject.io/downloads"; \
        exit 1; \
	fi

# Get secrets in dotenv format
vault_secret_to_dotenv: guard-VAULT_ADDR guard-VAULT_TOKEN vault-installed
	@ echo "$(BUILD_PRINT)Writing the mfy/sem-covid secret from Vault to .env"
	@ vault kv get -format="json" mfy/sem-covid-infra | jq -r ".data.data | keys[] as \$$k | \"\(\$$k)=\(.[\$$k])\"" > .env
	@ vault kv get -format="json" mfy/jupyter-notebook | jq -r ".data.data | keys[] as \$$k | \"\(\$$k)=\(.[\$$k])\"" >> .env
	@ vault kv get -format="json" mfy/ml-flow | jq -r ".data.data | keys[] as \$$k | \"\(\$$k)=\(.[\$$k])\"" >> .env
	@ vault kv get -format="json" mfy/air-flow | jq -r ".data.data | keys[] as \$$k | \"\(\$$k)=\(.[\$$k])\"" >> .env
	@ vault kv get -format="json" mfy/min-io | jq -r ".data.data | keys[] as \$$k | \"\(\$$k)=\(.[\$$k])\"" >> .env
	@ vault kv get -format="json" mfy/elastic-search | jq -r ".data.data | keys[] as \$$k | \"\(\$$k)=\(.[\$$k])\"" >> .env
	@ vault kv get -format="json" mfy/sem-covid | jq -r ".data.data | keys[] as \$$k | \"\(\$$k)=\(.[\$$k])\"" >> .env
	@ vault kv get -format="json" mfy/vault | jq -r ".data.data | keys[] as \$$k | \"\(\$$k)=\(.[\$$k])\"" >> .env

# Get secrets in json format
vault_secret_to_json: guard-VAULT_ADDR guard-VAULT_TOKEN vault-installed
	@ echo "$(BUILD_PRINT)Writing the mfy/sem-covid secret from Vault to variables.json"
	@ vault kv get -format="json" mfy/sem-covid-infra | jq -r ".data.data" > tmp1.json
	@ vault kv get -format="json" mfy/jupyter-notebook | jq -r ".data.data" > tmp2.json
	@ vault kv get -format="json" mfy/ml-flow | jq -r ".data.data" > tmp3.json
	@ vault kv get -format="json" mfy/air-flow | jq -r ".data.data" > tmp4.json
	@ vault kv get -format="json" mfy/min-io | jq -r ".data.data" > tmp5.json
	@ vault kv get -format="json" mfy/elastic-search | jq -r ".data.data" > tmp6.json
	@ vault kv get -format="json" mfy/sem-covid | jq -r ".data.data" > tmp7.json
	@ vault kv get -format="json" mfy/vault | jq -r ".data.data" > tmp8.json
	@ jq -s '.[0] * .[1] * .[2] * .[3] * .[4] * .[5] * .[6] * .[7]' tmp*.json> variables.json
	@ rm tmp*.json

start_airflow:
	@ echo "$(BUILD_PRINT)Starting the Airflow scheduler and webserver"
	@ export AIRFLOW_HOME=`pwd` ; \
	export AIRFLOW__CORE__LOAD_EXAMPLES=false ; \
	export AIRFLOW__CORE__DAGS_FOLDER=`pwd` ; \
	yes | airflow db reset ; \
	airflow db init ; \
	airflow users  create --role Admin --username admin --email admin --firstname admin --lastname admin --password admin
	@ export AIRFLOW_HOME=`pwd` ; \
	export AIRFLOW__CORE__LOAD_EXAMPLES=false ; \
	export AIRFLOW__CORE__DAGS_FOLDER=`pwd` ; \
	airflow webserver -p 8080 -D &
	@ export AIRFLOW_HOME=`pwd` ; \
	export AIRFLOW__CORE__LOAD_EXAMPLES=false ; \
	export AIRFLOW__CORE__DAGS_FOLDER=`pwd` ; \
	airflow scheduler -D &

stop_airflow:
	@ echo "$(BUILD_PRINT)Stopping the Airflow scheduler and webserver"
	@ pkill -f airflow


lint:
	@ echo "$(BUILD_PRINT)Looking for dragons in your code ...."
	@ pylint sem_covid