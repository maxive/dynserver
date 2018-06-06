'''
CEste archivo es parte de dynserver. 
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

import bottle

from require import require

from dynserver.web import route

from dynserver.interface.user import authorized_by_code

from dynserver.interface import validation
from dynserver.interface.validation import validate



@route('/login', method = 'POST')
@validate('/',
          username = validation.ValidUsername(min = 1, max = 255),
          password = validation.String())
@require(users = 'dynserver.interface.user:UserManager')
def post_login(data,
               users):
  ''' Handles user authentication. '''

  users.login(username = data.username,
              password = data.password)

  bottle.redirect('/')



@route('/logout', method = 'GET')
@require(users = 'dynserver.interface.user:UserManager')
def get_logout(users):
  ''' Handles user logout. '''

  users.logout()

  bottle.redirect('/')
