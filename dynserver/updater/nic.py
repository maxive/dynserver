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

import functools
import bottle

import formencode

from passlib.apps import custom_app_context as pwd

from require import require

from dynserver.web import route


# See http://www.noip.com/integrate for further protocol specification


class Response(object):
  """ The response send to the client. """
  __slots__ = ['name',
               'value']


  def __init__(self, name, value):
    self.name = name
    self.value = value


  def __str__(self):
    if self.value:
      return '%s %s' % (self.name, self.value)

    else:
      return '%s' % self.name

  __repr__ = __str__


# Existing response codes
resp_good = functools.partial(Response, 'good')
resp_nochg = functools.partial(Response, 'nochg')
resp_nohost = functools.partial(Response, 'nohost', None)
resp_badauth = functools.partial(Response, 'badauth', None)
resp_badagent = functools.partial(Response, 'badagent', None)
resp_not_donator = functools.partial(Response, '!donator', None)
resp_abuse = functools.partial(Response, 'abuse', None)
resp_911 = functools.partial(Response, '911', None)



@require(logger='dynserver.utils.logger:Logger',
         db='dynserver.db:Database')
def update(logger, db, username, password, hostnames, address):
  """ Update the records.

      The very first step is to check username and password. If they are not
      provided or the username does not exist, a bad credentials answer is
      returned.

      If the credentials are checked, for each given hostname, the address is
      stored in the database.
  """

  # Check if we get some credentials
  if not username or not password:
    logger.warning('updater: Update attempt with missing credentials')
    return resp_badauth()

  # Try to get user ID from database
  with db.cursor() as cur:
    cur.execute('''
      SELECT `id`, `password`
        FROM `users`
       WHERE `username` = %(username)s
         AND `active` = 1
    ''', {'username': username})
    user = cur.fetchone()

  # Check if we have a valid user
  if not user:
    logger.warning('updater: Update attempt with invalid username %s',
                   username)
    return resp_badauth()

  logger.debug('updater: Found user in DB: %s', user)

  # Validate the IP address
  try:
    validator = formencode.validators.IPAddress()
    validator.to_python(address)

  except formencode.Invalid:
    logger.warning('updater: Update attempt using an invalid IP address: %s',
                   address)
    return resp_abuse()

  # The specification allows to give multiple hosts separated by comma
  responses = []
  for hostname in hostnames:
    logger.debug('updater: Fetching existing host entry for %s', hostname)

    # Get the host entry for the current hostname from the database
    with db.cursor() as cur:
      cur.execute('''
        SELECT
          `host`.`id`,
          `host`.`address`,
          `host`.`password`
        FROM `hosts` AS `host`
        LEFT JOIN `suffixes` AS `suffix`
           ON ( `suffix`.`id` = `host`.`suffix_id` )
        WHERE `host`.`user_id` = %(user_id)s
          AND CONCAT(`host`.`hostname`, '.', `suffix`.`name`) = %(hostname)s
      ''', {'user_id': user['id'],
            'hostname': hostname})
      host = cur.fetchone()

    # Check if we got a host entry for the queried hostname
    if not host:
      logger.warning('updater: Update attempt for non-existing hostname %s',
                     hostname)

      responses.append(resp_nohost())
      continue

    # Check the users credentials (passwords are assigned to hosts)
    if not pwd.verify(password, host['password']):
      logger.warning('updater: Mismatching credentials for host %s',
                     hostname)

      responses.append(resp_badauth())
      continue

    # Check if the address has changed
    if host['address'] == address:
      logger.debug('updater: Address has not changed: %s',
                   address)

      responses.append(resp_nochg(value=address))
      continue

    # validate the ip address
    try:
      validator = formencode.validators.IPAddress()
      validator.to_python(address)

    except formencode.Invalid:
      logger.debug('Invalid IP address in update request: %s', address)

      responses.append(resp_abuse())
      continue

    # Update the host entry
    with db.cursor() as cur:
      cur.execute('''
          UPDATE `hosts`
          SET `address` = %(address)s,
              `updated` = CURRENT_TIMESTAMP
          WHERE `id` = %(id)s
      ''', {'id': host['id'],
            'address': address})

    logger.info('updater: Host entry updated: %s = %s', hostname, address)

    responses.append(resp_good(value=address))

  return responses


@route('/nic/ip', method='GET')
def get_ip():
  """ Return the IP address of the client extracted from
      the HTTP header.
  """

  return bottle.request.remote_addr


@route('/nic/update', method='GET')
@require(logger='dynserver.utils.logger:Logger')
def get_update(logger):
  """ Handles an update request from a dyncliente implementation.
  """

  # Extract the hostnames separated by comma, the new IP address
  # and the offline flag from the query
  hostnames = bottle.request.query.get('hostname', None)
  if hostnames:
    hostnames = hostnames.split(',')
    address = bottle.request.query.get('myip', None)
    offline = bottle.request.query.get('offline', 'NO') == 'YES'

    # If no IP was provided in the request, use the one from the request
    if not address:
        address = bottle.request.remote_addr

    # Fetch the the credentials from HTTP header
    if bottle.request.auth:
      username, password = bottle.request.auth

    else:
      username = bottle.request.query.get('username', None)
      password = bottle.request.query.get('password', None)

    # Clear the address if the offline flag is set
    if offline:
      address = None

    logger.info('updater: Update request for %s as %s', hostnames, address)

    # Call the update function
    try:
      responses = update(username=username,
                         password=password,
                         hostnames=hostnames,
                         address=address)

    except:
      responses = resp_911()

    # Blow up responses if we got a single response
    if isinstance(responses, Response):
      responses = [responses] * len(hostnames)

  # if no hostnames were provided, this is invalid usage of
  # the update protocol.
  else:
    responses = resp_abuse()
    responses = [responses]

  logger.debug('updater: Update responses: %s', responses)

  # Return responses as string
  return '\n'.join(str(response)
                   for response
                   in responses)
