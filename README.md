IMIO export users to authentic
==============================

This project is used to migrated users to csv file, which can be use by authentic.

Plone
-----
To use this project on plone servers, start export_plone_users.py as run script.

First, clone this repo on servers

    $ cd
    $ git clone https://github.com/IMIO/export_users.git

Then go to your instance directory and use script as

    $ bin/instance1 -O Plone run /home/imio/export_users/export_plone_users.py -a iA.Smartweb -m liege -s 80265465464

OR

Using imio.updates (to run on all / selected instances)

    $ bin/update_instances -c /home/zope/export_users/export_plone_users.py -d

And now you have a new users.csv file with all users.



Authentic
---------
To use this project in docker-teleservice container :

$ authentic2-multitenant-manage tenant_command runscript -d COMMUNE-auth.DOMAIN export-authentic-users.py -a iA.Teleservice -m liege -s 80265465464



Delete bad import
-----------------
User REST command with curl (for example)

    $ curl -X DELETE http://localhost:6543/users/liege/iA.Smartweb

Todo
----
- [X] Add arguments to choose app_id and mun_id
- [X] Send exported users to centralized data base
- [ ] Do not export test users
