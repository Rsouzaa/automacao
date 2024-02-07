@Profiling
Feature: Profiling
  adb of adb360000.com home

  Background: access to adb 360 system profiles
    Given that I access the application '${{datas:web}}'
    When username '${{users:users.userType10.username}}' password '${{users:users.userType10.password}}'
    Then login to level 1 successful


@monitoring
  Scenario: alarm Monitoring
    Given since I accessed monitoring
    When carry out treatment on the monitoring screen
    Then all events are being analyzed


@grupo_agencia
  Scenario: group created
    Given I accessed the group
    When add name to group
    Then a new user group will be created


@grupo_operacao
  Scenario: operation group
    Given I accessed the operation group
    When link a name to the group
    Then a new operation group will be created


@ponto_de_venda
  Scenario: Point of sale
    Given that a new unit will be registered
    When the user searches the unit
    Then it will be easier to delete the unit


@usuario
  Scenario: User
    Given that a new user will be created
    When new user is search
    Then it will be easier to delete or edit


@grupo_ambiente
  Scenario: ambient
    Given that I accessed the environment
    When click on add environment
    Then a new environment will be created


@multiplos_alarme
  Scenario: alarm multiple
    Given that the multiple alarm will be validated
    When Alarms are clicked
    Then The information will be edited

@alarmes_desativados
  Scenario: multiple disabled
    Given that the alarm has been deactivated
    When selected by user
    Then the event will no longer be generated

@feriado
  Scenario: holiday
    Given that the holiday
    When created it will be used
    Then a trip occurs in the unit

@regra_alarme
  Scenario: alarm rule
    Given a new alarm rule will be created
    When Including the information
    Then the rule can be used

@criticidade_alarme
  Scenario: alarm criticality
    Given that various types of criticality will be created
    When the user needs to use a new template
    Then then there will be several models available

@operacao_alarme
  Scenario: alarm operation
    Given
    When
    Then

