import os
import pathlib
import sys
import time
import traceback

#Update path to include working directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# importing django specific modules
import django
import pydicom
import pytz
import utils 
from dateutil import parser as dateparser
from tryworks_utils.docker_check import am_i_in_docker
import dotenv
dotenv.load_dotenv(dotenv.find_dotenv()) 



if not am_i_in_docker():
    print("dicoms.indexer is not in docker.")
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bids_tryworks.settings')
    django.setup()
else:
    print("dicoms.indexer is in docker.")
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bids_tryworks.docker')
    django.setup()

from dicoms.models import Session, Subject, Series
from django.template.defaultfilters import slugify
from django.utils import timezone


def clean_name(name):
    return name.replace('_', '').replace('-', '').lower()


def index_dicoms(root_dir):
    old_series_description = ''
    for root, dirs, files in os.walk(root_dir):
        old_subject_id = ''
        for f in files:
            try:
                dicom = pydicom.dcmread(os.path.join(root, f))

                new_subject, sc = Subject.objects.get_or_create(SubjectID=dicom.PatientID,
                                                                    slug=slugify(dicom.PatientID))


                # Create Session object
                new_session, new_session_status = Session.objects.get_or_create(Subject=new_subject,
                                                                                Path=os.path.dirname(
                                                                                    os.path.join(root, f)))
                aware = dateparser.parse(dicom.SeriesDate).replace(tzinfo=pytz.UTC)
                new_session.SessionDate = aware
                try:
                    new_session.StudyDescription = dicom.StudyDescription
                except AttributeError:
                    pass
                new_session.save()

                # Below is a list of data that we're trying to extract from the dicom,
                # we'll pass this list into a getattr try except, because occasionally
                # some dicom's won't have the data we're looking for
                dicom_data_we_want = ['SeriesDescription',
                                      'StudyDescription',
                                      'ImageType',
                                      'SeriesNumber',
                                      'PatientID',
                                      'SeriesDate',
                                      'StudyDate'
                                      ]
                session_dict = {}
                for attribute in dicom_data_we_want:
                    try:
                        if attribute is 'ImageType':
                            value = getattr(dicom, attribute)
                            value = str(value._list)
                            session_dict[attribute] = value.replace("_", "','")
                        elif 'Date' in attribute:
                            value = getattr(dicom, attribute)
                            value = dateparser.parse(str(value)).replace(tzinfo=pytz.UTC)
                            session_dict[attribute] = value
                        else:
                            value = getattr(dicom, attribute)
                            session_dict[attribute] = str(value)
                    except (AttributeError, ValueError):
                        pass
                    finally:
                        session_dict['IndexedDate'] = timezone.now()
                        session_dict['Path'] = root

                if session_dict['SeriesDescription'] != old_series_description:
                    old_series_description = session_dict['SeriesDescription']
                    new_series = Series.objects.get_or_create(**session_dict, Session=new_session, Subject=new_subject)
                    new_series.save()
                else:
                    pass

            except (pydicom.errors.InvalidDicomError, FileNotFoundError, PermissionError, AttributeError, OSError) as err:
                err
                pass


def deindex_sessions():
    """
    This function go through all sessions and checks to see if they still exist somewhere on the disk, if they do it
    does nothing if the session folder no longer exists it deletes the entry from the database
    :return: a list of deleted sessions
    """
    all_sessions = Session.objects.all()

    for session in all_sessions:
        if os.path.exists(session.Path):
            # do nothing this path exists
            pass
        else:
            session.delete()
            print("Deleted {} from database.".format(session))

if __name__ == "__main__":
	index_dicoms(os.environ['BASE_DICOM_DIR'])
