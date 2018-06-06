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

import enum
import collections

from require import export, require, extend



@export()
class MessageManager(object):
  class Level(enum.Enum):
    success = 'success'
    error = 'error'

  Message = collections.namedtuple('Message', ['level',
                                               'message'])


  def __init__(self):
    self.__messages = []


  @require(session = 'dynserver.interface.session:SessionManager')
  def __push(self, level, message, session):
    if not session.messages:
      session.messages = []

    session.messages.append(self.Message(level = level,
                                         message = message))
    session.save()


  def success(self, message):
    self.__push(self.Level.success, message)


  def error(self, message):
    self.__push(self.Level.error, message)


  @require(session = 'dynserver.interface.session:SessionManager')
  def popall(self, session):
    if not session.messages:
      return []

    messages = session.messages

    session.messages = []
    session.save()

    return messages



@extend('dynserver.interface.template:TemplateManager')
def template_message(template):
  @require(messages = 'dynserver.interface.message:MessageManager')
  def __(messages):
    return messages

  template.globals['messages'] = __
