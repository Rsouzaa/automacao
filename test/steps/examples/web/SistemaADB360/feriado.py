# -*- coding: utf-8 -*-
"""
Examples of behave Step usage in TalosBDD.
"""
import logging

from behave import use_step_matcher, step
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from arc.page_elements import Button, Text, Link
from arc.contrib.steps.web import appian_keywords
from test.helpers.page_objects.examples.san_web_demo.po_san import SanPageObject
from test.helpers.page_objects.examples.san_web_demo.po_menu import MenuPageObject, InputText

logger = logging.getLogger(__name__)
use_step_matcher("re")


@step("that the holiday")
def test(context):
    # retract management
    btn__login = Button(By.CSS_SELECTOR, '#app-container > nav > div.d-flex.align-items-center.navbar-left >'
                                         ' div:nth-child(1) > a.menu-button.d-none.d-md-block > div > svg.sub')
    btn__login.wait_until_clickable()
    btn__login.click()

    # click on management
    element = Link(By.CSS_SELECTOR, '#app-container > div > div.main-menu > section > ul > li:nth-child(1) > div > a')
    element.wait_until_clickable()
    element.scroll_element_into_view()
    element.click()

    context.utilities.wait_until_element_visible(element, 20)


@step("created it will be used")
def test(context):
    # click on feriado
    btn__login = Button(By.XPATH, '//*[@id="app-container"]/div/div[2]/section/ul[1]/li[6]/div/a')
    btn__login.wait_until_clickable()
    btn__login.click()
    # context.utilities.wait_until_element_visible(element, 20)

    btn__login = Button(By.CLASS_NAME, 'multiselect__single')
    btn__login.wait_until_clickable()
    btn__login.click()
    # context.utilities.wait_until_element_visible(element, 20)


@step('a trip occurs in the unit')
def test(context):
    context.driver.find_element(By.CLASS_NAME, 'se_filterInput').send_keys("SAO PAULO")
    context.driver.find_element(By.CLASS_NAME, 'se_filterInput').send_keys(Keys.ENTER)

    element = Link(By.XPATH, '//*[@id="app-container"]/main/div/div/div[2]/div/div/div/div[4]/div[2]/ul/li[6]/button')
    element.wait_until_clickable()
    element.scroll_element_into_view()
    element.click()
    context.utilities.wait_until_element_visible(element, 20)
