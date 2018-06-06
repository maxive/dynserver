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

import bottle

from require import extend, export, require

from dynserver.config import parse_bool



@extend('dynserver.config:ConfigDeclaration')
def config_web(config_decl):
  with config_decl.declare('wsgi') as s:
    s('host',
      conv = str,
      default = '0.0.0.0')
    s('port',
      conv = int,
      default = 8080)
    s('debug',
      conv = parse_bool,
      default = False)



@export()
def WebApp():
  # Create a new bottle application
  return bottle.Bottle()



@export(webapp = 'dynserver.web:WebApp')
def Middleware(webapp):
  # Return the webapp as initial middleware
  return webapp



def route(*args, **kwargs):
  def wrapper(func):

    @extend('dynserver.web:WebApp')
    def extender(webapp):
      webapp.route(*args, **kwargs)(func)

    return extender
  return wrapper



@export()
class Web(object):
  @require(config = 'dynserver.config:Config',
           middleware = 'dynserver.web:Middleware')
  def run(self,
          config,
          middleware):
    bottle.run(app = middleware,
               host = config.wsgi.host,
               port = config.wsgi.port,
               debug = config.wsgi.debug)
