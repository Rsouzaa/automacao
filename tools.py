import configparser
import json
import time
import traceback
import datetime
import typer
import os
import sys
import shutil
import requests
from pathlib import Path

from rich import print
from rich.table import Table
from zipfile import ZipFile
from arc.core.behave.env_utils import _generate_html_reports, prepare_json_data  # noqa
from arc.core.test_method.exceptions import TalosReportException
from arc.reports.pdf.create_report import CreatePDF
from arc.contrib.tools.web_template import create_web_template
from arc.contrib.tools.system_catalog import register_system
from arc.contrib.tools.api_template import create_api_template
from settings import settings
from rich.progress import Progress, SpinnerColumn, TextColumn
from subprocess import call

try:
    from arc.reports.doc.create_report import CreateDOC
    from arc.core.driver.driver_install import InstallDriver
    from arc.contrib.tools.crypto.crypto import encode, decode
    from arc.integrations.alm import alm3_properties
except (Exception,):
    print('[bold red]Error![/bold red] arc folder does not exist, update core to restore it!')

BASE_PATH = settings.BASE_PATH
OUTPUT_PATH = os.path.join(BASE_PATH, "output")
TEMP_PATH = os.path.join(OUTPUT_PATH, ".temp")
ZIP_PATH = os.path.join(TEMP_PATH, "test.zip")

app = typer.Typer()


@app.command()
def update_core(token: str = typer.Option(...), version: str = typer.Option(None)):
    if not version or version == 'latest':
        url = 'https://github.alm.europe.cloudcenter.corp/sgt-talos/python-talos-talos-bdd/archive/refs/heads/master.zip'
    else:
        base_url = 'https://github.alm.europe.cloudcenter.corp/sgt-talos/python-talos-talos-bdd/archive/refs'
        url = f"{base_url}/tags/{version}.zip"

    def create_temp_folder():
        """ Check if /output/.temp directory exists or create it."""
        print("[bold blue]Info![/bold blue] Creating temp folder.")
        if not os.path.exists(TEMP_PATH):
            os.makedirs(TEMP_PATH, exist_ok=True)
        else:
            shutil.rmtree(TEMP_PATH, ignore_errors=True)
            os.makedirs(TEMP_PATH, exist_ok=True)
        print('[bold blue]Info![/bold blue] Temp folder created.')
        progress1.update(task1, advance=20)

    def delete_temp_folder():
        """ Delete /.temp folder at the end"""
        if os.path.exists(TEMP_PATH):
            shutil.rmtree(TEMP_PATH, ignore_errors=True)
            print('[bold blue]Info![/bold blue] Temp folder has been deleted.')
        progress1.update(task1, advance=20)

    def github_request():
        print('[bold blue]Info![/bold blue] Making request to Github.')
        headers = {'Authorization': 'token ' + token}
        response = requests.get(url, headers=headers, stream=True, timeout=(10, 60))
        response.raise_for_status()
        print('[bold blue]Info![/bold blue] Request made successfully.')
        progress1.update(task1, advance=20)
        return response

    def download_zip(response):
        with open(ZIP_PATH, 'wb') as fd:
            for chunk in response.iter_content(chunk_size=1024):
                fd.write(chunk)
        progress1.update(task1, advance=10)
        print("[bold blue]Info![/bold blue] Zip file has been downloaded.")

    def extract_zip():
        print("[bold blue]Info![/bold blue] Extracting zip file.")
        with ZipFile(ZIP_PATH, "r") as zip_ref:
            temp_directory = Path(TEMP_PATH).resolve()
            for member in zip_ref.infolist():
                member_path = (temp_directory / member.filename).resolve()
                if temp_directory not in member_path.parents and member_path != temp_directory:
                    raise ValueError(f"Invalid archive path: {member.filename}")
            zip_ref.extractall(TEMP_PATH)
        print("[bold blue]Info![/bold blue] Zip file has been extracted.")
        progress1.update(task1, advance=20)

    def move_download_files():
        directories = [path for path in Path(TEMP_PATH).iterdir() if path.is_dir()]
        if len(directories) != 1:
            raise ValueError('The downloaded archive must contain a single root directory.')
        unzip_path = directories[0]
        files_to_move = ["changelog.md", "README.md", "requirements.txt", "VERSION", ".gitignore"]
        directories_to_move = ["arc"]
        for file in files_to_move:
            print(f"[bold blue]Info![/bold blue] Moving the file: {file}.")
            shutil.copyfile(unzip_path / file, Path(BASE_PATH) / file)
        for directory in directories_to_move:
            print(f"[bold blue]Info![/bold blue] Moving the files from the {directory} folder.")
            target = Path(BASE_PATH) / directory
            backup = Path(BASE_PATH) / f".{directory}.backup"
            if target.exists():
                if backup.exists():
                    shutil.rmtree(backup)
                target.replace(backup)
                shutil.move(str(unzip_path / directory), str(target))
                shutil.rmtree(backup, ignore_errors=True)
            else:
                shutil.move(str(unzip_path / directory), str(target))
        progress1.update(task1, advance=10)

    with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
    ) as progress_spinner:
        progress_spinner.add_task(description="Starting the update...", total=None)
        time.sleep(2)

    with Progress() as progress1:
        task1 = progress1.add_task("[cyan]Updating...", total=100)
        create_temp_folder()
        try:
            download_zip(github_request())
            extract_zip()
            move_download_files()
        finally:
            delete_temp_folder()


