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


@step("that I accessed the environment")
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

    # click on ambient
    btn__login = Button(By.XPATH, '//*[@id="app-container"]/div/div[2]/section/ul[1]/li[3]/div/a')
    btn__login.wait_until_clickable()
    btn__login.click()
    context.utilities.wait_until_element_visible(element, 20)

    # add group
    btn__login = Button(By.CLASS_NAME, 'float-right')
    btn__login.wait_until_clickable()
    btn__login.click()
    context.utilities.wait_until_element_visible(element, 20)

    context.driver.find_element(By.CLASS_NAME, 'se_name').send_keys("Ambiente")
    context.utilities.wait_until_element_visible(element, 20)

    context.driver.find_element(By.CLASS_NAME, 'se_order').send_keys("12345")
    context.driver.find_element(By.CLASS_NAME, 'se_order').send_keys(Keys.ENTER)
    context.utilities.wait_until_element_visible(element, 20)

#    context.driver.find_element(By.CLASS_NAME, 'btn.btn-primary.btn-lg.btn-multiple-state.btn-shadow').click()
#    context.utilities.wait_until_element_visible(element, 20)


@step("click on add environment")
def test(context):
    context.driver.find_element(By.CLASS_NAME, 'se_filterInput').send_keys("Ambiente")
    context.driver.find_element(By.CLASS_NAME, 'se_filterInput').send_keys(Keys.ENTER)

    btn__login = Button(By.CLASS_NAME, 'iconsminds-file-edit')
    btn__login.wait_until_clickable()
    btn__login.click()

    context.driver.find_element(By.CLASS_NAME, 'se_name').clear()

    context.driver.find_element(By.CLASS_NAME, 'se_name').send_keys("Ambiente alterado")

    # Click no Botão de salvar operação
    element = Link(By.CSS_SELECTOR, '#app-container > main > div > div > div:nth-child(2) > div > div >'
                                    ' div > div > div > div > form >'
                                    ' div.d-flex.justify-content-end.align-items-center > button')
    element.wait_until_clickable()
    element.scroll_element_into_view()
    element.click()


@step('a new environment will be created')
def test(context):
    # pesquisar operação
    context.driver.find_element(By.CLASS_NAME, 'se_filterInput').send_keys("Ambiente alterado")

    context.driver.find_element(By.CLASS_NAME, 'se_filterInput').send_keys(Keys.ENTER)

    # deletar grupo
    context.driver.find_element(By.CLASS_NAME, 'iconsminds-close').click()

    # deletar grupo
    element = Link(By.CLASS_NAME, 'btn.btn-danger.btn-sm')
    element.wait_until_clickable()
    element.scroll_element_into_view()
    element.click()
    context.utilities.wait_until_element_visible(element, 120)
