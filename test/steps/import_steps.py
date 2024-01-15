# -*- coding: utf-8 -*-
"""
Imports generic steps and steps that are inside folders nested in the steps' folder.
If you do not import the steps from the nested folders to the steps' folder, you may get the error that the framework
cannot find those steps. Adding here the imports of those steps is mandatory for use in the features.

Some Steps by default require the installation of some additional library.
If necessary, you will be prompted by a Warning message in runtime.

The default Steps are in the path: arc.contrib.steps
List of default steps:
######################
API Rest Keywords: from arc.contrib.steps.api import api_keywords
Data Base Keywords:
    - Oracle: from arc.contrib.steps.db import oracle_keywords
Personal Communication Host Keywords: from arc.contrib.steps.host import host_keywords
Web Keywords:
    - Generics: from arc.contrib.steps.web import web_keywords
    - Appian: from arc.contrib.steps.web import appian_keywords
General Keywords:
    Data: from arc.contrib.steps.general import datas_keywords
    Functional: from arc.contrib.steps.general import functional_keywords
    Mail: from arc.contrib.steps.general import mail_keywords
    FTP and SFTP: from arc.contrib.steps.general import ftp_keywords
Accessibility Keywords: from arc.contrib.steps.accessibility import accessibility_keywords

"""
try:
    # DEFAULT STEPS
    from arc.contrib.steps.api import api_keywords
    from arc.contrib.steps.web import web_keywords
    from arc.contrib.steps.accessibility import accessibility_keywords
    # USER STEPS

    from test.steps.examples.web.SistemaADB360 import User_user, monitoramento_alarme, grupo_agencia, ponto_de_venda, \
        usuario, grupo_operacao

except (Exception,) as ex:
    raise ImportError(
        f"There was an error in importing the steps.\n"
        f"Origin error: {ex}"
    )
