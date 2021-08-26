
from typing import List

from sem_covid.entrypoints.notebooks.language_modeling.language_model_tools.similarity_calculus import \
    build_similarity_matrix
from sem_covid.services.language_model_pipeline import LanguageModelPipeline
from sem_covid.services.pos_extraction import POSExtraction
from sem_covid.services.store_registry import store_registry


class LanguageModelExecutionSteps:
    def __init__(self, language_model_file_name: str, model_name: str) -> None:
        """
            This class executes three steps to view the similarity between words from word2vec model:
            (1) trains language model
            (2) filters language model words
            (3) trains similarity matrices
            Args:
                language_model_file_name: word2vec model filename to be stored in MinIO
                model_name: the name of the model config
        """
        self.language_model_file_name = language_model_file_name
        self.model_name = model_name
        self.word2vec = None

    def train_language_model(self, dataset_sources_config: List[tuple]) -> None:
        """
            Trains word2vec model from dataset config,
            which is a list of tuples of dataset and their textual columns.
            After training the model is stored in MinIO for later use.
        """
        model_language_model_pipeline = LanguageModelPipeline(dataset_sources=dataset_sources_config,
                                                              language_model_name=self.language_model_file_name)
        model_language_model_pipeline.execute()
        self.word2vec = model_language_model_pipeline.word2vec

    def filter_language_model_words(self):
        """
            It filters the word2vec indexes, extracting selected noun phrases
        """
        if self.word2vec:
            return POSExtraction(self.word2vec, pos=['NOUN', 'ADJ'])
        else:
            return None

    def train_similarity_matrices(self) -> None:
        """
            for each type of similarity functions, it will create a similarity matrix, based on
            indexes and their vectors from most similar words of key words.
            The matrices will be stored in MinIO for later use.
        """
        similarity_functions = ['cosine', 'euclidean', 'hamming']
        for index in range(len(similarity_functions)):
            print('Start computing similarity matrix.')
            model_similarity_matrix = build_similarity_matrix(
                self.filter_language_model_words().extract_pos_embeddings(),
                self.filter_language_model_words().filter_by_pos(),
                metric=similarity_functions[index])
            print('Finish computing similarity matrix.')
            print('Save similarity matrix.')
            store_registry.minio_feature_store('semantic-similarity-matrices').put_features(
                features_name=f'{self.model_name}_{similarity_functions[index]}_matrix.pkl',
                content= model_similarity_matrix
            )
            del model_similarity_matrix
