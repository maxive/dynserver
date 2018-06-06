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

from require import require

from dynserver.web import route

from dynserver.interface.user import authorized_admin

from dynserver.interface import validation
from dynserver.interface.validation import validate



@route('/admin/suffixes/list', method = 'GET')
@authorized_admin()
@require(db = 'dynserver.db:Database',
         templates = 'dynserver.interface.template:TemplateManager')
def get_suffix_list(user,
                    db,
                    templates):
  ''' Display a list of available suffixes (zones) '''

  with db.cursor() as cur:
    cur.execute('''
      SELECT `suffixes`.*, COUNT(`hosts`.`id`) AS count
        FROM `suffixes`
      LEFT JOIN `hosts`
        ON `suffixes`.`id` = `hosts`.`suffix_id`
      GROUP BY `suffixes`.`id`
    ''')
    suffixes = cur.fetchall()

  return templates['suffixes.html'](suffixes = suffixes)



@route('/admin/suffixes/add', method = 'GET')
@authorized_admin()
@require(db = 'dynserver.db:Database',
         config = 'dynserver.config:Config',
         templates = 'dynserver.interface.template:TemplateManager')
def get_suffix_add(user,
                   db,
                   config,
                   templates):
  '''  Display a form for adding new suffixes (zones) '''

  return templates['addsuffix.html']()



@route('/admin/suffixes/add', method = 'POST')
@authorized_admin()
@validate('/admin/suffixes/add',
          suffix_name = validation.ValidSuffix(min = 1, max = 255))
@require(db = 'dynserver.db:Database',
         messages = 'dynserver.interface.message:MessageManager')
def post_suffix_add(user,
                    data,
                    db,
                    messages):
  ''' Add a new suffix. '''

  with db.cursor() as cur:
    cur.execute('''
      SELECT *
      FROM `suffixes`
      WHERE `name` = %(name)s
    ''', {'name': data.suffix_name})

    if cur.rowcount > 0:
      messages.error('Suffix with same name already exists')
      bottle.redirect('/admin/suffixes/add')

    cur.execute('''
      INSERT
      INTO `suffixes`
      SET `name` = %(name)s
    ''', {'name': data.suffix_name})

  messages.success('Ok, done.')

  bottle.redirect('/admin/suffixes/list')



@route('/admin/suffixes/delete', method = 'POST')
@authorized_admin()
@validate('/admin/suffixes/list',
          suffix_id = validation.Int(not_empty = True))
@require(db = 'dynserver.db:Database',
         messages = 'dynserver.interface.message:MessageManager')
def post_suffix_delete(user,
                       data,
                       db,
                       messages):
  ''' Delete a suffix. '''

  with db.cursor() as cur:
    cur.execute('''
      DELETE
      FROM `suffixes`
      WHERE id = %(suffix_id)s
    ''', {'suffix_id': data.suffix_id})

  messages.success('Ok, done.')

  bottle.redirect('/admin/suffixes/list')


@route('/admin/suffix/<suffix_id>', method = 'GET')
@authorized_admin()
@require(db = 'dynserver.db:Database',
         templates = 'dynserver.interface.template:TemplateManager')
def get_suffix_hostnames(user,
                         db,
                         templates,
                         suffix_id):
  ''' Display a list of hostnames for a given suffixes. '''

  with db.cursor() as cur:
    cur.execute('''
      SELECT `suffixes`.`name` AS suffixname
        FROM `suffixes`
      WHERE `suffixes`.`id` = %(suffix_id)s
    ''', {'suffix_id': suffix_id})
    suffixname = cur.fetchone()

    cur.execute('''
      SELECT `users`.`username` AS username,
             `hosts`.*
        FROM `suffixes`
      RIGHT JOIN `hosts`
        ON `suffixes`.`id` = `hosts`.`suffix_id`
      RIGHT JOIN `users`
        ON `hosts`.`user_id` = `users`.`id`
      WHERE `suffixes`.`id` = %(suffix_id)s
    ''', {'suffix_id': suffix_id})
    hostlist = cur.fetchall()

  return templates['suffix_hosts.html'](suffix = suffixname,
                                        hostlist = hostlist)




@route('/admin/suffix/deleteHost', method = 'POST')
@authorized_admin()
@validate('/admin/suffixes/list',
          host_id = validation.Int(not_empty = True))
@require(db = 'dynserver.db:Database',
         messages = 'dynserver.interface.message:MessageManager')
def post_hosts_delete(user,
                      data,
                      db,
                      messages):
  ''' Delete a hostname administratively. '''

  with db.cursor() as cur:
    cur.execute('''
        DELETE
        FROM hosts
        WHERE id = %(host_id)s
    ''', {'host_id': data.host_id})

  messages.success('Ok, done.')

  bottle.redirect('/admin/suffixes/list')
