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

'''

from require import require

import dynserver.interface.pages.index  # @UnusedImport: for web application
import dynserver.interface.pages.signup  # @UnusedImport: for web application
import dynserver.interface.pages.lostpasswd  # @UnusedImport: for web application
import dynserver.interface.pages.login  # @UnusedImport: for web application
import dynserver.interface.pages.user.account  # @UnusedImport: for web application
import dynserver.interface.pages.user.hosts  # @UnusedImport: for web application
import dynserver.interface.pages.user.host  # @UnusedImport: for web application
import dynserver.interface.pages.admin.users  # @UnusedImport: for web application
import dynserver.interface.pages.admin.suffixes  # @UnusedImport: for web application

import dynserver.updater.nic  # @UnusedImport: for web application



@require(web = 'dynserver.web:Web')
def main(web):
  # Set up web server and run it
  web.run()



if __name__ == '__main__':
    main()
