
from sem_covid.services.language_model_pipeline import (add_space_between_dots_and_commas, apply_cleaning_functions,
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
    test_model_name = 'test_model'
    textual_data = ['title']
    test_model = [(transformed_pwdb_dataframe, textual_data)]
    language_model_pipeline = LanguageModelPipeline(test_model, test_model_name)
