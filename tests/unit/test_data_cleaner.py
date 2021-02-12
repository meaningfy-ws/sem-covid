from src.data_cleaner import cleaning


def test_data_cleaner():
    test_string = 'Hello World123 https:// [Dealing]'

    actual = cleaning(test_string)

    expected_text = ['hello'], ['world'], ['deal']

    assert len(actual) == len(expected_text)