@app.command()
def update_driver(driver: str = typer.Option(...), proxy: bool = typer.Option(False)):
    config = configparser.ConfigParser()
    config.read(os.path.join('settings', 'conf', 'properties.cfg'))
    if driver == 'chrome':
        driver_name = config.get('Driver', 'chrome_driver_path')
    elif driver == 'opera':
        driver_name = config.get('Driver', 'opera_driver_path')
    elif driver == 'iexplore':
        driver_name = config.get('Driver', 'explorer_driver_path')
    elif driver == 'firefox':
        driver_name = config.get('Driver', 'gecko_driver_path')
    else:
        driver_name = None

    if driver_name:
        enable_proxy = settings.PYTALOS_GENERAL['update_driver']['enable_proxy']
        update = False
        if proxy:
            settings.PYTALOS_GENERAL['update_driver']['enable_proxy'] = True
            if settings.PROXY['http_proxy'] and settings.PROXY['https_proxy']:
                update = True
            else:
                print('[bold red]Error![/bold red] Complete the proxy information in settings file, PROXY!')
        else:
            update = True
        if update:
            try:
                install_driver = InstallDriver(driver_name)
                install_driver.install_driver(driver)
                print(f"[bold blue]Info![/bold blue] {driver} driver has been updated!")
            except Exception:
                print('[bold red]Error![/bold red] It is not possible to update the core!')
        settings.PYTALOS_GENERAL['update_driver']['enable_proxy'] = enable_proxy
    else:
        print('[bold red]Error![/bold red] Invalid driver name!')


@app.command()
def encoder(text: str = typer.Option(...), passphrase: str = typer.Option(None)):
    with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
    ) as progress_spinner:
        progress_spinner.add_task(description="Encoding text...", total=None)
        time.sleep(2)
    if passphrase:
        encoded_text = encode(text, passphrase=passphrase)
    else:
        encoded_text = encode(text)
    table = Table("[bold green]Original[/bold green]", "[bold green]Encoded[/bold green]")
    table.add_row(f"[bold blue]{text}", f"[bold blue]{encoded_text}[/bold blue]")
    print(table)


@app.command()
def decoder(text: str = typer.Option(...), passphrase: str = typer.Option(None)):
    with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
    ) as progress_spinner:
        progress_spinner.add_task(description="Decoding text...", total=None)
        time.sleep(2)
    if passphrase:
        decoded_text = decode(text, passphrase=passphrase)
    else:
        decoded_text = decode(text)
    if decoded_text:
        table = Table("[bold green]Original[/bold green]", "[bold green]Decoded[/bold green]")
        table.add_row(f"[bold blue]{text}", f"[bold blue]{decoded_text}[/bold blue]")
        print(table)
    else:
        print('[bold red]Error![/bold red] Invalid PASSPHRASE')


@app.command()
def alm_encoder():
    alm_encoder_path = os.path.join(BASE_PATH, 'arc', 'resources', 'talos-encoder-5.1.1.jar')
    with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
    ) as progress_spinner:
        progress_spinner.add_task(description="Open encoder in new window...", total=None)
        call(['java', '-jar', alm_encoder_path])
    print('[bold blue]Info![/bold blue] Done!')


@app.command()
def post_alm():
    jar_path = 'arc/resources/'
    json_path = 'output/json/'
    alm3_properties(settings.PYTALOS_ALM['alm3_properties'])
    call(['java', '-jar', jar_path + 'talos-alm-connect-5.1.1.jar', json_path])


@app.command()
def create_evidence(report_type: str = typer.Option(None)):
    if os.path.exists(os.path.join(OUTPUT_PATH, 'reports', 'talos_report.json')):
        with open(os.path.join(OUTPUT_PATH, 'reports', 'talos_report.json'), encoding='utf-8') as json_file:
            json_data = prepare_json_data(json.load(json_file))
        if report_type:
            if str(report_type).lower() == 'docx':
                generate_document_reports('docx', json_data.copy())
            elif str(report_type).lower() == 'pdf':
                generate_document_reports('pdf', json_data.copy())
            elif str(report_type).lower() == 'html':
                generate_html_reports(json_data.copy())
            else:
                print(
                    '[bold red]Error![/bold red] Incorrect report type: pdf, docx or html')
        else:
            generate_document_reports('docx', json_data.copy())
            generate_document_reports('pdf', json_data.copy())
            generate_html_reports(json_data.copy())
    else:
        print(
            '[bold red]Error![/bold red] Reports cannot be created because the file talos_report.json does not exist')


