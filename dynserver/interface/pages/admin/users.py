'''´
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

from require import require

from dynserver.web import route

from dynserver.interface.user import authorized_admin

from dynserver.interface import validation
from dynserver.interface.validation import validate



@route('/admin/users/<mode>')
@authorized_admin()
@require(db = 'dynserver.db:Database',
         templates = 'dynserver.interface.template:TemplateManager')
def get_users(user,
              db,
              templates,
              mode = 'all'):
  """ Display a list of users. Depending on the mode, show all users,
      only show admins, or only show accounts that are awaiting activation.
  """

  if mode == 'admins':
      where = 'WHERE `admin` = 1'

  elif mode == 'inactive':
      where = 'WHERE `active` = NULL'

  else:
      where = 'WHERE 1 = 1'

  with db.cursor() as cur:
    cur.execute('''
        SELECT *
        FROM `users`
    ''' + where)
    users = cur.fetchall()

  return templates['users.html'](users = users,
                                 user = user,
                                 mode = mode)


@route('/admin/user/<userid>/hosts')
@authorized_admin()
@require(db = 'dynserver.db:Database',
         templates = 'dynserver.interface.template:TemplateManager')
def get_user_hosts(user,
                   userid,
                   db,
                   templates):
  """ Display a list of a users hostnames.
  """

  with db.cursor() as cur:
    cur.execute('''
        SELECT `hosts`.*,
               `suffixes`.`name` AS suffix,
               `users`.`username` AS username
        FROM `hosts`
        RIGHT JOIN `suffixes`
          ON `suffixes`.`id` = `hosts`.`suffix_id`
        RIGHT JOIN `users`
          ON `hosts`.`user_id` = `users`.`id`
        WHERE `user_id` = %(userid)s
    ''', {'userid': int(userid)})
    hosts = cur.fetchall()

  return templates['userhosts.html'](hosts = hosts,
                                     user = user)


@route('/admin/users/add', method = 'GET')
@authorized_admin()
@require(templates = 'dynserver.interface.template:TemplateManager')
def get_user_add(user,
                 templates):
  ''' Adds a new user. '''
  return templates['adduser.html']()



@route('/admin/users/add', method = 'POST')
@authorized_admin()
@validate('/admin/users/add',
          username = validation.UniqueUsername(max = 255),
          email = validation.Email())
@require(db = 'dynserver.db:Database',
         users = 'dynserver.interface.user:UserManager',
         emails = 'dynserver.mail:EmailManager',
         messages = 'dynserver.interface.message:MessageManager')
def post_user_add(user,
                  data,
                  db,
                  users,
                  emails,
                  messages):
  ''' Manually add a new user. '''

  with db.cursor() as cur:
    cur.execute('''
      INSERT
      INTO users
      SET `username` = %(username)s,
          `email` = %(email)s,
          `admin` = 0,
          `active` = 0,
          `created` = CURRENT_TIMESTAMP
    ''', {'username': data.username,
          'email': data.email})

   # Generate auth code
  users.generate_authcode(data.username)

  # Get user record
  user = users[data.username]

  # Send out activation mail
  try:
    emails.to_user('signup_activate.mail',
                   user = user)

  except:
    # Failed to send activation email.
    # We reset the authcode in this case, so an admin can send
    # a new one after fixing email issues
    with db.cursor() as cur:
      cur.execute('''
          UPDATE users
          SET `authcode` = %(authcode)s
          WHERE `username` = %(username)s
      ''', {'authcode': None,
            'username': data.username})

    messages.error('Failed to send activation email.')

  else:
    messages.success('Account created. The user will get an activation email.')

  bottle.redirect('/admin/users/all')



@route('/admin/users/activate', method = 'POST')
@authorized_admin()
@validate('/admin/users/all',
          username = validation.ValidUsername(min = 1, max = 255))
@require(db = 'dynserver.db:Database',
         users = 'dynserver.interface.user:UserManager',
         config = 'dynserver.config:Config',
         emails = 'dynserver.mail:EmailManager',
         messages = 'dynserver.interface.message:MessageManager')
def post_users_activate(user,
                        data,
                        db,
                        users,
                        config,
                        emails,
                        messages):
  ''' Activate a users account. '''

  users.generate_authcode(data.username)
  user = users[data.username]

  try:
    emails.to_user('signup_activate.mail',
                   user = user)

  except:
    # Failed to send activation email.
    # We reset the authcode in this case, so an admin can send
    # a new one after fixing email issues
    with db.cursor() as cur:
      cur.execute('''
          UPDATE users
          SET `authcode` = %(authcode)s
          WHERE `username` = %(username)s
      ''', {'authcode': None,
            'username': data.username})

    messages.error('Failed to send the activation email.')

  else:
    messages.success('Ok, done.')

  bottle.redirect('/admin/users/all')



@route('/admin/users/delete', method = 'POST')
@authorized_admin()
@validate('/admin/users/all',
          user_id = validation.Int(not_empty = True))
@require(db = 'dynserver.db:Database',
         messages = 'dynserver.interface.message:MessageManager')
def post_users_delete(user,
                      data,
                      db,
                      messages):
  ''' Delete a users account. '''

  with db.cursor() as cur:
    cur.execute('''
        DELETE
        FROM `users`
        WHERE `id` = %(user_id)s
    ''', { 'user_id': data.user_id})

  messages.success('Ok, done.')

  bottle.redirect('/admin/users/all')



@route('/admin/users/mkadmin', method = 'POST')
@authorized_admin()
@validate('/admin/users/all',
          user_id = validation.Int(not_empty = True))
@require(db = 'dynserver.db:Database',
         messages = 'dynserver.interface.message:MessageManager')
def post_user_mkadmin(user,
                      data,
                      db,
                      messages):
  ''' Makes a users an administrator. '''

  with db.cursor() as cur:
    cur.execute('''
        UPDATE `users`
        SET `admin` = 1
        WHERE `id` = %(user_id)s
    ''', { 'user_id': data.user_id})

  messages.success('Ok, done.')

  bottle.redirect('/admin/users/all')



@route('/admin/users/rmadmin', method = 'POST')
@authorized_admin()
@validate('/admin/users/all',
          user_id = validation.Int(not_empty = True))
@require(db = 'dynserver.db:Database',
         messages = 'dynserver.interface.message:MessageManager')
def post_user_rmadmin(user,
                      data,
                      db,
                      messages):
  ''' Makes a users account a unprivileged user. '''

  with db.cursor() as cur:
    cur.execute('''
        UPDATE `users`
        SET `admin` = NULL
        WHERE `id` = %(user_id)s
    ''', { 'user_id': data.user_id})

  messages.success('Ok, done.')

  bottle.redirect('/admin/users/admin')



@route('/admin/users/updateMaxhosts', method = 'POST')
@authorized_admin()
@validate('/admin/users/all',
          max_hosts = validation.Int(not_empty = True,
                                     min = -2),
          user_id = validation.Int(not_empty = True))
@require(db = 'dynserver.db:Database',
         messages = 'dynserver.interface.message:MessageManager')
def post_user_updatemaxhosts(user,
                             data,
                             db,
                             messages):
  ''' Update the maximum allowed hostnames of a user . '''

  if data.max_hosts == -2:
    data.max_hosts = None

  with db.cursor() as cur:
    cur.execute('''
        UPDATE `users`
        SET `maxhosts` = %(max_hosts)s
        WHERE `id` = %(user_id)s
    ''', {'max_hosts': data.max_hosts,
          'user_id': data.user_id})

  messages.success('Ok, done.')

  bottle.redirect('/admin/users/all')

