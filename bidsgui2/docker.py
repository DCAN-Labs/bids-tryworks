# importing all settings from standard settings file
# if you're seeing this grayed out on an editor don't delete the
# from bidsgui2.settings import *, otherwise you will have a bad time
#####################################################################
from bidsgui2.settings import *   # don't delete this line
#####################################################################
# don't delete above

# standard imports
import os
import dotenv

# loading variables from .env file
dotenv.load_dotenv(dotenv.find_dotenv())

# point to this settings module
DJANGO_SETTINGS_MODULE = os.path.abspath(__file__)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'HOST': 'bidsgui2_external_dicom_db',
        'PORT': '5432',
    }
}

# these paths are all hardcoded to the docker image
# set them to your local machine/server in a .env file
# for descriptions see sample.env or read the documents
# in bidsgui2/docs
BASE_DICOM_DIR = [
    os.path.join('/', 'MOUNTED_FOLDER','BASE_DICOM_DIR')
]
LOG_PATH = os.path.join('/', 'MOUNTED_FOLDER', 'LOG_PATH')
CONVERTED_FOLDER = os.path.join('/', 'MOUNTED_FOLDER', 'CONVERTED_FOLDER')
DCM2BIDS_FILES = os.path.join('/', 'MOUNTED_FOLDER', 'DCM2BIDS_FILES')
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000