@app.command('create-web-template')
def create_web_template_command(
        system_name: str = typer.Option(..., help='Name of the system to automate.'),
        project_root: str = typer.Option('.', help='Root directory of the AutomacaoBDD project.'),
):
    """Create the initial files required for a new Web automation."""
    try:
        result = create_web_template(system_name, Path(project_root))
    except (FileExistsError, FileNotFoundError, ValueError) as error:
        raise typer.BadParameter(str(error)) from error

    print(f"[bold green]Success![/bold green] Template created for {system_name}.")
    print(f"[bold blue]Info![/bold blue] Configure selectors in {result['page_object_directory']}.")
    print('[bold blue]Info![/bold blue] Set the generated username and password environment variables before running.')


@app.command('create-api-template')
def create_api_template_command(
        system_name: str = typer.Option(..., help='Name of the API to automate.'),
        project_root: str = typer.Option('.', help='Root directory of the AutomacaoBDD project.'),
):
    """Create the initial files required for a REST API automation."""
    try:
        result = create_api_template(system_name, Path(project_root))
    except (FileExistsError, FileNotFoundError, ValueError) as error:
        raise typer.BadParameter(str(error)) from error

    print(f"[bold green]Success![/bold green] API template created for {system_name}.")
    print(f"[bold blue]Info![/bold blue] Configure the endpoint in {result['profiles']}.")


@app.command('register-system')
def register_system_command(
        system_name: str = typer.Option(..., help='Name of the system to automate.'),
        system_type: str = typer.Option('web', help='System type: web or api.'),
        auth_type: str = typer.Option('password', help='Authentication: password, sso or mfa.'),
        project_root: str = typer.Option('.', help='Root directory of the AutomacaoBDD project.'),
):
    """Register a system for automation without storing credentials."""
    try:
        system = register_system(system_name, system_type, auth_type, Path(project_root))
    except (FileExistsError, ValueError) as error:
        raise typer.BadParameter(str(error)) from error

    print(f"[bold green]Success![/bold green] System '{system['name']}' registered.")
    print(f"[bold blue]Info![/bold blue] Credential prefix: {system['credential_environment_prefix']}.")


def generate_document_reports(report_type, json_data):
    """
        This function generates the doc reports.
    :return:
    :rtype:
    """
    with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
    ) as progress_spinner:
        progress_spinner.add_task(description=f"Creating {report_type.upper()}...", total=None)
        try:
            if report_type == 'pdf':
                save_value_pdf = settings.PYTALOS_REPORTS["generate_pdf"]
                save_value_docx = settings.PYTALOS_REPORTS["generate_docx"]
                settings.PYTALOS_REPORTS["generate_pdf"] = True
                settings.PYTALOS_REPORTS["generate_docx"] = False
                if not os.path.exists(os.path.join(OUTPUT_PATH, 'reports', 'pdf')):
                    pdf_path = os.path.join(OUTPUT_PATH, 'reports', 'pdf')
                    os.makedirs(pdf_path, exist_ok=True)
                report = CreatePDF()
            elif report_type == 'docx':
                save_value_pdf = settings.PYTALOS_REPORTS["generate_pdf"]
                save_value_docx = settings.PYTALOS_REPORTS["generate_docx"]
                settings.PYTALOS_REPORTS["generate_pdf"] = False
                settings.PYTALOS_REPORTS["generate_docx"] = True
                if not os.path.exists(os.path.join(OUTPUT_PATH, 'reports', 'doc')):
                    doc_path = os.path.join(OUTPUT_PATH, 'reports', 'doc')
                    os.makedirs(doc_path, exist_ok=True)
                report = CreateDOC()
            reports_created = []
            start_time = datetime.datetime.now()
            for feature in json_data.get("features", []):
                files = report.generate_document_report(feature, json_data.get("global_data", []))
                reports_created.append(files)
                print(f"[bold blue]Info![/bold blue] {report_type.upper()} report has been created!")
            end_time = datetime.datetime.now()
            print(f"Files generated in {end_time - start_time}")
            settings.PYTALOS_REPORTS["generate_pdf"] = save_value_pdf
            settings.PYTALOS_REPORTS["generate_docx"] = save_value_docx
        except(Exception,) as e:
            raise TalosReportException(f"It was impossible to generate {report_type} reports, Exception error: {e}")


def generate_html_reports(json_data):
    """
        This function generates the html reports.
    :return:
    :rtype:
    """
    with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
    ) as progress_spinner:
        progress_spinner.add_task(description="Creating HTML...", total=None)
        try:
            if not os.path.exists(os.path.join(OUTPUT_PATH, 'reports', 'html')):
                pdf_path = os.path.join(OUTPUT_PATH, 'reports', 'html')
                os.makedirs(pdf_path, exist_ok=True)
            start = datetime.datetime.now()
            html_files = _generate_html_reports(json_data)
            end = datetime.datetime.now()
            print(f"Html reports generated in: {end - start}\n")
            print('[bold blue]Info![/bold blue] HTML report has been created!')
            return html_files

        except (Exception,):
            traceback.print_exc()


@app.callback()
def callback():
    print(
        "[red]\n==============================================================================\n"
        "==                          AUTOMACAO BDD                                  ==\n"
        "==                          AutomacaoBDD - SGTO                            ==\n"
        "==============================================================================\n")


if __name__ == "__main__":
    app()
