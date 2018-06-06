'''
Este archivo es parte de dynserver. 
dynserver es software libre: puede redistribuirlo y/o modificado 
bajo los términos de la Licencia Pública General Affero de GNU como
publicado por la Free Software Foundation, ya sea la versión 3 de la
Licencia, o (a su elección) cualquier versión posterior. 

dynserver se distribuye con la esperanza de que sea útil, pero 
SIN NINGUNA GARANTÍA; sin siquiera la garantía implícita de 
COMERCIABILIDAD o IDONEIDAD PARA UN PROPÓSITO PARTICULAR. Vea la 
Licencia pública general Affero de GNU para más detalles. 

Deberías haber recibido una copia de la Licencia Pública General 
Affero de GNU junto con dynserver. Si no, mira.  <http://www.gnu.org/licenses/>.

Esta es una version basada en el trabajo de Dustin Frisch 2013
y soportada por el instituto de gobierno para la plataforma maxive
'''

import setuptools


version = open('./VERSION').read().strip()

setuptools.setup(
    license = 'GNU AGPLv3',

    name = 'dynserver',
    version = version,

    author = 'Cleb Arantes',
    author_email = 'clebaresu@gmail.com',

    url = 'https://dynserver.maxive.pe',

    description = 'Una aplicacion de la plataforma Maxive para gestion dinamica de DNS.',
    long_description = open('README.md').read(),
    keywords = 'dynserver dinamic dns nsupdate',

    install_requires = [
        'beaker >= 1.6',
        'bottle >= 0.11',
        'jinja2 >= 2.6',
        'formencode >= 1.3.0a1',
        'passlib >= 1.6',
        'mysql-connector-python >= 2.0.0',
        'require >= 0.1.0',
        'requests >= 2.5.0',
        'enum34 >= 1.0.0',
        'configparser >= 3.2'
    ],

    packages = setuptools.find_packages(),

    zip_safe = False,

    package_data = {
        'dynserver.resources': [
            'email/*.mail',
            'web/css/*.css',
            'web/fonts/*',
            'web/js/*.js',
            'templates/*.html',
        ],
    },
    include_package_data = True,

    data_files = [
        ('/etc/dynserver', ['dynserver/resources/doc/dynserver.conf.example',
                           'dynserver/resources/doc/motd']),
        ('/etc/init.d', ['dynserver/resources/doc/debian.init.d/dynserver']),
        ('/usr/share/dynserver/static/css', ['dynserver/resources/web/css/bootstrap.min.css',
                                            'dynserver/resources/web/css/bootstrap-theme.min.css',
                                            'dynserver/resources/web/css/font-awesome.min.css',
                                            'dynserver/resources/web/css/dynserver.css'
                                            ]),
        ('/usr/share/dynserver/static/fonts', ['dynserver/resources/web/fonts/FontAwesome.otf',
                                              'dynserver/resources/web/fonts/fontawesome-webfont.eot',
                                              'dynserver/resources/web/fonts/fontawesome-webfont.svg',
                                              'dynserver/resources/web/fonts/fontawesome-webfont.ttf',
                                              'dynserver/resources/web/fonts/fontawesome-webfont.woff'
                                              ]),
        ('/usr/share/dynserver/static/js', ['dynserver/resources/web/js/bootstrap.min.js',
                                           'dynserver/resources/web/js/Chart.min.js',
                                           'dynserver/resources/web/js/jquery.min.js',
                                           'dynserver/resources/web/js/pwstrength.js',
                                           'dynserver/resources/web/js/pwstrength.options.js'
                                           ]),
        ('/usr/share/doc/dynserver', ['dynserver/resources/doc/schema.sql',
                                     'dynserver/resources/doc/schema.upgrade.sql',
                                     'dynserver/resources/doc/dynserver.conf.example',
                                     'dynserver/resources/doc/dyncliente.conf.example',
                                     'README.md', 'INSTALL.md', 'VERSION', 'LICENSE',
                                     'CHANGES.md', 'UPGRADING.md']),
        ('/usr/share/doc/dynserver/centos.init.d', ['dynserver/resources/doc/centos.init.d/dynserver']),
        ('/usr/share/doc/dynserver/debian.init.d', ['dynserver/resources/doc/debian.init.d/dynserver'])
    ],

    entry_points = {
        'console_scripts': [
            'dynserver-interface = dynserver.interface.__main__:main',
            'dynserver-updater = dynserver.updater.__main__:main',
            'dynserver-bundle = dynserver.__main__:main',
            'dynserver-recursor = dynserver.recursor.__main__:main',
        ]
    },
)
