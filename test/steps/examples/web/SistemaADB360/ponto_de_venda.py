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


@step("that a new unit will be registered")
def test(context):
    # retrair gerenciamentos
    element = Link(By.CSS_SELECTOR, '#app-container > nav > div.d-flex.align-items-center.navbar-left >'
                                    ' div:nth-child(1) > a.menu-button.d-none.d-md-block > div > svg.sub')
    element.wait_until_clickable()
    element.scroll_element_into_view()
    element.click()
    context.utilities.wait_until_element_visible(element, 20)

    # clicar no ponto de venda
    element = Link(By.CLASS_NAME, 'iconsminds-bank')
    element.wait_until_clickable()
    element.scroll_element_into_view()
    element.click()
    context.utilities.wait_until_element_visible(element, 20)

@step("the user searches the unit")
def test(context):
    # Adicionar nova unidade
    element = Link(By.XPATH, '//*[@id="app-container"]/main/div/div/div[1]/div/a')
    element.wait_until_clickable()
    element.scroll_element_into_view()
    element.click()
    context.utilities.wait_until_element_visible(element, 20)

    # localizar unidade
    element = context.driver.find_element(By.CSS_SELECTOR, "#filterInput").send_keys("VILA MADA")
    element.context.driver.find_element(By.CSS_SELECTOR, "#filterInput").send_keys(Keys.ENTER)

    context.utilities.wait_until_element_visible(element, 30)


@step("it will be easier to delete the unit")
def test(context):
    # deletar unidade
    element = Link(By.CLASS_NAME, 'iconsminds-close')
    element.wait_until_clickable()
    element.scroll_element_into_view()
    element.click()
    context.utilities.wait_until_element_visible(element, 20)

    # Botão para deletar loja
    context.driver.find_element(By.CLASS_NAME, "btn-danger").click()
    context.utilities.wait_until_element_visible(element, 40)
