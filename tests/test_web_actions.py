from arc.contrib.web import assert_text, fill_input, login, upload_file


class FakeInput:
    def __init__(self, text=''):
        self.text = text
        self.clear_calls = 0

    def clear(self):
        self.clear_calls += 1
        self.text = ''


class FakeButton:
    def __init__(self):
        self.click_calls = 0

    def click(self):
        self.click_calls += 1
        return self


def test_fill_input_replaces_existing_value():
    field = FakeInput('old value')

    result = fill_input(field, 'new value')

    assert result is field
    assert field.clear_calls == 1
    assert field.text == 'new value'


def test_login_fills_credentials_and_submits():
    username = FakeInput()
    password = FakeInput()
    submit = FakeButton()

    result = login(username, password, submit, 'tester', 'secret')

    assert result is submit
    assert username.text == 'tester'
    assert password.text == 'secret'
    assert submit.click_calls == 1


def test_upload_file_uses_absolute_path(tmp_path):
    file_path = tmp_path / 'evidence.txt'
    file_path.write_text('evidence', encoding='utf-8')
    file_input = FakeInput()

    upload_file(file_input, file_path)

    assert file_input.text == str(file_path.resolve())


def test_assert_text_supports_exact_and_partial_matching():
    element = FakeInput('Execution completed successfully')

    assert assert_text(element, 'Execution completed successfully') == element.text
    assert assert_text(element, 'completed', contains=True) == element.text