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


@step("since I accessed monitoring")
def test(context):
    # search alarm event
    context.driver.find_element(By.CLASS_NAME, "se_all_filteer").send_keys("001-0011")
    context.driver.find_element(By.CLASS_NAME, "se_all_filteer").send_keys(Keys.ENTER)

    element = Link(By.CLASS_NAME, "simple-icon-arrow-right.pointer")
    element.wait_until_clickable()
    element.scroll_element_into_view()
    element.click()

    element = Link(By.CLASS_NAME, "simple-icon-arrow-down.pointer")
    element.wait_until_clickable()
    element.scroll_element_into_view()
    element.click()


@step("carry out treatment on the monitoring screen")
def test(context):
    element = Link(By.CLASS_NAME, "simple-icon-book-open.px-1.pointer")
    element.wait_until_clickable()
    element.scroll_element_into_view()
    element.click()


@step("all events are being analyzed")
def test(context):
    context.btn__menu = Button(By.CLASS_NAME, "btn.btn-tertiary.mt-2.btn-secondary").click()

    context.btn__menu = Button(By.CLASS_NAME, "btn.float-right.btn-primary.btn-sm").click()


    # element = Link(By.CLASS_NAME, "btn.float-right.btn-primary.btn-sm")
    # element.wait_until_clickable()
    # element.scroll_element_into_view()
    # element.click()
    # context.utilities.wait_until_element_visible(element, 20)
