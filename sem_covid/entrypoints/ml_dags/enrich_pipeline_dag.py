# -*- coding: utf-8 -*-
# Date    : 19.07.2021 
# Author  : Stratulat Ștefan
# File    : enrich_pipeline_dag.py
# Software: PyCharm
from typing import Type

from sem_covid.adapters.dag.abstract_dag_pipeline import DagPipeline
from sem_covid.services.enrich_pipelines.base_enrich_pipeline import BaseEnrichPipeline, BasePrepareDatasetPipeline


class EnrichPipelineDag(DagPipeline):
    """
        This class aims to combine the pipeline of data preparation
         and enrichment pipeline.
    """

    def __init__(self, textual_columns: list,
                 ds_es_index: str,
                 features_store_name: str,
                 dataset_preparation_pipeline: Type[BasePrepareDatasetPipeline] = BasePrepareDatasetPipeline,
                 dataset_enrichment_pipeline: Type[BaseEnrichPipeline] = BaseEnrichPipeline):
        self.textual_columns = textual_columns
        self.ds_es_index = ds_es_index
        self.features_store_name = features_store_name
        self.dataset_preparation_pipeline = dataset_preparation_pipeline
        self.dataset_enrichment_pipeline = dataset_enrichment_pipeline

    def get_steps(self) -> list:
        return [
            self.prepare_dataset,
            self.enrich_dataset
        ]

    def prepare_dataset(self, *args, **context):
        """
            Method for making preparation pipeline.
        :return:
        """
        self.dataset_preparation_pipeline(textual_columns=self.textual_columns,
                                          ds_es_index=self.ds_es_index,
                                          features_store_name=self.features_store_name
                                          ).execute()

    def enrich_dataset(self, *args, **context):
        """
             Method for making enrich pipeline.
        :return:
        """
        self.dataset_enrichment_pipeline(feature_store_name=self.features_store_name,
                                         ds_es_index=self.ds_es_index
                                         ).execute()
