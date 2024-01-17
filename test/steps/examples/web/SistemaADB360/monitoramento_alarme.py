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
    # relogio
    element = Link(By.CLASS_NAME, 'simple-icon-clock')
    element.wait_until_clickable()
    element.scroll_element_into_view()
    element.click()
    context.utilities.wait_until_element_visible(element, 20)

    # criação de evento manual
    element = Link(By.CLASS_NAME, 'btn.se_manual_event.btn-primary')
    element.wait_until_clickable()
    element.scroll_element_into_view()
    element.click()

    element = Link(By.CLASS_NAME, 'multiselect.se_manual_event_creation.multiselect--active')
    element.wait_until_clickable()
    element.scroll_element_into_view()
    element.click()

    context.driver.find_element(By.CLASS_NAME, 'multiselect.se_manual_event_creation').send_keys("004-0004")
    context.driver.find_element(By.CLASS_NAME, 'multiselect.se_manual_event_creation').send_keys(Keys.ENTER)
    context.driver.find_element(By.CLASS_NAME, 'multiselect.se_manual_event_creation').click()

    context.driver.find_element(By.CLASS_NAME, 'multiselect.se_event_type').send_keys("GERADOR DE NEBLINA")
    context.driver.find_element(By.CLASS_NAME, 'multiselect.se_event_type').send_keys(Keys.ENTER)
    context.driver.find_element(By.CLASS_NAME, 'multiselect.se_event_type').click()

    context.driver.find_element(By.CLASS_NAME, 'multiselect.se_criticality').send_keys("Normal")
    context.driver.find_element(By.CLASS_NAME, 'multiselect.se_criticality').send_keys(Keys.ENTER)
    context.driver.find_element(By.CLASS_NAME, 'multiselect.se_criticality').click()

    context.driver.find_element(By.CLASS_NAME, "se_note.form-control").send_keys("Alarme criado com sucesso")
    context.driver.find_element(By.CLASS_NAME, "se_note.form-control").send_keys(Keys.ENTER)

    # salvar evento
    btn__login = Button(By.XPATH, '//*[@id="modalManualEvents___BV_modal_footer_"]/div/button[1]')
    btn__login.wait_until_clickable()
    btn__login.click()

    # relogio
    element = Link(By.CLASS_NAME, 'simple-icon-clock')
    element.wait_until_clickable()
    element.scroll_element_into_view()
    element.click()
    context.utilities.wait_until_element_visible(element, 20)

    # redistribuir evento
    element = Link(By.CLASS_NAME, 'btn.se_transaction.btn-primary')
    element.wait_until_clickable()
    element.scroll_element_into_view()
    element.click()

    # botao sim
    btn__login = Button(By.CLASS_NAME, 'btn.btn-danger.btn-sm')
    btn__login.wait_until_clickable()
    btn__login.click()

    # relogio
    element = Link(By.CLASS_NAME, 'theme-button.se_options')
    element.wait_until_clickable()
    element.scroll_element_into_view()
    element.click()
    context.utilities.wait_until_element_visible(element, 20)

    # operadores online
    element = Link(By.CLASS_NAME, 'btn.se_users.btn-primary')
    element.wait_until_clickable()
    element.scroll_element_into_view()
    element.click()

    # pesquisar usuario online
    context.driver.find_element(By.CLASS_NAME, "se_filter_filter").send_keys("operador 1")
    context.driver.find_element(By.CLASS_NAME, "se_filter_filter").send_keys(Keys.ENTER)

    # cancelar
    element = Link(By.CLASS_NAME, 'btn.float-right.btn-primary.btn-sm')
    element.wait_until_clickable()
    element.scroll_element_into_view()
    element.click()

    # relogio
    element = Link(By.CLASS_NAME, 'theme-button.se_options')
    element.wait_until_clickable()
    element.scroll_element_into_view()
    element.click()
    context.utilities.wait_until_element_visible(element, 20)

    # Tramitações Vinculadas
    element = Link(By.CLASS_NAME, 'btn.se_all_trasaction.btn-primary.blink')
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
