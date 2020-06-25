from django.conf import settings
from django.core.management.base import BaseCommand

from dicoms.indexer import index_dicoms

from utils.docker_check import am_i_in_docker
if not am_i_in_docker():
    from bids-tryworks.settings import BASE_DICOM_DIR, LOG_PATH
else:
    from bids-tryworks.docker import BASE_DICOM_DIR, LOG_PATH

class Command(BaseCommand):
    """
    This class provides the user with the ability to index dicoms via the
    command line without having to run the whole django project.
    usage is as follows

    >python manage.py index
    or to index a specific path the syntax below.
    >python manage.py index /dicoms/2019/etc/etc
    """

    def add_arguments(self, parser):
        parser.add_argument('-d', '--directory', type=str, help="index any path following this argument")

    def handle(self, *args, **options):
        if options['directory']:
            index_dicoms(options['directory'])
        elif not options['directories'] and settings.BASE_DICOM_DIR:
            print('settings.BASE_DICOM_DIR', settings.BASE_DICOM_DIR)
            for directory in settings.BASE_DICOM_DIR:
                print('directory', directory)
                index_dicoms(directory)
        else:
            print("No directory passed to index, check BASE_DICOM_DIR in bids-tryworks.settings or supply path with -d \
                   argument")
