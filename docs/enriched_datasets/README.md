# *WP2.3 - enriched data-sets by classification models*

## **Dependencies**

- pycaret
- mlflow 

## **Classifiers**

The classifiers were trained based on the textual fields from ds_pwdb dataset. A classifier has been trained for each field of the ds_pwdb dataset in the list below. :
 - businesses 
 - citizens
 - workers
 - category
 - subcategory
 - type_of_measure 
 - funding

The classifiers can be found in the WP2.2 package.
## **Enrichment pipeline**
The enrichment pipeline aims to enrich the datasets (ds_eu_cellar, ds_eu_timeline, ds_ireland_timeline) with new fields based on the classifiers trained on the ds_pwdb dataset.

The new fields that are added to the datasets are: 
 - businesses 
 - citizens
 - workers
 - category
 - subcategory
 - type_of_measure 
 - funding

Each new field can be found in the enriched datasets that are attached to the WP2.3 package in the enriched_datasets folder:
- ds_eu_cellar_enriched
- ds_eu_timeline_enriched
- ds_ireland_timeline_enriched

### **Source code**
The enrichment pipeline is divided into two sub-pipelines, namely the enrichment dataset preparation pipeline and the enrichment pipeline:
 - BasePrepareDatasetPipeline - basic class for pipeline preparation of the dataset to be enriched.
 - BaseEnrichPipeline - basic class for pipeline enrichment of a dataset.

 [Source code](sem_covid/services/enrich_pipelines/base_enrich_pipeline.py)
 - sem_covid/services/enrich_pipelines/base_enrich_pipeline.py

 [Execution in Jupyter Notebook](sem_covid/entrypoints/notebooks/enrichment_pipeline.ipynb) 
 - sem_covid/entrypoints/notebooks/enrichment_pipeline.ipynb
