import os
import traceback

import yaml
from django.core.management.base import BaseCommand

from bidsgui2.settings import server_config


class Command(BaseCommand):
    """
    This class allaws the user to add a new path to watch for dicoms via manage.py

    >>> python manage.py setwatchedfolders -d /path/to/folder/to/watch
    """
    def add_arguments(self, parser):
        parser.add_argument('-d', '--directory', type=str, help="Path to watch for new dicoms.")

    def handle(self, *args, **options):
        if options['directory']:
            if os.path.isdir(options['directory']):
                new_watched_directory = options['directory']
                directory_exists = True
            else:
                directory_exists = False
            try:
                if not directory_exists:
                    os.makedirs(options['directory'])
            except FileExistsError:
                traceback.print_exc()
                print("You shouldn't have been able to get here.")
            except PermissionError:
                traceback.print_exc()
                raise PermissionError

            # if all the above is hunky dory we will add the new path/watched path our server settings
            try:
                server_yaml = {}
                with open(server_config, 'r') as infile:
                    server_yaml = yaml.load(infile, Loader=yaml.Loader)
                    server_yaml['BASE_DICOM_DIR'].append(new_watched_directory)
                if server_yaml != {}:
                    with open(server_config, 'w') as outfile:
                        yaml.dump(server_yaml, stream=outfile, Dumper=yaml.Dumper)
            except KeyError:
                traceback.print_exc()
                raise KeyError
            except IOError:
                traceback.print_exc()
                raise IOError

        else:
            print("No directory passed to watch, check BASE_DICOM_DIR in bidsgui2.settings or supply path with -d \
                   argument")
