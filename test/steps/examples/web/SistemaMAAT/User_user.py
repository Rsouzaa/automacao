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
    # login / senha
    inp__username = InputText(By.XPATH, '//*[@id="__BVID__29"]')
    inp__password = InputText(By.XPATH, '//*[@id="__BVID__31"]')

    inp__username.wait_until_visible()
    inp__username.text = username
    inp__password.text = password

    # login de acesso
    btn__login = Button(By.CLASS_NAME, "btn.btn-primary.btn-block")
    btn__login.wait_until_clickable()
    btn__login.click()


@step("login to level 1 successful")
def test(context):
    # validação de acesso
    element = Link(By.CSS_SELECTOR, "#menu-dashboards")
    element.wait_until_clickable()
    element.scroll_element_into_view()
    element.click()

    # Confirmação de acesso
    btn__login = Button(By.CSS_SELECTOR, '#menu-dashboards')
    btn__login.wait_until_clickable()
    btn__login.click()
