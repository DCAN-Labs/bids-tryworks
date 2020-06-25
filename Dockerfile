# Creating from base ubuntu image because Ubuntu generally works.
FROM ubuntu:18.04

# setting local env vars
ENV LANG="en_US.UTF-8" \
    LC_ALL="C.UTF-8"

# Instal python, rysync and other requirements into image
RUN apt-get update && apt-get install -yq --no-install-recommends \
        rsync \
        make \
        cmake \
        vim \
        ssh \
        wget \
        build-essential \
        python3 \
        python3-pip \
        git \
        pkg-config \
        pigz \
        libpq-dev \
        python3-dev \
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# installing dcm2niix
# see https://github.com/rordenlab/dcm2niix for further details
RUN git clone https://github.com/rordenlab/dcm2niix.git &&\
    cd dcm2niix &&\
    mkdir build &&\
    cd build &&\
    ls &&\
    cmake .. &&\
    make install




# creating mount points for the base incoming dicom dir( where we are indexing from/watching for dicoms)
# and creating a converted folder where dcm2niix/dcm2bids will write conversions to.
# these folders will need to be correctly mounted at launch of this image.
# these folder names are the same case as the variables they correspond to in settings.py
# Further, this codebase defaults to outputing it's
RUN mkdir /bidsgui2/ \
 && mkdir /MOUNTED_FOLDER \
 && mkdir /MOUNTED_FOLDER/BASE_DICOM_DIR \
 && mkdir /MOUNTED_FOLDER/CONVERTED_FOLDER \
 && mkdir /MOUNTED_FOLDER/LOG_PATH \
 && mkdir /MOUNTED_FOLDER/DCM2BIDS_FILES \
 && touch /bidsgui2_is_running_in_docker.fact


COPY requirements.txt /bidsgui2/requirements.txt

# install setup tools and pipwheel
RUN pip3 install setuptools wheel

# Install python requirements from text file
RUN pip3 install -r bidsgui2/requirements.txt

