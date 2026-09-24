from behave import step

from test.helpers.page_objects.controle_vendas_shopee.login_page import ControleVendasShopeeDashboardPage


@step('I should see the Controle Vendas Shopee dashboard')
def see_dashboard(context):
    page = ControleVendasShopeeDashboardPage(context)
    page.dashboard.wait_until_visible()
