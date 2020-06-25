import os
import os
import threading
import time

import pandas as pd
from pydicom import FileDataset
from pydicom.errors import InvalidDicomError
from pydicom.filereader import dcmread
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer


# local imports, namely the dicom indexer
from dicoms.indexer import index_dicoms, deindex_sessions

class BaseWatcher:
    def __init__(self, path='.'):
        """
        Basic watcher class from which we'll inherit a dicom watcher and a folder watcher.
        :param path: Path to watch for file system changes
        """
        self.path = path
        self.patterns = "*"  # Patterns to match, presently all for this generic class
        self.ignore_patterns = ""  # Ignore none
        self.ignore_directories = False  # Watch Directories too
        self.case_sensitive = True  # I don't see a downside to making things case sensitive

        # Spooling up a watchdog event handler with the above options
        self.my_event_handler = PatternMatchingEventHandler(patterns=self.patterns,
                                                            ignore_patterns=self.ignore_patterns,
                                                            ignore_directories=self.ignore_directories,
                                                            case_sensitive=self.case_sensitive)

        # Registering our file system events with those of the event handler
        self.my_event_handler.on_created = self.on_created
        self.my_event_handler.on_deleted = self.on_deleted
        self.my_event_handler.on_modified = self.on_modified
        self.my_event_handler.on_moved = self.on_moved

        # Creating an observer object to pass our event handler to
        self.observer = Observer()
        # Scheduling the observer/pointing at our path to watch
        self.observer.schedule(self.my_event_handler, path=self.path, recursive=True)
        # Starting the observer/event handler.
        self.observer.start()

    @staticmethod
    def on_created(event):
        """
        Put your on created logic here
        :param event: A watchdog event handler event
        :return: pass
        """
        pass

    @staticmethod
    def on_deleted(event):
        """
        On file system event deletion do this method
        :param event: A watchdog event handler event
        :return: pass
        """
        pass

    @staticmethod
    def on_modified(event):
        """
        On file system event modified do this method
        :param event: A watchdog event handler event
        :return: pass
        """
        pass

    @staticmethod
    def on_moved(event):
        """
        On file system event moved do this method
        :param event: A watchdog event handler event
        :return: pass
        """
        pass


class SessionWatcher(BaseWatcher):
    """
    This class inherits from BaseWatcher and overrides the on_created and on_modified events to perform some
    action if a folder is created or modified. Presently there is no handling on the deletion of folders or on a folder
    move.
    """

    @staticmethod
    def on_created(event):
        if os.path.isdir(event.src_path):
            print("New Session folder created at {}".format(event.src_path))

    @staticmethod
    def on_modified(event):
        if os.path.isdir(event.src_path):
            print("Session folder at {} has been modified.".format(event.src_path))
    @staticmethod
    def on_deleted(event):
        if os.path.isdir(event.src_path):
            print("Session folder at {} has been deleted.".format(event.src_path))
        deindex_sessions()

    @staticmethod
    def on_moved(event):
        if os.path.isdir(event.src_path):
            print("Session folder at {} has been deleted.".format(event.src_path))


class DicomWatcher(BaseWatcher):
    """
    This class inherits from BaseWatcher and watches for newly created dicoms. It also will do some action on created
    if the dicom it detects is invalid for some reason. This is achieved by relying on pydicom to throw an
    InvalidDicomError or to be successful after attempting to read a new dicom (specifically a .dcm) file.
    """

    def __init__(self, path='.', action_method=None, timeout=30.0):
        self.array = None
        self.idle_time = None  # time between file system events
        self.timeout = timeout  # time at which to terminate observing and exit
        self.fail_safe = threading.Thread(target=self.idle_switch)
        self.fail_safe.start()
        self.event_tracker = {}
        self.paths_to_index = {}
        super().__init__(path)
        print("launched a DicomWatcher at path {}".format(path))

    def idle_switch(self):
        while True:
            time.sleep(3)
            if self.idle_time and time.time() - self.idle_time > self.timeout:
                # TODO INDEX PARENT WATCHED PATH!!
                self.paths_to_index = [path for path in self.event_tracker.keys()]
                print("Preparing to index the following paths:")
                good_paths = [path for path in self.paths_to_index]

                for path in good_paths:
                    print(path)
                print("*************INDEXING********************")
                try:
                    path_to_index = os.path.commonpath(good_paths)
                except ValueError as err:
                    print("Error with good paths: {}, {}".format(good_paths, err))
                    path_to_index = ''
                self.event_tracker = {}
                print('index_dicoms({})'.format(path_to_index))
                if path_to_index is not [] and path_to_index is not '':
                    index_dicoms(path_to_index)
                # clearing out now indexed paths
                self.paths_to_index = []
                good_paths = []
                self.idle_time = None




    def record_event(self, file_delivered, delivered_time):
        """
        Faster way to append to two lists the delivered time of a dicom and the destination of the delivery,
        this method will be called each time a dicom is detected as being created if the self.log is not None.
        :param delivered_time: Time dicom was detected as arriving in watched directory located at self.path
        :return:
        """
        self.event_tracker[file_delivered] = delivered_time

    def on_created(self, event):
        """
        On file system creation check if .dcm is in the file path and if so validate if it's a proper dicom using
        dcmread from pydicom.
        :param event: A watchdog watcher event
        :return: None
        """
        self.idle_time = time.time()
        if ".dcm" or 'MRDC' in event.src_path:
            landed_time = time.time()
            self.record_event(event.src_path, landed_time)
            print("New file/folder at {}".format(event.src_path))

    @staticmethod
    def is_valid_dicom(dicom, silent=True):
        """
        This method uses pydicom to validate incoming dicoms with dcmread.
        :param dicom: A potential dicom file
        :param silent: Boolean to silence print statements upon validation or invalidation.
        :return: Dicom's validity as a boolean.
        """
        try:
            unverified_dicom = dcmread(dicom)
            if type(unverified_dicom) is FileDataset:
                if not silent:
                    print("{} is a valid dicom.".format(dicom))
                return True
        except InvalidDicomError:
            if not silent:
                print("##" * 50)
                print("{} is not a valid dicom".format(dicom))
                print("##" * 50)
            return False


if __name__ == "__main__":
    # getting user's home folder path.
    home = os.path.expanduser('~')
    # collecting incoming dicom path
    incoming_dicoms = os.path.join(home, 'incoming_dicoms')
    # scheduling a folder/session watcher on the incoming dicom folder
    # my_observer = SessionWatcher(incoming_dicoms)
    # scheduling a dicom watcher on the incoming folder
    dicom_observer = DicomWatcher(incoming_dicoms, log_path='/home/anthony/incoming_dicoms')

    # collecting source dicom path for simultor
    dicoms = os.path.join(home, 'Dicoms')
    """
    try:
        test_sim = Simulator(input_directory='/home/anthony/Dicoms/test_dicoms_1000/phantom_scan_20190716',
                             output_directory=incoming_dicoms,
                             tr=0.001,
                             clean_output_dir=True,
                             test=True)
        test_sim.run()
        '''
        while True:
            # running simulator with test dicoms located in variable dicoms
            for session in [os.path.join(dicoms, dicom_folder) for dicom_folder in os.listdir(dicoms)]:
                test_sim = Simulator(session, incoming_dicoms, tr=0.001, clean_output_dir=True)
                test_sim.run()
        '''

    except KeyboardInterrupt:
        # Kill when ctrl-c
        dicom_observer.observer.stop()
        dicom_observer.observer.join()
        #my_observer.observer.stop()
        #my_observer.observer.join()
    """
