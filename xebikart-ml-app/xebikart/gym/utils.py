import requests
import zipfile
import shutil
import platform
import os


def download_simulator(url, output_path):
    """
    Download simulator

    :param url:
    :param output_path:
    :return:
    """
    print("Downloading: %s..." % url)
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open(output_path, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)
    else:
        raise RuntimeError("Unable to download %s - (error: %d)" % (url, r.status_code))
    return output_path


def extract_simulator(zip_path, output_path):
    """
    Extract simulator

    :param zip_path:
    :param output_path:
    :return:
    """
    zip_ref = zipfile.ZipFile(zip_path, 'r')
    zip_ref.extractall(output_path)
    zip_ref.close()
    return output_path


def get_or_download_simulator(donkey_sim_home=None):
    assert_supported_version()

    if donkey_sim_home is None:
        donkey_sim_home = os.environ.get('DONKEY_SIM_HOME')
        if donkey_sim_home is None:
            donkey_sim_home = os.path.abspath("donkey_home")

    if not os.path.isabs(donkey_sim_home):
        donkey_sim_home = os.path.abspath(donkey_sim_home)

    print("Looking in donkey_sim_home path: %s" % donkey_sim_home)
    donkey_sim_path = get_donkey_sim_abs_path(donkey_sim_home)
    print("Looking for file: %s" % donkey_sim_path)
    if not os.path.isfile(donkey_sim_path):
        print("Simulator doesn't exist.")
        donkey_sim_url = get_donkey_sim_url()
        donkey_sim_archive = donkey_sim_url[donkey_sim_url.rfind("/") + 1:]
        donkey_sim_abs_archive = os.path.join(donkey_sim_home, donkey_sim_archive)
        print("Download simulator: %s to %s" % (donkey_sim_url, donkey_sim_abs_archive))
        os.makedirs(donkey_sim_home, exist_ok=True)
        download_simulator(donkey_sim_url, donkey_sim_abs_archive)
        print("Extracting simulator %s to %s", donkey_sim_abs_archive, donkey_sim_home)
        extract_simulator(donkey_sim_abs_archive, donkey_sim_home)
        if not os.path.isfile(donkey_sim_path):
            raise RuntimeError("Unable to get or download donkey simulator.")
    else:
        print("Found: %s" % donkey_sim_path)
    return donkey_sim_path


def get_donkey_sim_url():
    if is_linux():
        return "https://github.com/tawnkramer/donkey_gym/releases/download/v18.9/DonkeySimLinux.zip"
    elif is_os_x():
        return "https://github.com/tawnkramer/donkey_gym/releases/download/v18.9.1/DonkeySimMac_10_13.zip"
    return None


def get_donkey_sim_abs_path(donkey_sim_home):
    if is_linux():
        return os.path.join(donkey_sim_home, "DonkeySimLinux/donkey_sim.x86_64")
    elif is_os_x():
        return os.path.join(donkey_sim_home, "DonkeySimMac/donkey_sim.app/Contents/MacOS/donkey_sim")
    return None


def is_linux():
    return platform.system() == "Linux"


def is_os_x():
    return platform.system() == "Darwin"


def assert_supported_version():
    if not is_linux() and not is_os_x():
        raise RuntimeError("Only support Linux or Darwin platform.")
