
import pandas as pd

from sem_covid.services.language_model_pipelines.language_model_pipeline import (add_space_between_dots_and_commas, apply_cleaning_functions,
                                                                                 LanguageModelPipeline)


def test_add_space_between_dots_and_commas():
    text = 'hibidi.hobiti,you.have.no.property'
    spacer = add_space_between_dots_and_commas(text)
    assert str == type(spacer)
    assert 'hibidi. hobiti, you. have. no. property' == spacer


def test_apply_cleaning_functions(transformed_pwdb_dataframe):
    textual_cleaning = apply_cleaning_functions(transformed_pwdb_dataframe['title'])
    assert textual_cleaning[0] == 'hardship case fund: safety net self employed'
    assert textual_cleaning[1] == 'state support tourism access finance'


def test_language_model_pipeline(transformed_pwdb_dataframe):

    unused_characters = ["\\r", ">", "\n", "\\", "<", "''", "%", "...", "\'", '"', "(", "\n", "*", "1)", "2)", "3)",
                         "[", "]", "-", "_", "\r", '®', '..']
    test_model_name = 'test_model'
    textual_data = ['title', 'background_info_description']
    test_model = [(transformed_pwdb_dataframe, textual_data)]
    language_model_pipeline = LanguageModelPipeline(test_model, test_model_name)

    extraction = language_model_pipeline.extract_textual_data()
    assert pd.Series == type(language_model_pipeline.documents_corpus)
    assert 2 == len(language_model_pipeline.documents_corpus)
    assert 'Hardship case fund: Safety net for self-employed' in language_model_pipeline.documents_corpus[0]
    assert 'State support for tourism - Access to finance' in language_model_pipeline.documents_corpus[1]

    cleaning = language_model_pipeline.clean_textual_data()
    for character in unused_characters:
        assert character not in language_model_pipeline.documents_corpus

    transformation = language_model_pipeline.transform_to_spacy_doc()
    assert 'hardship case fund: safety net self employed' in str(language_model_pipeline.documents_corpus[0])
    assert 'state support tourism access finance' in str(language_model_pipeline.documents_corpus[1])

    featuring = language_model_pipeline.extract_features()
    assert pd.Series == type(language_model_pipeline.documents_corpus)
    assert list == type(language_model_pipeline.documents_corpus[0])
    assert list == type(language_model_pipeline.documents_corpus[1])

