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
import requests

from require import extend, require

from dynserver.config import parse_bool



@extend('dynserver.config:ConfigDeclaration')
def config_captcha(config_decl):
  with config_decl.declare('captcha') as s:
    s('enabled',
      conv = parse_bool,
      default = False)
    s('recaptcha_public_key',
      conv = str,
      default = '')
    s('recaptcha_private_key',
      conv = str,
      default = '')



def captcha_check(__on_error__):
  ''' Checks if the captcha challenge and response in the request are matching.

      The challenge and response values are extracted from the POST data and
      passed to the recaptcha API.

      @param __on_error__: The target to redirect if the check failed
  '''

  def wrapper(func):
    @require(config = 'dynserver.config:Config',
             users = 'dynserver.interface.user:UserManager',
             messages = 'dynserver.interface.message:MessageManager')
    def wrapped(config,
                users,
                messages,
                *args,
                **kwargs):
      if config.captcha.enabled:
        response = bottle.request.POST.pop('g-recaptcha-response', None)

        if response is None:
          messages.error('Captcha values are missing')
          bottle.redirect('/')

        request = requests.get('https://www.google.com/recaptcha/api/siteverify',
                               params = {
                                   'secret': config.captcha.recaptcha_private_key,
                                   'response': response,
                                   'remoteip': bottle.request.remote_addr
                               })

        response = request.json()

        if not response['success']:
          messages.error('Captcha invalid')
          bottle.redirect(__on_error__)

      # Call the wrapped function
      return func(*args,
                  **kwargs)

    return wrapped
  return wrapper
