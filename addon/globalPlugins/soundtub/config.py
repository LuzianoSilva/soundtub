from pathlib import Path

import config

SECTION = "soundtub"


def initialize():
    config.conf.spec[SECTION] = {
        "downloadFolder": "string(default='')",
        "defaultFormat": "option('MP3', 'MP4', default='MP3')",
    }


def default_download_folder():
    folder = Path.home() / "Downloads"
    return str(folder if folder.is_dir() else Path.home())


def get_download_folder():
    initialize()
    value = config.conf[SECTION]["downloadFolder"]
    return value or default_download_folder()


def set_download_folder(folder):
    initialize()
    config.conf[SECTION]["downloadFolder"] = folder
    config.conf.save()


def get_default_format():
    initialize()
    return config.conf[SECTION]["defaultFormat"]

