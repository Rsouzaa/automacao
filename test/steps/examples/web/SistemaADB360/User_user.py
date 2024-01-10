# -*- coding: utf-8 -*-
"""
Examples of behave Step usage in TalosBDD.
"""
import logging

from behave import use_step_matcher, step
from selenium.webdriver.common.by import By

from arc.page_elements import Button, Text, Link
from arc.contrib.steps.web import appian_keywords
from test.helpers.page_objects.examples.san_web_demo.po_san import SanPageObject
from test.helpers.page_objects.examples.san_web_demo.po_menu import MenuPageObject, InputText

logger = logging.getLogger(__name__)
use_step_matcher("re")


@step("that I access the application '(?P<url>.+)'")
def test(context, url):
    logger.info(f'Accessing the url: {url}')
    context.driver.get(url)


@step("username '(?P<username>.+)' password '(?P<password>.+)'")
def test(context, username, password):
    inp__username = InputText(By.CLASS_NAME, 'se_user_user')
    inp__password = InputText(By.CLASS_NAME, 'se_user_password')

    inp__username.wait_until_visible()
    inp__username.text = username
    inp__password.text = password

    btn__login = Button(By.CSS_SELECTOR, "#root > main > div > div > div > "
                                         "div >div.form-side > form > div > button > span.label")
    btn__login.wait_until_clickable()
    btn__login.click()


@step("login to level 1 successful")
def test(context):
    pass
