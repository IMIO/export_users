#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import logging
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

APPLICATIONS = [
    {
        "slug": "liege-renocopro",
        "title": "Liège Reno Copro",
        "URL": "https://renocopro.staging.imio.be",
        "": "",
    }
]


def create_json(data, exported_filename="services.json"):
    with open(exported_filename, "wb") as jsonfile:
        json.dump(data, jsonfile)
        logger.info(
            "{0} services exported on {1}".format(
                len(data["services"]), exported_filename
            )
        )


def get_services():
    result = {}
    services = []
    for app in APPLICATIONS:
        service = {}
        service["name"] = app["title"]
        service["slug"] = app["slug"]
        service["client_id"] = ""
        service["client_secret"] = ""
        service["redirect_uris"] = [
            "{0}/authentic-handler/authentic-usagers".format(app["URL"])
        ]
        service["post_logout_redirect_uris"] = [app["URL"]]
        service["frontchannel_logout_uri"] = "{0}/logout".format(app["URL"])
        service["open_to_all"] = True
        services.append(service)
    result["services"] = services
    result["locality"] = {"name": "Liege, AC"}
    return result


if __name__ == "__main__":
    services = get_services()
    create_json(services)
