
from sem_covid.services.pos_extraction import POSExtraction


def test_pos_extraction(common_word2vec_model):
    extractor = POSExtraction(common_word2vec_model, pos=['NOUN'])

    pos_filter = extractor.filter_by_pos()
    assert list == type(pos_filter)
    assert ['system', 'graph', 'trees', 'user', 'minors', 'time', 'computer', 'interface'] == pos_filter

    selection = extractor.select_key_words(['system', 'trees'])
    assert list == type(selection)
    assert ['system', 'trees'] == selection

    pos_index = extractor.extract_pos_index()
    assert list == type(pos_index)
    assert [0, 1, 2, 3, 4, 6, 9, 10] == pos_index

    pos_embeddings = extractor.extract_pos_embeddings()
    assert list == type(pos_embeddings)

