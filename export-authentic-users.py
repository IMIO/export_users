# -*- coding: utf-8 -*-
# usage : authentic2-multitenant-manage tenant_command runscript -d COMMUNE-auth.DOMAIN /opt/publik/scripts/build-e-guichet/export-authentic-users.py -a app_id -m mun_id -s mun_slug
# with memory for historic 
# sample : http://memory-prod1.imio.be:6543/users/liege/json
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django_rbac.utils import get_role_model, get_ou_model
from hobo.agent.authentic2.provisionning import provisionning
import argparse
import csv
import hashlib
import requests
import sys

parser = argparse.ArgumentParser(description="Run a script")
parser.add_argument(
    "-a",
    dest="app_id",
    help="Set application id (example: iA.Teleservice)",
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

arg = parser.parse_args()
mun_id = arg.mun_id
app_id = arg.app_id
mun_slug = arg.mun_slug
app_name = "users"
formated_app_id = app_id.lower().replace(".", "")
memroy_base_url = "http://memory-prod1.imio.be:6543"

def writerow(columns):
    with open("/var/tmp/{}.csv".format("{}_export".format(mun_id)), "a") as csvfile:
        csvwriter = csv.writer(csvfile, delimiter="|",
            quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
        csvwriter.writerow(columns)


def export_authentic_user_to_csv(mun_id, app_id):
    columns = ["municipality_id","app_id","user_id","fullname","email","password","old_{}_password".format(app_id),"old_{}_userid".format(app_id)]
    writerow(columns)
    User = get_user_model()
    users = User.objects.all()
    for user in users:
        columns = []
        columns.append(mun_id)
        columns.append(app_id)
        columns.append(user.uuid)
        columns.append("{} {}".format(user.first_name, user.last_name))        
        columns.append(user.email)        
        columns.append(user.password)
        columns.append(user.uuid)
        writerow(columns)

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

def export_authentic_user_to_memory(users):
    add_app(mun_id, app_id)
    line_count = 0
    for user in users:
        add_user(user)
        line_count += 1
        # logger.info("{0}/{1} user added".format(line_count, len(users)))

def get_users():
    columns = ["municipality_id","app_id","user_id","fullname","email","password","old_{}_password".format(app_id),"old_{}_userid".format(app_id)]
    writerow(columns)
    members = []
    User = get_user_model()
    users = User.objects.all()
    for user in users:
        current_user = {}
        current_user["app_id"] = app_id
        current_user["mun_id"] = mun_id
        current_user["mun_slug"] = mun_slug
        current_user["user_id"] = user.email
        current_user["username"] = user.username
        current_user["content_id"] = user.uuid
        current_user["fullname"] = u"{} {}".format(user.first_name, user.last_name)
        current_user["email"] = user.email
        current_user["password"] = user.password
        allowed_services = []
        allowed_services.append("{0}-{1}".format(mun_id, formated_app_id)) 
        current_user["allowed_services"] = allowed_services
        members.append(current_user)
    return members

# export_authentic_user_to_csv(mun_id, app_id)
add_root()
users = get_users()
export_authentic_user_to_memory(users)
