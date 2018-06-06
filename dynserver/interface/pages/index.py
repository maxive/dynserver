"""
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

"""

import os

import bottle

from dynserver.web import route

from dynserver.interface.user import authorized

from require import require, extend



@extend('dynserver.config:ConfigDeclaration')
def config_wsgi(config_decl):
  with config_decl.declare('wsgi') as s:
    s('static_files',
      conv = str,
      default = '/usr/share/dynserver/static')



@route('/static/<path:path>', method = 'GET')
@require(config = 'dynserver.config:Config')
def get_static(path,
               config):
  """ Provides a route to static files (like css, images, etc).
  """

  return bottle.static_file(path,
                            root = config.wsgi.static_files)



@route('/', method = 'GET')
@require(db = 'dynserver.db:Database',
         templates = 'dynserver.interface.template:TemplateManager',
         session = 'dynserver.interface.session:SessionManager')
def get_index(db,
              templates,
              session):
  """ Display the index page.
  """

  if session.username:
    motd = None
    if os.path.isfile('/etc/dynserver/motd'):
      motd = open('/etc/dynserver/motd').read()

    (users, zones, hosts, userhosts) = get_statistics()

    return templates['index.html'](users = users,
                                   zones = zones,
                                   hosts = hosts,
                                   userhosts = userhosts,
                                   current_ip = bottle.request.remote_addr,
                                   motd = motd)

  else:
    return templates['index.html']()



@require(db = 'dynserver.db:Database')
@authorized()
def get_statistics(user,
                   db):
  """ collect some statistics, which will be displayed on the index page
  """
  with db.cursor() as cur:
    cur.execute('''
      SELECT COUNT(`id`) AS count
      FROM `users`
    ''')
    users = cur.fetchone()

    cur.execute('''
      SELECT COUNT(`id`) AS count
      FROM `suffixes`
    ''')
    zones = cur.fetchone()

    cur.execute('''
      SELECT COUNT(`id`) AS count
      FROM `hosts`
    ''')
    hosts = cur.fetchone()


    cur.execute('''
      SELECT COUNT(`id`) AS count
      FROM `hosts`
      WHERE `user_id` = %(user_id)s
    ''', {'user_id': user.id })
    userhosts = cur.fetchone()

    return (users, zones, hosts, userhosts)
