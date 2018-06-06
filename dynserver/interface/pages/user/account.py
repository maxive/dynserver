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
from dynserver.interface.user import authorized_by_code

from dynserver.interface import validation
from dynserver.interface.validation import validate

from passlib.apps import custom_app_context as pwd



@extend('dynserver.config:ConfigDeclaration')
def config_auth(config_decl):
  with config_decl.declare('auth') as s:
    s('password_min_chars',
       conv = int,
       default = 8)



@route('/user/account', method = 'GET')
@authorized()
@require(template = 'dynserver.interface.template:TemplateManager')
def get_account(user,
                template):
  ''' Display account information. '''

  return template['account.html'](data = user)



@route('/user/account', method = 'POST')
@authorized()
@validate('/user/account',
          email = validation.Email())
@require(db = 'dynserver.db:Database',
         messages = 'dynserver.interface.message:MessageManager')
def post_account_edit(user,
                      data,
                      db,
                      messages):
  ''' Display account information. '''

  with db.cursor() as cur:
    cur.execute('''
        UPDATE `users`
        SET `email` = %(email)s
        WHERE `id` = %(id)s
    ''', {'email': data.email,
          'id': user.id})

  messages.success('Ok, done.')

  bottle.redirect('/user/account')



@route('/user/account/password', method = 'POST')
@authorized()
@validate('/user/account',
          password = validation.SecurePassword(min = 8),
          password_confirm = validation.String(),
          chained_validators = [validation.FieldsMatch('password', 'password_confirm')])
@require(db = 'dynserver.db:Database',
         messages = 'dynserver.interface.message:MessageManager')
def post_account_password(user,
                          data,
                          db,
                          messages):
  ''' Update the users password. '''

  encrypted_password = pwd.encrypt(data.password)

  with db.cursor() as cur:
    cur.execute('''
        UPDATE `users`
        SET `password` = %(newpass)s
        WHERE `id` = %(id)s
    ''', {'newpass' : encrypted_password,
          'id': user.id})

  messages.success('Ok, done.')

  bottle.redirect('/user/account')



@route('/user/account/delete', method = 'POST')
@authorized()
@require(db = 'dynserver.db:Database',
         auth = 'dynserver.interface.user:UserManager',
         messages = 'dynserver.interface.message:MessageManager')
def post_account_delete(user,
                        db,
                        auth,
                        messages):
  ''' Delete the users account. '''

  with db.cursor() as cur:
    cur.execute('''
        DELETE
        FROM users
        WHERE id = %(id)s
    ''', {'id': user.id})

  auth.logout()

  bottle.redirect('/')

