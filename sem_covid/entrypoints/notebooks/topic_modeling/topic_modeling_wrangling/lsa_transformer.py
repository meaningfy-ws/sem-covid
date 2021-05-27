
from typing import List

from sklearn.decomposition import TruncatedSVD


def lsa_document_transformation(document_vectors: List, num_components: int) -> tuple:
    """
        this function is using sklearn library TruncatedSVD, which creates
        an LSA model based on document's vectors
        :num_components: the number of components created by tfidf vectorizer
        :return: lsa data and latent components
    """

    lsa_object = TruncatedSVD(n_components=num_components, n_iter=100, random_state=42)
    tfidf_lsa_data = lsa_object.fit_transform(document_vectors)
    sigma = lsa_object.singular_values_
    v_transpose = lsa_object.components_.T

    return tfidf_lsa_data, sigma, v_transpose
