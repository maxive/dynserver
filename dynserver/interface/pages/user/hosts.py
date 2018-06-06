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

from require import extend, require

from dynserver.web import route

from dynserver.interface.user import authorized

from dynserver.interface import validation
from dynserver.interface.validation import validate

from passlib.apps import custom_app_context as pwd



@extend('dynserver.config:ConfigDeclaration')
def config_auth(config_decl):
  with config_decl.declare('dns') as s:
    s('max_hosts',
       conv = int,
       default = 5)


@route('/user/hosts/list', method = 'GET')
@authorized()
@require(db = 'dynserver.db:Database',
         templates = 'dynserver.interface.template:TemplateManager')
def get_hosts_display(user,
                      db,
                      templates):
  ''' Display a list of the users hostnames '''

  with db.cursor() as cur:
    # Get hosts of the user
    cur.execute('''
        SELECT
          `host`.`id` AS `id`,
          `host`.`hostname` AS `hostname`,
          `suffix`.`name` AS `suffix`,
          `host`.`address` AS `address`,
          `host`.`address_v6` AS `address_v6`,
          `host`.`updated` AS `updated`,
          `host`.`description` AS `description`
        FROM `hosts` AS `host`
        LEFT JOIN `suffixes` AS `suffix`
          ON ( `suffix`.`id` = `host`.`suffix_id` )
        WHERE `user_id` = %(user_id)s
    ''', {'user_id': user.id})
    hosts = cur.fetchall()

  return templates['hosts.html'](hosts = hosts)



@route('/user/hosts/add', method = 'GET')
@authorized()
@require(db = 'dynserver.db:Database',
         templates = 'dynserver.interface.template:TemplateManager')
def get_hosts_add(user,
                  db,
                  templates):
  ''' Display a form for adding new hostnames '''

  with db.cursor() as cur:
    # Get all available suffixes
    cur.execute('''
        SELECT *
        FROM `suffixes`
    ''')
    suffixes = cur.fetchall()

  return templates['addhost.html'](suffixes = suffixes,
                                   current_ip = bottle.request.remote_addr)



@route('/user/hosts/add', method = 'POST')
@authorized()
@validate('/user/hosts/add',
          hostname = validation.ValidHostname(),
          suffix = validation.Int(not_empty = True),
          address = validation.IPAddress(),
          address_v6 = validation.IPv6Address(),
          description = validation.String(max = 255),
          password = validation.SecurePassword(min = 8),
          password_confirm = validation.String(),
          chained_validators = [validation.FieldsMatch('password', 'password_confirm'),
                                validation.UniqueHostname('hostname', 'suffix')])
@require(db = 'dynserver.db:Database',
         config = 'dynserver.config:Config',
         messages = 'dynserver.interface.message:MessageManager')
def post_hosts_add(user,
                   data,
                   db,
                   config,
                   messages):
  ''' Add a new hostname. '''

  # We do net check passed suffix, as mysql will tell us later on

  with db.cursor() as cur:
    # Users can have an individual hostname limit, unlimited hostnames (-1)
    # or have no limit set in the db to use the default from the config
    cur.execute('''
      SELECT COUNT(*) AS count
      FROM `hosts`
      WHERE `user_id` = %(user_id)s
    ''', {'user_id': user.id})

    count = cur.fetchone()
    if not ((user.maxhosts is None and (count['count'] < config.dns.max_hosts)) or
            (user.maxhosts is not None and (count['count'] < user.maxhosts)) or
            (user.maxhosts == -1)):
      messages.error('Maximum number of hosts reached')
      bottle.redirect('/user/hosts/add')

    # Encrypt the host password for for storage
    encrypted_password = pwd.encrypt(data.password)

    cur.execute('''
      INSERT
      INTO `hosts`
      SET `hostname` = %(hostname)s,
          `address` = %(address)s,
          `address_v6` = %(address_v6)s,
          `description` = %(description)s,
          `password` = %(password)s,
          `user_id` = %(user_id)s,
          `suffix_id` = %(suffix_id)s
    ''', {'hostname': data.hostname,
          'address': data.address,
          'address_v6': data.address_v6,
          'description': data.description,
          'password': encrypted_password,
          'user_id': user.id,
          'suffix_id': data.suffix})

  messages.success('Ok, done.')

  bottle.redirect('/user/hosts/list')



@route('/user/hosts/delete', method = 'POST')
@authorized()
@validate('/user/hosts/list',
          host_id = validation.Int(not_empty = True))
@require(db = 'dynserver.db:Database',
         messages = 'dynserver.interface.message:MessageManager')
def post_hosts_delete(user,
                      data,
                      db,
                      messages):
  ''' Delete a hostname. '''

  # We do not check the host id for existence and belonging as we only delete
  # host of the user

  with db.cursor() as cur:
    cur.execute('''
        DELETE
        FROM hosts
        WHERE id = %(host_id)s
          AND user_id = %(user_id)s
    ''', {'host_id': data.host_id,
          'user_id': user.id})

  messages.success('Ok, done.')

  bottle.redirect('/user/hosts/list')
