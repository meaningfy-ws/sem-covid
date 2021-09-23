import spacy
nlp = spacy.load('en_core_web_sm')

import torch
import numpy as np

from typing import List
from sem_covid.services.sc_wrangling.data_cleaning import clean_fix_unicode, clean_remove_urls, \
    clean_remove_emails, clean_remove_currency_symbols, clean_remove_numbers, clean_text_from_specific_characters
from sem_covid.entrypoints.notebooks.topic_modeling.topic_modeling_wrangling.token_management import spacy_stop_words


class DocEmbeddingPipeline:
    """
        This pipeline aims to calculate embedding vectors for documents. The process is done in 5 steps:
        1. Load the data set.
        2. Prepare initial data set for cleaning process.
        3. Apply cleaning functions.
        4. Compute embedding vectors.
        5. Storage of calculated embedding vectors.
    """

    def __init__(self, store_registry, es_index_name: str, textual_columns: list, tokenizer, embedding_model,
                 doc_emb_feature_store_name: str):
        """
            Document embedding pipeline depends on the following parameters:
        :param store_registry: register of different types of storage
        :param es_index_name: elastic search index name for concrete data set
        :param textual_columns: textual columns names from concrete data set
        :param tokenizer: tokenizer used by the embedding model
        :param embedding_model: embedding model that will be used to calculate embedding documents
        :param doc_emb_feature_store_name: the name of the feature store for the calculated embeddings
        """
        self.store_registry = store_registry
        self.data_set = None
        self.es_index_name = es_index_name
        self.prepared_data_set = None
        self.textual_columns = textual_columns
        self.tokenizer = tokenizer
        self.embedding_model = embedding_model
        self.doc_emb_feature_store_name = doc_emb_feature_store_name

    def load_data_set(self):
        """
            This method performs the step of loading the required documents from the preconfigured data set.
        :return:
        """
        es_index_store = self.store_registry.es_index_store()
        self.data_set = es_index_store.get_dataframe(self.es_index_name)

    def prepare_data_set_for_cleaning(self):
        """
            This method prepares the data set for cleaning.
        :return:
        """
        self.prepared_data_set = self.data_set.dropna(subset=self.textual_columns)
        self.prepared_data_set['txt'] = self.prepared_data_set[self.textual_columns].agg(' '.join, axis=1)
        self.prepared_data_set.drop(self.textual_columns, axis=1, inplace=True)

    def apply_cleaning_functions(self):
        """
            This method prepares the textual data before calculating embeddings based on them.
        :return:
        """
        unused_characters = ["Download", "\\r", ">", "\n", "\\", "<", "''", "%", "...", "\'", '"', "(", ")",
                             "\n", "*", "1)", "2)", "3)", "[", "]", "-", "_", "\r", "=", "!", ",", ".", "?", ":", "/",
                             "+", ";"]

        self.prepared_data_set['txt'] = self.prepared_data_set['txt'].apply(clean_fix_unicode)
        self.prepared_data_set['txt'] = self.prepared_data_set['txt'].apply(clean_remove_urls, replace_with=' ')
        self.prepared_data_set['txt'] = self.prepared_data_set['txt'].apply(clean_remove_emails, replace_with=' ')
        self.prepared_data_set['txt'] = self.prepared_data_set['txt'].apply(clean_remove_currency_symbols,
                                                                            replace_with=' ')
        self.prepared_data_set['txt'] = self.prepared_data_set['txt'].apply(clean_remove_numbers, replace_with=' ')
        self.prepared_data_set['txt'] = self.prepared_data_set['txt'].apply(clean_text_from_specific_characters,
                                                                            characters=unused_characters)
        self.prepared_data_set['txt'] = self.prepared_data_set['txt'].apply(lambda x: self.remove_stop_words(x))
        self.prepared_data_set['txt'] = self.prepared_data_set['txt'].apply(lambda x: self.remove_short_words(x))
        self.prepared_data_set['txt'] = self.prepared_data_set['txt'].apply(lambda x: self.lemmatize_text(x))
        self.prepared_data_set['txt_splitted'] = self.prepared_data_set['txt'].apply(lambda x: self.get_split(x))

    def compute_embeddings(self):
        """
           This method performs the step of calculating embeddings based on the textual data in the data set.
        :return:
        """
        self.prepared_data_set['embedding'] = self.get_embeddings(self.tokenizer, self.embedding_model,
                                                                  self.prepared_data_set['txt_splitted'])
        self.prepared_data_set.drop('txt_splitted', axis=1, inplace=True)

    def store_embeddings(self):
        """
            This method performs the storage step of the calculated embeddings.
        :return:
        """
        es_index_store = self.store_registry.es_index_store()
        es_index_store.put_dataframe(index_name=self.doc_emb_feature_store_name,
                                     content=self.prepared_data_set)

    def execute(self):
        """
           This method performs the steps of the pipeline in the required order.
        :return:
        """
        self.load_data_set()
        self.prepare_data_set_for_cleaning()
        self.apply_cleaning_functions()
        self.compute_embeddings()
        self.store_embeddings()

    @staticmethod
    def remove_stop_words(txt: str) -> str:
        """
            This method aims to perform stop words removal.
        :param txt: the text from which stop words should be removed
        :return: the text without stop words
        """
        txt_no_stop_words = ' '.join([word for word in txt.split() if word.lower() not in spacy_stop_words])

        return txt_no_stop_words

    @staticmethod
    def remove_short_words(txt: str) -> str:
        """
            This method aims to perform short words removal.
        :param txt: the text from which short words should be removed
        :return: the text without short words
        """
        txt_no_short_words = ' '.join([word for word in txt.split() if len(word) > 3])

        return txt_no_short_words

    @staticmethod
    def lemmatize_text(txt: str) -> str:
        """
            This method aims to lemmatize text.
        :param txt: the text that should be lemmatized
        :return: the lemmatized text
        """
        doc = nlp(txt)
        lemmatized_text = ' '.join([token.lemma_ for token in doc])

        return lemmatized_text

    @staticmethod
    def get_split(txt: str) -> List[str]:
        """
            This method aims to divide the input text into smaller chunks.
        :param txt: the text that should be divided
        :return: a list of text chunks
        """
        chunks = []

        if len(txt.split()) <= 150:
            chunk = ' '.join(txt.split()[:150])
            chunks.append(chunk)
        else:
            n = len(txt.split()) // 100

            if n % 100 == 0:
                nr_of_chunks = n
            else:
                nr_of_chunks = n + 1

            for i in range(0, nr_of_chunks):
                if i == 0:
                    chunk = ' '.join(txt.split()[:150])
                    chunks.append(chunk)
                else:
                    chunk = ' '.join(txt.split()[i*100:i*100+150])
                    chunks.append(chunk)

        return chunks

    @staticmethod
    def get_embeddings(tokenizer, model, docs_splitted: List) -> List:
        """
            This method aims to compute document embeddings.
        :param tokenizer: the tokenizer used by the below model
        :param model: the model used for computing embeddings
        :param docs_splitted: a list with divided documents
        :return: a list of embedding vectors
        """
        embeddings = []

        for doc_splitted in docs_splitted:

            tmp_embeddings = []

            for chunk_of_doc in doc_splitted:
                ids_ = tokenizer.encode(chunk_of_doc)
                ids_ = torch.LongTensor(ids_)
                ids_ = ids_.unsqueeze(0)

                with torch.no_grad():
                    out = model(input_ids=ids_)

                hidden_states = out[2]

                last_four_layers = [hidden_states[i] for i in (-1, -2, -3, -4)]

                concat_hidden_states = torch.cat(tuple(last_four_layers), dim=-1)

                tmp_embedding = torch.mean(concat_hidden_states, dim=1).squeeze().numpy()

                tmp_embeddings.append(tmp_embedding)

            embedding = [np.mean(grouped_vals) for grouped_vals in zip(*tmp_embeddings)]

            embeddings.append(embedding)

        return embeddings
