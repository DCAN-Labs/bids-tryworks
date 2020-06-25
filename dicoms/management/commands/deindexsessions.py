from django.core.management.base import BaseCommand

from dicoms.indexer import deindex_sessions


class Command(BaseCommand):
    """
    This class provides the user with the ability to deindex dicoms via the
    usage is as follows

    >python manage.py deindex
    """

    def handle(self, *args, **options):
        print("Deindexing sessions...")
        deindex_sessions()
