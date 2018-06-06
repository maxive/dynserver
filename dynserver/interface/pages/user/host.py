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

from require import extend, require

from dynserver.web import route

from dynserver.interface.user import authorized

from dynserver.interface import validation
from dynserver.interface.validation import validate

from passlib.apps import custom_app_context as pwd
import formencode



@route('/user/host/<host_id>', method = 'GET')
@authorized()
@require(db = 'dynserver.db:Database',
         templates = 'dynserver.interface.template:TemplateManager',
         messages = 'dynserver.interface.message:MessageManager')
def get_host_display(user,
                     host_id,
                     db,
                     templates,
                     messages):
  ''' Display the users hostnames and a form for adding new ones. '''

  with db.cursor() as cur:
    # Get host details
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
        WHERE `host`.`id` = %(id)s
          AND `host`. `user_id` = %(user_id)s
    ''', {'id': host_id,
          'user_id': user.id})
    host = cur.fetchone()

  if host is None:
    messages.error('Hostname not found or no access!')
    bottle.redirect('/user/hosts/list')

  return templates['host.html'](host = host,
                                current_ip = bottle.request.remote_addr)



@route('/user/host/updateAddress', method = 'POST')
@authorized()
@validate('/user/hosts/list',
          host_id = formencode.validators.Int(),
          address = validation.IPAddress(),
          address_v6 = validation.IPv6Address(),
          description = validation.String(max = 255))
@require(db = 'dynserver.db:Database',
         messages = 'dynserver.interface.message:MessageManager')
def post_host_update_address(user,
                             data,
                             db,
                             messages):
  ''' Update the IP address and/or description of a hostname. '''

  with db.cursor() as cur:
    cur.execute('''
      UPDATE `hosts`
        SET  `address` = %(address)s,
             `address_v6` = %(address_v6)s,
             `description` = %(description)s,
             `updated` = CURRENT_TIMESTAMP
      WHERE  `id` = %(host_id)s
        AND  `user_id` = %(user_id)s
    ''', {'address': data.address,
          'address_v6': data.address_v6,
          'description': data.description,
          'host_id': data.host_id,
          'user_id': user.id})

  messages.success('Ok, done.')

  bottle.redirect('/user/hosts/list')



@route('/user/host/updatePassword', method = 'POST')
@authorized()
@validate('/user/hosts/list',
          host_id = formencode.validators.Int(),
          password = validation.SecurePassword(min = 8),
          password_confirm = validation.String(),
          chained_validators = [validation.FieldsMatch('password', 'password_confirm')])
@require(db = 'dynserver.db:Database',
         config = 'dynserver.config:Config',
         messages = 'dynserver.interface.message:MessageManager')
def post_host_update_password(user,
                              data,
                              db,
                              config,
                              messages):
  ''' Update the password of a hostname. '''

  encrypted_password = pwd.encrypt(data.password)

  with db.cursor() as cur:
    cur.execute('''
      UPDATE `hosts`
        SET  `password` = %(password)s
      WHERE  `id` = %(host_id)s
        AND  `user_id` = %(user_id)s
    ''', {'password': encrypted_password,
          'host_id': data.host_id,
          'user_id': user.id})

  messages.success('Ok, done.')

  bottle.redirect('/user/hosts/list')
