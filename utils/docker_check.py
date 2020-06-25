import os


def am_i_in_docker():
    utils_path = os.path.dirname(os.path.realpath(__file__))
    bidsgui2_path = os.path.dirname(utils_path)
    possible_docker_root = os.path.dirname(bidsgui2_path)

    if 'bidsgui2_is_running_in_docker.fact' in os.listdir(possible_docker_root):
        return True
    else:
        return False


