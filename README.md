# Sem-covid
Semantic analysis of COVID-19 measures adopted at the EU and Member State (MS) level.

This project includes functionality for gathering documents from various legal sources, and a series
of ML experiments.

![test](https://github.com/meaningfy-ws/sem-covid/actions/workflows/main.yml/badge.svg)
[![codecov](https://codecov.io/gh/meaningfy-ws/sem-covid/branch/main/graph/badge.svg?token=taHJFheCrU)](https://codecov.io/gh/meaningfy-ws/sem-covid)

## Objective
Establish a semantic mapping of the European Union and Member States response to the COVID-19 crisis 
in the area of living and working conditions.

## Description
In order to perform mapping and interlinking between the EU COVID-19 response to the key policies of 
the Member States in the area of working and living conditions, the appropriate data sources need 
to be identified and crawled into a unified dataset. Next, the data needs to be prepared then for 
machine learning (ML) methods, which in this case are notably the data classification, topic modelling,
data clustering and document similarity calculation. The results from ML tasks shall serve as the basis 
for a new dataset with document mappings, indicating possible correspondence between EU and MS responses 
to COVID-19 crisis.

## Datasets
- *Policy watch database (ds_pwdb)* - A suitable set of summarised descriptions of 
  what a COVID-19 measure looks like.
  - [Readme](docs/data-catalog/ds_pwdb.md)
  - [Download](docs/data-catalog/ds_pwdb.zip)
- *EU Cellar COVID-19 dataset (ds_eu_cellar)* - The Cellar is the semantic repository of the Publications Offic
  - [Readme](docs/data-catalog/ds_eu_cellar.md)
  - [Download](docs/data-catalog/ds_eu_cellar.zip)
- *EU action timeline dataset (ds_eu_timeline)* - The European Commission (EC) is coordinating a common 
  European response  to the coronavirus outbreak.
  - [Readme](docs/data-catalog/ds_eu_timeline.md)
  - [Download](docs/data-catalog/ds_eu_timeline.zip)  
- *Ireland action timeline dataset (ds_ireland_timeline)* - Ireland was selected as a tryout member state country for 
  which a COVID-19 timeline shall be created similar to the EU action timeline.
  - [Readme](docs/data-catalog/ds_ireland_tinmeline.md)
  - [Download](docs/data-catalog/ds_ireland_tinmeline.zip)

  
## Experiment's workflow
When the dataset reaches a significant extent, it shall be cleaned up and prepared for use in a series of 
Machine Learning (ML), Natural Language Processing (NLP) and Exploratory Data Analysis (EDA) tasks. These 
tasks need to be conceived as documented experiments that follow a “cycle of experimentation” comprising 
(a) the data analysis and preparation phase, (b) feature engineering and model training phase and (c) the 
maintenance, deployment and improvement phase, which subsequently may lead back to the data analysis and 
preparation phase and so entering the next experimentation cycle. 


## Project Structure
- `/docker` - the docker files representing specification and configurations for running the services on a target server
- `/docs` - dataset description
     - `/docs/data-catalog` - description of each dataset
     - `/docs/data-collection-report` - reports of data collection
     - `/docs/sparql-query-research` - SPARQL queries to research data
- `/resources` - data mapping resources
     - `/resources/crawlers` - the list of each press assistants and spoke persons
     - `/resources/elasticsearch` - mapper of each dataset
- `/requirements` - project requirements    
- `/sem-covid` - base architecture specific to this project 
     - `/sem-covid/adapters` - tools for dataset and language model usage from elasticsearch and MinIO
     - `/sem-covid/entrypoints` - a common package for DAGS, Machine Learning (ML) experiments and UI
       - `/sem-covid/entrypoints/etl_dags` - DAGS for data crawling and extraction
       - `/sem/covid/entrypoints/ml_dags` - DAGS for Machine Learning (ML) workflow of data cleaning and experimentation
       - `/sem/covid/entrypoints/notebooks` - notebooks with Machine Learning (ML) experiments and EDAs
       - `/sem/covid/entrypoints/ui` - legal initiatives UI
     - `/sem-covid/services` - directory for base Machine Learning (ML) experiments and data cleaning
       - `/sem-covid/services/crawlers` - tools for data crawling
       - `/sem-covid/services/sc_wrangling` - reusable classes for Machine Learning (ML) experiments
  
  
## Technological stack

See the infrastructure setup with explanations available in the [sem-covid-infra repository](https://github.com/meaningfy-ws/sem-covid-infra)

 - Jupyter Notebook & Polotly
 - scikit-learn \ Gensym \ Spacy \ PyTorch
 - Docker(+compose)
 - Apache Airflow
 - MinIO
 - MLFlow
 - Elasticsearch

# Contributing

You are more than welcome to help expand and mature this project.

When contributing to this repository, please first discuss the change you wish
to make via issue, email, or any other method with the owners of this repository
before making a change.

Please note we adhere to [Apache code of conduct](https://www.apache.org/foundation/policies/conduct), please follow it in all your
interactions with the project.

# License

The documents, such as reports and specifications, available in the /doc folder,
are licenced under a [CC BY 4.0 licence](https://creativecommons.org/licenses/by/4.0/deed.en).

The scripts (stylesheets) and other executables are licenced under [GNU GPLv3](https://www.gnu.org/licenses/gpl-3.0.en.html) licence.

