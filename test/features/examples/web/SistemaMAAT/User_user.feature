@Profiling
Feature: Profiling
  maat of maat.com home

  Background: access to maat system profiles
    Given that I access the application '${{datas:web}}'
    When username '${{users:users.userType1.username}}' password '${{users:users.userType1.password}}'
    Then login to level 1 successful

@User_user
  Scenario: User
    Given that a new user will be created
    When nem user is search
    Then it will be easier to delete or edit
