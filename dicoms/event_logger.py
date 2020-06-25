#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This has been deprecated, dirwatch.py in /utils instead for dynamic directory watching. This module
might still be useful for appilcations such as watching an incredibly large amount of dicoms (Terrabytes upon
terrabytes).

This script will watch the dicom directory to notice whenever
new files and folders are added, modified, or deleted and create a log
of these events. The eventlog is converted to a list of newly created folders (object eventlog).
The common path for these folders is determined(object common_path) and this path is fed to
index_dicoms function for indexing
"""
import datetime
import logging
import os
import shutil
import time

from watchdog.events import LoggingEventHandler
from watchdog.observers import Observer

from dicoms.indexer import index_dicoms


def event_logger(pathtowatch, logpath):
    logging.basicConfig(level=logging.INFO,
                        #format='%(asctime)s - %(message)s',
                        format='%(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename= logpath)
    event_handler = LoggingEventHandler()
    observer = Observer()
    observer.schedule(event_handler, pathtowatch, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def parselogs(logpath):
    eventlog = []
    today = datetime.datetime.now().strftime("%Y%m%d")
    todays_logpath = logpath + today

    try:
        shutil.copy(logpath, todays_logpath)

        if os.path.isfile(todays_logpath):
            temp = open(logpath, "w")
            temp.close()

        with open(todays_logpath, "r") as inputfile:
            lines = [line.rstrip('\n') for line in inputfile]

        for line in lines:
            if "Created directory" in line:
                split = str.split(line)
                eventlog.append(split[-1])
            else:
                pass
        print('contents of eventlog are', eventlog)
        common_path = os.path.commonpath(eventlog)
        print('common path for events is', common_path)
        index_dicoms(common_path)
        return eventlog
    except (IOError, OSError, shutil.SameFileError):
        pass


def start_logging_and_run_indexer(path_to_watch, log_path):
    # TODO add these paths to a general config file that then pushes
    # TODO these paths to settings.py
    path_to_watch = path_to_watch  # BASE_DICOM_DIR[0]
    log_path = log_path #LOG_PATH

    event_logger(path_to_watch, log_path)

    while True:
        # run the log parser (index new dicoms/folders at 12am every night)
        if time.localtime().tm_hour % 24 == 0:
            x = parselogs(log_path)
            # if indexing finishes before 1am prevent indexing from running again
            # by sleeping until it's past 12am.
            if time.localtime().tm_hour % 24 == 0:
                time_left_in_hour = (60 - time.localtime().tm_min) * 60
                time.sleep(time_left_in_hour + 10)


if __name__ == "__main__":
    start_logging_and_run_indexer('/remote_home/galassi', '/remote_home/galassi/logger/logs.out')


'''
logpath = "/mnt/max/home/moorlu/lucilog"+today

def parselogs(logpath):
    eventlog = []
    with open(logpath, "r") as inputfile:
        lines = [line.rstrip('\n') for line in inputfile]

    for line in lines:
        if "Created directory" in line:
            split = str.split(line)
            eventlog.append(split[-1])
        else:
            pass
    print('contents of eventlog are', eventlog)
    return eventlog

common_path = os.path.commonpath(parselogs(logpath))
print('common path for events is', common_path)
index_dicoms(common_path)
'''


'''
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        # format='%(asctime)s - %(message)s',
                        format='%(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename="/mnt/max/home/moorlu/lucilog"
    #path = sys.argv[1] if len(sys.argv) > 1 else '.'
    event_handler = LoggingEventHandler()
    observer = Observer()
    observer.schedule(event_handler, logpath, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
'''