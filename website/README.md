Layout
=====================

Frontend is the UI which provides the tool and feel of the system.
Tracker is the backend which keeps track of stats about the system.

Initial Configuration
=====================

To get the code and dependencies:

    git clone git@github.com:timvideos/streaming-system.git
    cd streaming-system/website
    make

Running a test server
=====================

Simply ``make serve``; this will configure a virtualenv, download and install
dependencies (inside the virtualenv; your system will not be touched); and a
test server will be started.

If this is your first time running ``make serve`` you'll be prompted to provide
a username and password for an admin account.

Registering a flumotion encoder server onto frontend
====================================================

```cd ../tools/register/```

```python fake_register.py --ip 127.0.0.1```

Sample output:

    Registered av at 2013-04-24 09:32:43.961403 result OK
    Registered av at 2013-04-24 09:32:45.130072 result OK
    ...

This keeps on going.

Open http://127.0.0.1:8000/av?template=group to view the page

Note: DO NOT run ``make serve`` as root. If you do, virtualenv folders won't have write permissions, so fake_register.py won't be able to write to sqlite database.

Production Deployment
=====================

 *  To account for differences between the dev and prod infrastructure a
    config-private.json can be provided at the base level directory.

 *  The deployment uses one user to deploy the code, and another user to
    run the code:

        tim@website:~$ grep website /etc/passwd /etc/group
        /etc/passwd:website:x:100:100::/home/website:/bin/bash
        /etc/passwd:website-run:x:101:101::/home/website-run:/bin/false
        /etc/group:website:x:101:tim
        /etc/group:website-run:x:105:website,tim

 *  Usually, the run user should only need read access to the files you've
    checked out. If there are specific files or directories that the run user
    needs to write to, simply use ``chgrp website-run $FILE; chmod g+w $FILE``
    to make them accessible to both the deploy and run users. If this needs to
    be persisted across deployments, you may have to take care of this in your
    deploy script.

 *  To do the deployment, I use the ``setup.sh`` script in conf directory. It
    takes a copy of the current code in ``~website/timvideos`` and puts it in
    ``~website/$VERSION-$DATE-$TIME`` directory and then links
    ``~website/current`` to that.

    This makes it relatively easy to revert to an earlier version of the code.

 *  The app runs inside [Green Unicorn][], and is started by
    [upstart][]. Take a look at conf/init.conf

 *  The app uses [nginx][] as a frontend, and to serve static files. Only a few
    changes from the default config are needed to accomplish this.

    Take a look at conf/nginx.conf

  [deploy key]: http://help.github.com/deploy-keys/
  [Green Unicorn]: http://gunicorn.org/
  [upstart]: http://upstart.ubuntu.com/
  [nginx]: http://nginx.org/en/ "nginx"
