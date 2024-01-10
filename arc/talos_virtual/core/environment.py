from arc.talos_virtual.core.contrib.mountebank.mountebank import MountebankWrapper
from arc.talos_virtual.core.env_utils import create_dict_imposter
from arc.talos_virtual.core.context import TalosVirtual, RuntimeDatas
from settings import settings


def before_execution(args, context):
    context.mountebank = TalosVirtual(context)
    context.runtime = RuntimeDatas(context)
    context.mountebank = MountebankWrapper()
    imposter = None
    if args.console:
        settings.MOUNTEBANK['console'] = True
    if args.imposter:
        imposter = args.imposter[0]

    create_dict_imposter(imposter, context)
    context.mountebank.start_process()


def before_all(context):
    context.mountebank.create_imposter(dict_imposter=context.mountebank.dict_imposter)


def after_all(context):
    pass


def after_execution(context):
    if settings.MOUNTEBANK['url'] == 'localhost':
        if settings.MOUNTEBANK['console'] is True:
            answer = 'N'
            while str(answer).lower() != 'y':
                answer = input('Do you want to close mountebank service? (Y/N): ')
            context.mountebank.stop_process()
            print('mountebank service closed.')
