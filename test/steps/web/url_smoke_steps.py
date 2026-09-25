import os

from behave import step
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


@step('the target page should contain visible text')
def target_page_has_content(context):
    body = WebDriverWait(context.driver, 20).until(
        lambda driver: driver.find_element(By.TAG_NAME, 'body').text.strip())
    normalized = body.casefold()
    blocks = ('sorry, you have been blocked', 'you are unable to access',
              'verify you are human', 'checking your browser', 'access denied')
    assert not any(message in normalized for message in blocks), 'A URL abriu uma página de bloqueio.'
    expected = os.environ.get('AUTOMACAO_EXPECTED_TEXT', '').strip()
    if expected:
        assert expected.casefold() in normalized, f'O texto {expected!r} não apareceu na página.'
