import os
import json
import random
import datetime


def read_from_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    return content


def read_config(config_path):
    config_content = read_from_file(config_path)
    return json.loads(config_content)


def write_file(file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    return open(file_path, "w", encoding="utf-8")


def shuffled(seq):
    copy = seq.copy()
    random.shuffle(copy)
    return copy


def get_date_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H_%M_%S")
