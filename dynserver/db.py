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

import contextlib
import threading

import mysql.connector

from require import extend, export, require



@extend('dynserver.config:ConfigDeclaration')
def config_db(config_decl):
  with config_decl.declare('db') as s:
    s('host',
      conv = str,
      default = 'localhost')
    s('port',
      conv = int,
      default = 3306)
    s('name',
      conv = str,
      default = 'dynserver')
    s('username',
      conv = str,
      default = 'dynserver')
    s('password',
      conv = str)



@export()
class Database(object):

  thread_local = threading.local()

  @contextlib.contextmanager
  @require(config = 'dynserver.config:Config')
  def cursor(self, config):
    # Ensure we have a connection for this thread
    if not hasattr(self.thread_local, 'connection'):
      connection = mysql.connector.connect(host = config.db.host,
                                           port = config.db.port,
                                           user = config.db.username,
                                           password = config.db.password,
                                           database = config.db.name,
                                           charset = 'utf8')
      setattr(self.thread_local, 'connection', connection)

    else:
      # Use existing connection
      connection = getattr(self.thread_local, 'connection')

      # Reconnect if connection is down
      connection.ping(True)

    cursor = connection.cursor(dictionary=True)

    try:
      yield cursor

    except:
      connection.rollback()
      raise

    else:
      connection.commit()

    finally:
      cursor.close()
