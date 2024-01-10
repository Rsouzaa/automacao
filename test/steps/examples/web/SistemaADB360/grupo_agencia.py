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


@step("I accessed the group")
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

    # click on agency
    btn__login = Button(By.XPATH, '//*[@id="menu_0_0"]/ul/li[1]/div/a/span')
    btn__login.wait_until_clickable()
    btn__login.click()

    context.utilities.wait_until_element_visible(element, 20)


@step("add name to group")
def test(context):
    # add group
    btn__login = Button(By.CLASS_NAME, 'iconsminds-add')
    btn__login.wait_until_clickable()
    btn__login.click()

    context.driver.find_element(By.CLASS_NAME, 'se_group_name').send_keys("SUPORTE TECNICO")

    context.driver.find_element(By.CLASS_NAME, 'se_user').send_keys("X218090")
    context.driver.find_element(By.CLASS_NAME, 'se_user').send_keys(Keys.ENTER)

    context.driver.find_element(By.CLASS_NAME, 'multiselect.se_office').send_keys("003-0001")
    context.driver.find_element(By.CLASS_NAME, 'multiselect.se_office').send_keys(Keys.ENTER)


@step('a new user group will be created')
def test(context):
    btn__login = Button(By.CSS_SELECTOR, '#app-container > main > div > div > div:nth-child(2) >'
                                         ' div > div > div > div > div > div > form > div > button')
    btn__login.wait_until_clickable()
    btn__login.click()
