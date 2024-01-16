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

    element = context.driver.find_element(By.XPATH, '//*[@id="app-container"]/div/div[1]/section/ul/li[7]/div/a')
    element.location_once_scrolled_into_view

    # clicar no ponto de venda
    element = Link(By.CLASS_NAME, 'iconsminds-bank')
    element.wait_until_clickable()
    element.scroll_element_into_view()
    element.click()
    # context.utilities.wait_until_element_visible(element, 50)


@step("the user searches the unit")
def test(context):
    btn__login = Button(By.CLASS_NAME, 'iconsminds-add')
    btn__login.wait_until_clickable()
    btn__login.click()

    # Cadastro ponto de venda
    context.driver.find_element(By.CLASS_NAME, 'se_uniorg').send_keys("123-4567")
    context.driver.find_element(By.CLASS_NAME, 'se_uniorg').send_keys(Keys.ENTER)

    context.driver.find_element(By.CLASS_NAME, 'se_regional').send_keys("Santo Amaro")
    context.driver.find_element(By.CLASS_NAME, 'se_regional').send_keys(Keys.ENTER)

    context.driver.find_element(By.CLASS_NAME, 'se_name').send_keys("Agencia teste")
    context.driver.find_element(By.CLASS_NAME, 'se_name').send_keys(Keys.ENTER)

    context.driver.find_element(By.CLASS_NAME, 'se_parent').send_keys("teste ok")
    context.driver.find_element(By.CLASS_NAME, 'se_parent').send_keys(Keys.ENTER)

    context.driver.find_element(By.CLASS_NAME, 'se_gg').send_keys("Roberto Souza")
    context.driver.find_element(By.CLASS_NAME, 'se_gg').send_keys(Keys.ENTER)

    context.driver.find_element(By.CLASS_NAME, 'se_phone_gg').send_keys("(11) 93212-2342")
    context.driver.find_element(By.CLASS_NAME, 'se_phone_gg').send_keys(Keys.ENTER)

    context.driver.find_element(By.CLASS_NAME, 'se_ga').send_keys("Jane Germano")
    context.driver.find_element(By.CLASS_NAME, 'se_ga').send_keys(Keys.ENTER)

    context.driver.find_element(By.CLASS_NAME, 'se_phone_ga').send_keys("(11) 00922-2322")
    context.driver.find_element(By.CLASS_NAME, 'se_phone_ga').send_keys(Keys.ENTER)

    context.driver.find_element(By.CLASS_NAME, 'se_sa').send_keys("Jayme Fernandes")
    context.driver.find_element(By.CLASS_NAME, 'se_sa').send_keys(Keys.ENTER)

    context.driver.find_element(By.CLASS_NAME, 'se_phone_sa').send_keys("(19) 87321-3221")
    context.driver.find_element(By.CLASS_NAME, 'se_phone_sa').send_keys(Keys.ENTER)

    context.driver.find_element(By.CLASS_NAME, 'se_sra').send_keys("Marcus Pimentel")
    context.driver.find_element(By.CLASS_NAME, 'se_sra').send_keys(Keys.ENTER)

    context.driver.find_element(By.CLASS_NAME, 'se_phone_sra').send_keys("(22) 94563-9032")
    context.driver.find_element(By.CLASS_NAME, 'se_phone_sra').send_keys(Keys.ENTER)

    context.driver.find_element(By.CLASS_NAME, 'se_state').send_keys("SAO PAULO")
    context.driver.find_element(By.CLASS_NAME, 'se_state').send_keys(Keys.ENTER)
    context.driver.find_element(By.CLASS_NAME, 'se_state').click()

    context.driver.find_element(By.CLASS_NAME, 'se_address').send_keys("Rua Interlagos")
    context.driver.find_element(By.CLASS_NAME, 'se_address').send_keys(Keys.ENTER)

    context.driver.find_element(By.CLASS_NAME, 'se_district').send_keys("Silveira")
    context.driver.find_element(By.CLASS_NAME, 'se_district').send_keys(Keys.ENTER)

    context.driver.find_element(By.CLASS_NAME, 'se_phone').send_keys("4162-9464")
    context.driver.find_element(By.CLASS_NAME, 'se_phone').send_keys(Keys.ENTER)

    context.driver.find_element(By.CLASS_NAME, 'se_phone_police').send_keys("190")
    context.driver.find_element(By.CLASS_NAME, 'se_phone_police').send_keys(Keys.ENTER)

    context.driver.find_element(By.CLASS_NAME, 'se_code').send_keys("06448-200")
    context.driver.find_element(By.CLASS_NAME, 'se_code').send_keys(Keys.ENTER)

    context.driver.find_element(By.CLASS_NAME, 'se_portage').send_keys("A")
    context.driver.find_element(By.CLASS_NAME, 'se_portage').send_keys(Keys.ENTER)

    # context.driver.find_element(By.CLASS_NAME, 'se_password').send_keys("RADAR")
    # context.driver.find_element(By.CLASS_NAME, 'se_password').send_keys(Keys.ENTER)

    # context.driver.find_element(By.CLASS_NAME, 'se_password_check').send_keys("GERACAO DIGITAL")
    # context.driver.find_element(By.CLASS_NAME, 'se_password_check').send_keys(Keys.ENTER)

    # element = Link(By.CSS_SELECTOR, '#app-container > main > div > div > div:nth-child(2) >'
    #                                ' div > div > div > div > div > div > form >'
    #                                ' div.d-flex.justify-content-end.align-items-center > button')
    # element.wait_until_clickable()
    # element.scroll_element_into_view()
    # element.click()
    # context.utilities.wait_until_element_visible(element, 60)

@step("it will be easier to delete the unit")
def test(context):
    context.driver.find_element(By.CLASS_NAME, 'se_filterInput.form-control').send_keys("123-4567")
    context.driver.find_element(By.CLASS_NAME, 'se_filterInput.form-control').send_keys(Keys.ENTER)

    btn__login = Button(By.CLASS_NAME, 'iconsminds-file-edit')
    btn__login.wait_until_clickable()
    btn__login.click()

    context.driver.find_element(By.CLASS_NAME, 'se_regional').clear()

    context.driver.find_element(By.CLASS_NAME, 'se_regional').send_keys("GERACAO Radar")

    # Click no Botão de salvar operação
    element = Link(By.CSS_SELECTOR, '#app-container > main > div > div > div:nth-child(2) > div > div >'
                                    ' div > div > div > div > form >'
                                    ' div.d-flex.justify-content-end.align-items-center > button')
    element.wait_until_clickable()
    element.scroll_element_into_view()
    element.click()

    context.driver.find_element(By.CLASS_NAME, 'se_filterInput.form-control').send_keys("123-4567")
    context.driver.find_element(By.CLASS_NAME, 'se_filterInput.form-control').send_keys(Keys.ENTER)

    # deletar unidade
    element = Link(By.CLASS_NAME, 'iconsminds-close')
    element.wait_until_clickable()
    element.scroll_element_into_view()
    element.click()
    context.utilities.wait_until_element_visible(element, 20)

    # Botão para deletar loja
    element = Link(By.CLASS_NAME, 'btn.btn-danger.btn-sm')
    element.wait_until_clickable()
    element.scroll_element_into_view()
    element.click()
    context.utilities.wait_until_element_visible(element, 120)
