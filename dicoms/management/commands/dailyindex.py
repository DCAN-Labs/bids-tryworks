from django.core.management.base import BaseCommand
from utils.docker_check import am_i_in_docker
from dicoms.indexer import index_dicoms
from dicoms.models import HasBeenIndexed
import datetime
import time
import os


if not am_i_in_docker():
    from bidsgui2.settings import BASE_DICOM_DIR, LOG_PATH
else:
    from bidsgui2.docker import BASE_DICOM_DIR, LOG_PATH


class Command(BaseCommand):
    """
    This command indexes all of the dicoms in
    """

    def handle(self, *args, **options):
        # start indexing once on launch
        if am_i_in_docker():
            first_index_history = HasBeenIndexed.objects.all()
            if not first_index_history:
                for directory in BASE_DICOM_DIR:
                    index_dicoms(directory)
                first_index = HasBeenIndexed.objects.create(date_indexed=datetime.datetime.now(),
                                                            directories_indexed=str(BASE_DICOM_DIR))
                first_index.save()
            else:
                pass
        current_time = datetime.datetime.now()
        next_scan_time = current_time + datetime.timedelta(hours=24)
        print("Initiating daily indexer, next index will begin after {}".format(next_scan_time))
        while True:
            time.sleep(900)
            current_time = datetime.datetime.now()
            if current_time >= next_scan_time:
                for directory in BASE_DICOM_DIR:
                    index_dicoms(directory)
                next_scan_time = datetime.datetime.now() + datetime.timedelta(hours=24)
                print("Next index scheduled to begin after {}".format(next_scan_time))

        pass


