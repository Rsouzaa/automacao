from selenium.webdriver.common.by import By

from arc.page_elements import Text
from arc.page_objects.page_object import PageObject


class ControleVendasShopeeDashboardPage(PageObject):
    def init_page_elements(self):
        self.dashboard = Text(By.XPATH, "//h2[normalize-space()='Seu negócio em números']", wait=True)
