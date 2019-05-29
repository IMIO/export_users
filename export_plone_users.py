# -*- coding: utf-8 -*-
from plone import api

import argparse
import csv
import logging
import requests
import sys


app_ids = ["iA.Smartweb", "iA.Delib", "iA.Docs", "iA.Urban", "iA.PST"]


logger = logging.getLogger("export_plone_users.py")
logger.setLevel(logging.INFO)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
formatter = logging.Formatter(
    "%(asctime)s %(levelname)s %(name)s %(message)s", "%Y-%m-%d %H:%M:%S"
)
ch.setFormatter(formatter)
logger.addHandler(ch)

parser = argparse.ArgumentParser(description="Run a script")
parser.add_argument(
    "-a",
    dest="app_id",
    help="Set application id (example: iA.Smartweb, iA.Delib, ...)",
    required=True,
    choices=app_ids,
)
parser.add_argument(
    "-m",
    dest="mun_id",
    help="Set municipality id (example: liege, namur, ...)",
    required=True,
    default="",
)
parser.add_argument(
    "-s",
    dest="mun_slug",
    help="Set municipality slug, slug it's a company number from 'Banque-Carrefour des Entreprises'",
    required=True,
    default="",
)

# parser.add_argument("-c")  # use to bin/instance run script.py

# remove -c script_name from args before argparse runs:
if "-c" in sys.argv:
    index = sys.argv.index("-c")
    del sys.argv[index]
    del sys.argv[index]

arg = parser.parse_args()
mun_id = arg.mun_id
app_id = arg.app_id
mun_slug = arg.mun_slug
formated_app_id = app_id.lower().replace(".", "")
app_name = "users"
memroy_base_url = "http://memory-prod1.imio.be:6543"
# memroy_base_url = "http://localhost:6543"


def get_users():
    users = []
    pas = api.portal.get().acl_users
    passwords = dict(pas.source_users._user_passwords)
    list_members = api.user.get_users()
    for member in list_members:
        user = {}
        user["app_id"] = app_id
        user["mun_id"] = mun_id
        user["mun_slug"] = mun_slug
        user["user_id"] = member.getId()
        user["username"] = member.getId()
        user["content_id"] = member.getId()
        user["fullname"] = member.getProperty("fullname", member.getUserName())
        user["email"] = member.getProperty("email", None)
        user["password"] = passwords.get(user["user_id"])
        allowed_services = []
        allowed_services.append("{0}-{1}".format(mun_id, formated_app_id))
        user["allowed_services"] = allowed_services
        users.append(user)
    return users


def create_csv(users, exported_filename="users.csv", delimiter=","):
    with open(exported_filename, "wb") as csvfile:
        filewriter = csv.writer(
            csvfile, delimiter=delimiter, quotechar="|", quoting=csv.QUOTE_MINIMAL
        )
        # first_line = users[0].keys()
        first_line = ["id", "name", "email", "password"]
        filewriter.writerow(first_line)
        for user in users:
            user_line = [user[id] for id in first_line]
            filewriter.writerow(user_line)
        logger.info("{0} users exported on {1}".format(len(users), exported_filename))


def add_root():
    url = "{0}/{1}".format(memroy_base_url, app_name)
    req = requests.get(url)
    if req.status_code == 404:
        requests.post(memroy_base_url, json={"app_id": app_name})


def add_municipality(mun_id):
    url = "{0}/{1}".format(memroy_base_url, app_name)
    req = requests.get(url)
    if not req or mun_id not in req.json():
        params = {"container_id": mun_id}
        req = requests.post(url, json=params)


def add_app(mun_id, app_id):
    url = "{0}/{1}/{2}".format(memroy_base_url, app_name, mun_id)
    req = requests.get(url)
    if req.status_code == 404:
        add_municipality(mun_id)
    req = requests.get(url)
    if app_id not in req.json():
        params = {"container_id": app_id}
        req = requests.post(url, json=params)


def add_user(user):
    url = "{0}/{1}/{2}/{3}".format(
        memroy_base_url, app_name, user["mun_id"], user["app_id"]
    )
    params = user
    requests.post(url, json=params)
    # print(f'\tUser {user["user_id"]} added from {user["app_id"]}')


def export_to_memory(users):
    add_app(mun_id, app_id)
    line_count = 0
    for user in users:
        add_user(user)
        line_count += 1
        logger.info("{0}/{1} user added".format(line_count, len(users)))


if __name__ == "__main__":
    add_root()
    users = get_users()
    export_to_memory(users)
