dynserver - Un servidor de DNS dinámico
=======================================

Acerca
------

Una aplicacion de la plataforma Maxive para gestion dinamica de DNS.

It allows you to specify hostnames (subdomains) inside a dynamic DNS zone, and
to update the IPv4 address of those hostnames using the dyndns2 update protocol
(http://www.noip.com/integrate). This enables you to access hosts with dynamic
IP addresses by a static domain name, even if the IP address changes.

Le permite especificar nombres de host (subdominios) dentro de una zona DNS dinámica, 
y actualizar la dirección IPv4 de esos nombres de host utilizando el protocolo de 
actualización dyndns2 (http://www.noip.com/integrate). Esto le permite acceder a 
hosts con dinámica Direcciones IP por un nombre de dominio estático, incluso si 
la dirección IP cambia.


Características
---------------

* Interfaz de usuario web agradable e intuitiva
   - Registro automático / semiautomático o gestión manual de usuarios
   - Los administradores pueden agregar y administrar zonas
   - Los usuarios pueden agregar y administrar nombres de host
   - Re-captcha apoyo
* Actualización de la dirección IP utilizando el protocolo dyndns2
   - Actualizar múltiples nombres de host a la vez
   - Funciona con la mayoría de los homerouters, dyncliente o incluso wget
   - Actualizaciones manuales de la dirección IP a través de la interfaz de usuario web
* Soporte para múltiples dominios
* Número configurable de hosts por usuario
* Fuerte encriptación de todas las contraseñas (host y usuario)
* Admite instalación distribuida
   - Paquetes separados para Web-UI, updater y DNS-backend
   - Soporte de redundancia


Modo de operación
-----------------

dynserver está escrito en Python (2.7) utilizando Bottle Web Framework y viene
con un frontend HTML5 limpio usando el framework Bootstrap3 CSS.

Toda la información de usuario y nombre de host se almacena en una base de datos
MySQL. Por nombre.
el dynserver de resolución depende de PowerDNS como servidor DNS.

Las partes individuales de dynserver, que pueden ejecutarse en un servidor, o distribuidas
en diferentes máquinas, son

* dynserver-bundle es la versión incluida de
   - Interfaz dynserver: una interfaz web bonita para agregar nombres de host o zonas y administrar usuarios.
   - dynserver-updater: la implementación del protocolo de actualización dyndns2.
* dynserver-recursor responde las consultas DNS. Se ejecuta como un backend de tubería para el servidor PowerDNS.

License
-------

dynserver es software libre y puede ser redistribuido y / o modificado bajo el
términos de la Licencia Pública General Affero de GNU publicada por el
Software Foundation, ya sea la versión 3 de la Licencia, o (a su opción) cualquier
última versión.
