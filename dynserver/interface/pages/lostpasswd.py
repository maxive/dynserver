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

from dynserver.interface.captcha import captcha_check

from passlib.apps import custom_app_context as pwd



@route('/lostpass', method = 'GET')
@require(config = 'dynserver.config:Config',
         templates = 'dynserver.interface.template:TemplateManager')
def get_lostpass(config,
                 templates):
  return templates['lostpass.html']()



@route('/lostpass', method = 'POST')
@captcha_check('/lostpass')
@validate(username = validation.ExistendUsername())
@require(users = 'dynserver.interface.user:UserManager',
         emails = 'dynserver.mail:EmailManager',
         messages = 'dynserver.interface.message:MessageManager')
def post_lostpass(data,
                  users,
                  emails,
                  messages):
  # Generate a authcode for the user
  users.generate_authcode(data.username)

  # Fetch user info
  user = users[data.username]

  emails.to_user('lostpasswd.mail',
                 user = user)

  messages.success('Password recovery email has been sent.')

  bottle.redirect('/')



@route('/lostpass/recover', method = 'GET')
@require(templates = 'dynserver.interface.template:TemplateManager')
def get_lostpass_setnew(templates):
  username = bottle.request.query.username
  authcode = bottle.request.query.authcode

  return templates['resetpass.html'](username = username,
                                     authcode = authcode)



@route('/lostpass/setnew', method = 'POST')
@authorized_by_code()
@validate(password = validation.SecurePassword(min = 8),
          password_confirm = validation.String(),
          chained_validators = [validation.FieldsMatch('password', 'password_confirm')])
@require(db = 'dynserver.db:Database',
         messages = 'dynserver.interface.message:MessageManager')
def post_lostpass_setnew(user,
                         data,
                         db,
                         messages):
  encrypted_password = pwd.encrypt(data.password)

  with db.cursor() as cur:
    cur.execute('''
        UPDATE `users`
        SET `password` = %(encrypted_password)s,
            `authcode` = NULL
        WHERE `id` = %(user_id)s
    ''', {'encrypted_password': encrypted_password,
          'user_id': user.id})

  messages.success('Your new password has been set.')

  bottle.redirect('/')



@route('/lostpass/cancel', method = 'POST')
@authorized_by_code()
@require(db = 'dynserver.db:Database',
         messages = 'dynserver.interface.message:MessageManager')
def post_lostpass_cancel(user,
                         db,
                         messages):
  with db.cursor() as cur:
    cur.execute('''
        UPDATE `users`
        SET `authcode` = NULL
        WHERE `id` = %(user_id)s
    ''', {'user_id': user.id})

  messages.success('Your password reset request has been cancelled.')

  bottle.redirect('/')
