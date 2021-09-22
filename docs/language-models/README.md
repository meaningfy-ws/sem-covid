# *WP3.2 - Trained language models*

## **Dependencies**

- spacy
- pandas
- gensim 

## **Language models**

To see the differences between different types of data sources, namely between legal data that are stored in ds_eu_cellar and media data that are stored in ds_eu_timeline, ds_pwdb, ds_ireland_timeline, 3 language models were involved, with **gensim** library help: 

- M1 (language model 1) - is a language model driven on textual data from the ds_pwdb, ds_eu_timeline, ds_ireland_timeline datasets.
- M2 (language model 2) - is a language model driven on textual data from the ds_eu_cellar dataset.
- M3 (language model 3) - is a language model driven on textual data from the ds_pwdb, ds_eu_timeline, ds_ireland_timeline, ds_eu_cellar datasets.

Each model is a model driven type Word2Vec and was saved in a separate file named:
- model**X**_ language_model.model (where X can have the values 1,2 or 3).

### **Source code**
A separate pipeline has been created for language modeling, the pipeline is made through a class:
- **LanguageModelPipeline** - this class creates a pipeline that trains the language model in a few predefined steps:
    - data download
    - extraction of textual data
    - textual data processing
    - transformation into **spacy** document
    - extracting features
    - model training
    - saving the model 


 [Source code](../../sem_covid/services/language_model_pipelines/language_model_pipeline.py)
 - sem_covid/services/language_model_pipeline.py

 [Execution in Jupyter Notebook](../../sem_covid/entrypoints/notebooks/language_modeling/word2vec_model_training.ipynb)
 - sem_covid/entrypoints/notebooks/language_modeling/word2vec_model_training.ipynb

