from arc.core.driver.driver_install import InstallDriver


def test_move_driver_replaces_the_local_driver(tmp_path):
    downloaded_driver = tmp_path / 'downloaded' / 'chromedriver.exe'
    downloaded_driver.parent.mkdir()
    downloaded_driver.write_text('new driver', encoding='utf-8')
    target_directory = tmp_path / 'drivers'
    target_directory.mkdir()
    target_driver = target_directory / 'chromedriver.exe'
    target_driver.write_text('old driver', encoding='utf-8')

    installer = InstallDriver('chromedriver.exe')
    installer.drivers_path = str(target_directory)
    installer._move_driver(str(downloaded_driver))

    assert downloaded_driver.exists()
    assert target_driver.read_text(encoding='utf-8') == 'new driver'