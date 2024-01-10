@get
Feature: api
  Demo Api Example adb360

  @ge1
  Scenario Outline: request <>
  """
  Description of the <app_version> and <total_disk_size> capacity of the card
  """

    Given prepare the uri 'http://180.235.184.58:3000/api/self-defense' request with path 'get-all-info-devices'
    And prepare the method 'GET' request
    When send request
    And verify status code is '200'
    And verify value '<app_version>' of type 'str' in path key 'app_version'
    And verify value '<total_disk_size>' of type 'str' in path key 'total_disk_size'

    Examples:
    |app_version | total_disk_size |
    |3.0.6       | 28%             |
