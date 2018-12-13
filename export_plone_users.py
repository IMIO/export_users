# -*- coding: utf-8 -*-
from AccessControl.SecurityManagement import newSecurityManager
from plone import api
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Testing import makerequest
from zope.component.hooks import setSite
from zope.globalrequest import setRequest

import argparse
import csv
import logging
import sys


logger = logging.getLogger('export_plone_users.py')
logger.setLevel(logging.INFO)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s',
                              '%Y-%m-%d %H:%M:%S')
ch.setFormatter(formatter)
logger.addHandler(ch)

parser = argparse.ArgumentParser(description='Run a script')
parser.add_argument('--plone-path', dest='plone_path',
                    help='Set plone path (example: liege/liege)',
                    default='')
parser.add_argument('-c')  # use to bin/instance run script.py


def get_site(app, path=''):
    zopeapp = makerequest.makerequest(app)
    zopeapp.REQUEST['PARENTS'] = [app]
    setRequest(zopeapp.REQUEST)
    # newSecurityManager(None, user)
    user = app.acl_users.getUser('admin')
    newSecurityManager(None, user.__of__(app.acl_users))
    portal = None
    if not path:
        for oid in app.objectIds():
            obj = app[oid]
            if IPloneSiteRoot.providedBy(obj):
                portal = obj
    else:
        container = app
        for name in path.split('/'):
            if name in container.objectIds():
                container = container[name]
            else:
                error = 'Bad path {0}'.format(name)
                logger.error(error)
                raise(error)
        portal = container
    if not portal:
        error = 'Do not find portal'
        logger.error(error)
        raise(error)
    setSite(portal)
    return portal


def get_users(portal):
    users = []
    pas = api.portal.get().acl_users
    passwords = dict(pas.source_users._user_passwords)
    list_members = api.user.get_users()
    for member in list_members:
        user = {}
        user['id'] = member.getId()
        user['name'] = member.getProperty('fullname', member.getUserName())
        user['email'] = member.getProperty('email', None)
        # user['fullname'] = member.getProperty('fullname', None)
        # user['roles'] = member.getRoles()
        # user['domains'] = member.getDomains()
        user['password'] = passwords.get(user['id'])
        users.append(user)
    return users


def create_csv(users, exported_filename='users.csv', delimiter=','):
    with open(exported_filename, 'wb') as csvfile:
        filewriter = csv.writer(
            csvfile,
            delimiter=delimiter,
            quotechar='|',
            quoting=csv.QUOTE_MINIMAL
        )
        # first_line = users[0].keys()
        first_line = ['id', 'name', 'email', 'password']
        filewriter.writerow(first_line)
        for user in users:
            user_line = [user[id] for id in first_line]
            filewriter.writerow(user_line)
        logger.info(
            '{0} users exported on {1}'.format(len(users), exported_filename))


if __name__ == '__main__':
    args = parser.parse_args()
    plone_path = args.plone_path
    portal = get_site(app, plone_path)  # noqa
    users = get_users(portal)
    create_csv(users)
