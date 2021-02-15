from src.data_cleaner import prepare_text_for_cleaning


def test_data_cleaner():
    test_string = 'Hello World123 https:// [Dealing]'

    actual = prepare_text_for_cleaning(test_string)
    expected_text = ['hello', 'https', '']

    assert len(actual) == len(expected_text)
    assert all([a == b for a, b in zip(actual, expected_text)])
