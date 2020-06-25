import getpass
import random
import subprocess
import time

import pexpect


def login_and_sync(source, destination, user, host, password=None):
    # TODO Add some error handling, seriously. Namely incorrect user, failed password, and host does not exist.
    # TODO You need to take into account accepting the key thingy when ssh/scp/rsync first
    # TODO generates when connecting to a new server.
    """
    This function provide a means for the user to transfer their data between the local server to
    either a remote server or locally using scp. This function uses pexpect is similar to calling a linux command with
    subprocess. Pexpect provides some additional benefits however, namely it keeps things such as passwords and entered
    text from appearing in bash history and it's designed to respond to text prompts that it's instructed to recieve.

    In this specific case pexpect calls scp with it's requisite arguments then waits for scp to open up a password
    prompt. Once that prompt appears the password argument above is provided to pexpect and scp does it's magic.
    :param source: The source file or folder to be transmitted
    :param destination: The filepath the user wishes to deliver the file to.
    :param user: The user at the destination host, it's this user's password that will be required for this function
    to work.
    :param host: The machine to deliver files/folders to from the where this code is locally.
    :param password: user's password, passed in as string.
    :return:
    """
    if not source:
        raise Exception("Must provide source data to be transferred")
    if not destination:
        raise Exception("Must provide destination to transmit data to.")
    # if no host is provided it will be assumed that transfer should occur locally
    if not host:
        cmd = 'scp {source} {destination}'.format(source=source, destination=destination)
        child = pexpect.spawn(cmd)
        child.expect(pexpect.EOF)  # if this isn't present transfer will be cut off before it can complete.
    # if host is provide use this alternate command and pass it a password.
    else:
        # first make destination folder on remote host
        # ssh galassi@exahead1 "mkdir -p /home/exacloud/lustre1/fnl_lab/scratch/new_folder"
        make_dir_cmd = 'ssh {user}@{host} "mkdir -p {destination}"'.format(user=user,
                                                                           host=host,
                                                                           destination=destination)
        print(make_dir_cmd)
        make_dir_child = pexpect.spawn(make_dir_cmd)
        connection = make_dir_child.expect(['password:', 'Are you sure you want to continue connecting'], timeout=None)
        if connection == 0:
            make_dir_child.sendline(password)
        elif 1:
            print("got this response", make_dir_child.before, make_dir_child.after)
            make_dir_child.sendline('yes')
            make_dir_child.expect('to the list of known hosts.')
            make_dir_child.sendline(password)
        make_dir_child.expect(pexpect.EOF)

        # then do you scp like this
        """
        # scp -r /group_shares/fnl/scratch/data/dicom2bids/earl_test_20190717_0837/sub-* 
        # galassi@exahead1:/home/exacloud/lustre1/fnl_lab/scratch/new_folder
        
        cmd = 'scp -r {source} {user}@{host}:{destination}'.format(source=source, user=user, host=host,
                                                                    destination=destination)
        """

        # although it turns out it's easier to user rsync if we want to excluded tmp_dcm2bids (which we do)
        cmd = 'rsync -rt --exclude tmp_dcm2bids ' + \
              '{source} {user}@{host}:{destination}'.format(source=source,
                                                            user=user,
                                                            host=host,
                                                            destination=destination)
        print(cmd)
        child = pexpect.spawn(cmd)
        time.sleep(random.random() * random.randrange(1, 5) + .33)  # I don't think this is necessary, but it don't hurt
        child.expect('password:', timeout=None)
        child.sendline(password)
        child.expect(pexpect.EOF, timeout=None) # if this isn't present transfer will be cut off before it can complete
        child.sendline("echo $?")
        child.close()
        # after closing the moving subprocess we want to collect the status of the move
        signal_status = child.signalstatus
        exit_code = child.exitstatus

        # if the move went well we delete the source files
        if exit_code == 0 or exit_code == '0':
            rm_cmd = 'rm -rf {source}'.format(source=source)
            remove_source = subprocess.run(rm_cmd, shell=True)
            print(rm_cmd)


if __name__ == "__main__":
    # prompt user for password:
    print("Enter your login credentials below:")
    source = input("Enter source: ")
    destination = input("Enter Destination: ")
    user = input("Enter Username: ")
    host = input("Enter Hostname: ")
    password1 = ''
    password2 = '1'
    while password1 != password2:
        password1 = getpass.getpass()
        password2 = getpass.getpass(prompt="Confirm Password:")
        if password1 != password2:
            print("Passwords do not match. Try again")
    for i in range(1):
        destination = destination
        login_and_sync(source=source, destination=destination, user=user, host=host, password=password1)
