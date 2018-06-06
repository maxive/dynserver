dynserver - Upgrade instructions
===============================

If you are performing a fresh installation, please follow the
instructions given in file INSTALL.

If you are upgrading from a previous version of dynserver, please
follow the instructions below, that match the version you are
upgrading from.

In any case, you should create a backup of your dynserver database
before you perform an upgrade!


Si está realizando una instalación nueva, siga las instrucciones 
dadas en el archivo INSTALAR. Si está actualizando desde una versión 
anterior de dynserver, por favor siga las instrucciones a continuación, 
que coinciden con la versión que está actualizar desde. 

En cualquier caso, debe crear una copia de seguridad de su base de datos
dynserver antes de realizar una actualización!



Actualizando desde 0.1.x
--------------------

1. Make a backup of your dynserver database!
2. Stop dynserver.
3. Unpack and install the new version of dynserver.
   python setup.py install
4. Apply all the SQL statements from file
   dynserver/resources/doc/schema.upgrade.sql to your database.
5. Check /etc/dynserver/dynserver.conf.example for new configuration
   parameters and add them to your own configuration file
6. Start dynserver.
7. Restart powerdns ro reload the dynserver-recursor.
