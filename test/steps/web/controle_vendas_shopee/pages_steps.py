"""Checks visible tabs and headings without changing application data."""

from behave import step
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


TABS = {'Painel', 'Vendas', 'Estoque', 'Investimentos'}
HEADINGS = {'Seu negócio em números', 'Vendas recentes', 'Histórico de vendas',
            'Produtos e estoque', 'Investimentos do negócio'}


@step('I open the "{tab}" tab in Controle Vendas Shopee')
def open_tab(context, tab):
    assert tab in TABS, f'Aba desconhecida: {tab}'
    locator = (By.XPATH, f"//*[self::button or @role='tab'][normalize-space()='{tab}']")
    WebDriverWait(context.driver, 20).until(ec.element_to_be_clickable(locator)).click()


@step('I should see the "{heading}" heading in Controle Vendas Shopee')
def see_heading(context, heading):
    assert heading in HEADINGS, f'Seção desconhecida: {heading}'
    locator = (By.XPATH, f"//*[self::h1 or self::h2 or self::h3 or self::h4][normalize-space()='{heading}']")
    WebDriverWait(context.driver, 20).until(ec.visibility_of_element_located(locator))
