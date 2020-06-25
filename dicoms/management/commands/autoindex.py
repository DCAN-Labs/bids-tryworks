from django.conf import settings
from django.core.management.base import BaseCommand

from dicoms.event_logger import start_logging_and_run_indexer
from utils.docker_check import am_i_in_docker
from utils.dir_watch import DicomWatcher, SessionWatcher

if not am_i_in_docker():
    from bidsgui2.settings import BASE_DICOM_DIR, LOG_PATH
else:
    from bidsgui2.docker import BASE_DICOM_DIR, LOG_PATH

class Command(BaseCommand):
    """
    This class provides the user with the ability to index dicoms automatically
    usage is as follows

    >python manage.py autoindex
    """

    # TODO add support for passing in paths to this command
    def handle(self, *args, **options):
        dirs_being_watched = {}
        dirs_being_watched_to_deindex = {}
        for directory in BASE_DICOM_DIR:
            dirs_being_watched[directory] = DicomWatcher(path=directory, timeout=10.0)
            dirs_being_watched_to_deindex[directory] = SessionWatcher(path=directory)


