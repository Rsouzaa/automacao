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

    # add group
    btn__login = Button(By.XPATH, '//*[@id="app-container"]/main/div/div/div[1]/div/a')
    btn__login.wait_until_clickable()
    btn__login.click()
    context.utilities.wait_until_element_visible(element, 20)

    context.driver.find_element(By.CLASS_NAME, 'se_full_name').send_keys("Usuario teste")
    context.utilities.wait_until_element_visible(element, 20)

    context.driver.find_element(By.CLASS_NAME, 'se_username').send_keys("X236156")
    context.driver.find_element(By.CLASS_NAME, 'se_username').send_keys(Keys.ENTER)
    context.utilities.wait_until_element_visible(element, 20)

    context.driver.find_element(By.CLASS_NAME, 'se_password').send_keys("123456")
    context.driver.find_element(By.CLASS_NAME, 'se_password').send_keys(Keys.ENTER)
    context.utilities.wait_until_element_visible(element, 20)

    context.driver.find_element(By.CLASS_NAME, 'se_repeat_password').send_keys("123456")
    context.driver.find_element(By.CLASS_NAME, 'se_repeat_password').send_keys(Keys.ENTER)
    context.utilities.wait_until_element_visible(element, 20)


@step("new user is search")
def test(context):
    # localizar usuario
    context.driver.find_element(By.XPATH, '//*[@id="filterInput"]').send_keys("Usuario teste")
    context.driver.find_element(By.XPATH, '//*[@id="filterInput"]').send_keys(Keys.ENTER)

    btn__login = Button(By.CLASS_NAME, 'iconsminds-file-edit')
    btn__login.wait_until_clickable()
    btn__login.click()

    context.driver.find_element(By.CLASS_NAME, 'se_full_name').clear()

    context.driver.find_element(By.CLASS_NAME, 'se_full_name').send_keys("Usuario editado")

    # Click no Botão de salvar operação
    element = Link(By.CSS_SELECTOR, '#app-container > main > div > div > div:nth-child(2) > div > div >'
                                    ' div > div > div > div > form >'
                                    ' div.d-flex.justify-content-end.align-items-center > button')
    element.wait_until_clickable()
    element.scroll_element_into_view()
    element.click()


@step("it will be easier to delete or edit")
def test(context):
    # pesquisar usuario
    context.driver.find_element(By.XPATH, '//*[@id="filterInput"]').send_keys("X236156")
    context.driver.find_element(By.XPATH, '//*[@id="filterInput"]').send_keys(Keys.ENTER)

    btn__login = Button(By.CLASS_NAME, 'iconsminds-close')
    btn__login.wait_until_clickable()
    btn__login.click()
    context.utilities.wait_until_element_visible(btn__login, 120)

    # deletar usuario
    element = Link(By.CLASS_NAME, 'btn.btn-danger.btn-sm')
    element.wait_until_clickable()
    element.scroll_element_into_view()
    element.click()
    context.utilities.wait_until_element_visible(element, 120)
