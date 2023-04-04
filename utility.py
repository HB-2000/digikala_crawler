import csv
from time import sleep
import random
import unicodedata
import re


def write_category_to_csv(file_dir, file_name, headers, rows):
    with open(file_dir + f'{file_name}.csv', 'w', encoding='utf-8', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(headers)
        csvwriter.writerows(rows)


def delay(min_sec, max_sec=None):
    if max_sec is None:
        max_sec = min_sec
    sleep(random.randint(min_sec, max_sec + 1))


def slugify(value, allow_unicode=False):
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    value = re.sub(r'[-\s]+', '-', value).strip('-_')
    if len(value) > 50:
        value = value[0:50]
    return value
