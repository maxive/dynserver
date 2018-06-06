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

import beaker.middleware

from require import export, extend, require



@extend('dynserver.web:Middleware')
def middleware_session(middleware):
  return beaker.middleware.SessionMiddleware(middleware,
                                             {'session.cookie_expires': True})



@export()
class SessionManager(object):
  def __init__(self):
    pass


  @property
  def session(self):
    return bottle.request.environ.get('beaker.session')


  def __getattr__(self, key):
    try:
      return self.session[key]

    except KeyError:
      return None


  def __setattr__(self, key, value):
    self.session[key] = value


  def __delattr__(self, key):
    del self.session[key]


  def save(self):
    self.session.save()



@extend('dynserver.interface.template:TemplateManager')
def template_session(templates):
  @require(session = 'dynserver.interface.session:SessionManager')
  def __(session):
    return session

  templates.globals['session'] = __
