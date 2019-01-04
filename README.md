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

    $ bin/instance1 run /home/zope/export_users/export_plone_users.py --plone-path Plone

OR

Using imio.updates (to run on all / selected instances)

    $ bin/update_instances -c /home/zope/export_users/export_plone_users.py -d

And now you have a new users.csv file with all users.
