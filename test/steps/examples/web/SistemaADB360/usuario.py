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


@step("that a new user will be created")
def test(context):
    # retrair gerenciamentos
    element = Link(By.CSS_SELECTOR, '#app-container > nav > div.d-flex.align-items-center.navbar-left >'
                                    ' div:nth-child(1) > a.menu-button.d-none.d-md-block > div > svg.sub')
    element.wait_until_clickable()
    element.scroll_element_into_view()
    element.click()
    context.utilities.wait_until_element_visible(element, 200)

    # clicar em usuario
    element = Link(By.CSS_SELECTOR, '#app-container > div > div.main-menu >'
                                    ' section > ul > li:nth-child(4) > div > a')
    element.wait_until_clickable()
    element.scroll_element_into_view()
    element.click()
    context.utilities.wait_until_element_visible(element, 200)


@step("new user is search")
def test(context):
    # localizar usuario
    context.driver.find_element(By.XPATH, '//*[@id="filterInput"]').send_keys("TestSoftware")
    context.driver.find_element(By.XPATH, '//*[@id="filterInput"]').send_keys(Keys.ENTER)

    # deletar usuario
    context.driver.find_element(By.CLASS_NAME, 'iconsminds-close').click()
    context.driver.find_element(By.CLASS_NAME, 'btn.btn-danger.btn-sm').click()

    # Adicionar novo usuario
    context.driver.find_element(By.XPATH, '//*[@id="app-container"]/main/div/div/div[1]/div/a').click()

    # nome completo
    context.driver.find_element(By.CLASS_NAME, 'se_full_name').send_keys("Test")
    context.driver.find_element(By.CLASS_NAME, 'se_full_name').send_keys(Keys.ENTER)

    # matricula
    context.driver.find_element(By.CLASS_NAME, 'se_username').send_keys("X236156")
    context.driver.find_element(By.CLASS_NAME, 'se_username').send_keys(Keys.ENTER)

    # senha
    context.driver.find_element(By.CLASS_NAME, 'se_password').send_keys("123456")
    context.driver.find_element(By.CLASS_NAME, 'se_password').send_keys(Keys.ENTER)

    # repetir senha
    context.driver.find_element(By.CLASS_NAME, 'se_repeat_password').send_keys("123456")
    context.driver.find_element(By.CLASS_NAME, 'se_repeat_password').send_keys(Keys.ENTER)


@step("it will be easier to delete or edit")
def test(context):
    # localizar usuario
    context.driver.find_element(By.XPATH, '//*[@id="filterInput"]').click()
    context.driver.find_element(By.XPATH, '//*[@id="filterInput"]').send_keys("Test")
    context.driver.find_element(By.XPATH, '//*[@id="filterInput"]').send_keys(Keys.ENTER)

    # editar usuario
    context.driver.find_element(By.CLASS_NAME, 'iconsminds-file-edit').click()

    # edição usuario
    context.driver.find_element(By.CLASS_NAME, 'se_full_name').send_keys("Software")
    context.driver.find_element(By.CLASS_NAME, 'se_full_name').send_keys(Keys.ENTER)

    # salvar
    context.driver.find_element(By.CLASS_NAME, 'btn.btn-primary.btn-lg.btn-multiple-state.btn-shadow').click()
