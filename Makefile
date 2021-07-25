SHELL=/bin/bash -o pipefail
BUILD_PRINT = \e[1;34mSTEP: \e[0m

#-----------------------------------------------------------------------------
# PIP Install commands
#-----------------------------------------------------------------------------

install:
	@ echo "$(BUILD_PRINT)Installing the requirements"
	@ pip install --upgrade pip
	@ pip install -r requirements-dev.txt
	@ python -m spacy download en_core_web_sm

install-prod:
	@ echo "$(BUILD_PRINT)Installing the requirements"
	@ pip install --upgrade pip
	@ pip install -r requirements-prod.txt
	@ python -m spacy download en_core_web_sm

#-----------------------------------------------------------------------------
# Poetry Install commands
#-----------------------------------------------------------------------------

poetry-install:
	@ echo "$(BUILD_PRINT)Installing the requirements.txt"
	@ pip install --upgrade pip
	@ poetry install
	@ python -m spacy download en_core_web_sm

poetry-export:
	@ echo "$(BUILD_PRINT)Exporting the requirements.txt"
#	@ poetry export -f requirements.txt --output requirements-prod.txt --without-hashes
	@ poetry export --dev -f requirements.txt --output requirements-dev.txt --without-hashes


#-----------------------------------------------------------------------------
# Testing commands
#-----------------------------------------------------------------------------

test:
	@ echo "$(BUILD_PRINT)Running the unit tests"
	@ py.test --ignore=tests/tests/e2e -s --html=report.html --self-contained-html

test-all:
	@ echo "$(BUILD_PRINT)Running all tests"
	@ py.test -s --html=report.html --self-contained-html

lint:
	@ echo "$(BUILD_PRINT)Looking for dragons in your code ...."
	@ pylint sem_covid
#-----------------------------------------------------------------------------
# Getting secrets from Vault
#-----------------------------------------------------------------------------

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

vault_secret_fetch: vault_secret_to_dotenv vault_secret_to_json

#-----------------------------------------------------------------------------
# Test/Dev environment make targets
#-----------------------------------------------------------------------------
start-splash:
	@ echo -e '$(BUILD_PRINT)(dev) Starting the splash container'
	@ docker-compose --file docker/docker-compose.yml --env-file ../.env up -d splash

stop-splash:
	@ echo -e '$(BUILD_PRINT)(dev) Starting the splash container'
	@ docker-compose --file docker/docker-compose.yml --env-file ../.env stop splash

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


build-airflow-image:
	@ echo "$(BUILD_PRINT)Building airflow image"
	@ cp requirements-airflow.txt docker/airflow
	@ docker build --tag airflow2_meaningfy:latest docker/airflow
	@ rm docker/airflow/requirements-airflow.txt


scrapy-eu-timeline-local:
	@ echo "$(BUILD_PRINT)Staring the local version of eu-timeline crawler"
	@ export PYTHONPATH=${CURDIR}; \
		cd sem_covid/services/crawlers/ ; \
		scrapy crawl eu-timeline