dynserver - Instrucciones de instalacion
========================================

Bienvenido a dynserver.


Prerequisitos
-------------

Before you start to install dynserver, please make sure that you have installed
python2.7, MySQL and PowerDNS (including the pipe-backend) on your server.

On Debian GNU/Linux you will need to install these packages:

 libmysqlclient-dev
 python-dev
 python-setuptools

On CentOS you will need to install these packages:

 mysql-devel
 python-devel
 python-setuptools


Instalación
------------

1. To install dynserver you can just run:
```
    python setup.py install
```

2. After this step, dynserver installed to the following locations:
  * /usr/local/lib/python2.7/dist-packages/ contains the installed python packages
  * /etc/dynserver contains the configuration file
  * /etc/init.d/dynserver is a debian init-script for controlling dynserver
  * /usr/share/doc/dynserver contains the database schema and some readme files
  * /usr/share/dynserver contains static files like CSS, JavaScript, eMail-Templates, ..
  * /usr/local/bin contains the dynserver executables

3. Create a new database (i.e. named dynserver) and a database user with
   usage privileges (at least SELECT, DELETE, UPDATE) for the database.

4. Install the database using /usr/share/doc/dynserver/schema.sql

  Note: When installing the default database schema, an initial user will be
  installed to log into the Web-UI. The default login is: admin:admin

5. Copy the configuration file /etc/dynserver/dynserver.conf.example to
   /etc/dynserver/dynserver.conf and edit it to fit your needs.

6. Start dynserver using /etc/init.d/dynserver

7. Run the dynserver-recursor by adding the following lines to your powerdns
   configuration and restart powerdns.
```
    launch=pipe
    pipe-command=/usr/local/bin/dynserver-recursor
```

Documentación y Soporte
-----------------------

Please refer to https://dynserver.maxive.pe for further documentation and
support. If you have any problems using dynserver you can send an email
to dynserver@0x80.io or file a bugreport at
https://github.com/dynserver/dynserver/issues
