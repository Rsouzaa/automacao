@url_smoke
Feature: Verificar URL informada no painel local

  Scenario: Página carrega conteúdo visível
    Given access to the web application '${{controle_vendas_shopee:web}}'
    Then the target page should contain visible text
