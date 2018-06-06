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


import jinja2
import smtplib

from require import export, extend, require



@extend('dynserver.config:ConfigDeclaration')
def config_email(config_decl):
  with config_decl.declare('smtp') as s:
    s('host',
      conv = str,
      default = 'localhost')
    s('port',
      conv = int,
      default = 25)

  with config_decl.declare('contact') as s:
    s('name',
      conv = str,
      default = 'Your Administrator')
    s('email',
      conv = str)

  with config_decl.declare('wsgi') as s:
    s('protocol',
      conv = str,
      default = 'http://')

  with config_decl.declare('wsgi') as s:
    s('basename',
      conv = str,
      default = 'localhost:8080')



@export()
class EmailManager(object):
  def __init__(self):
    self.__environment = jinja2.Environment(loader = jinja2.PackageLoader('dynserver.resources',
                                                                          'email'))


  @require(config = 'dynserver.config:Config',
           messages = 'dynserver.interface.message:MessageManager',
           logger = 'dynserver.utils.logger:Logger')
  def __send(self,
             key,
             rcpt,
             config,
             messages,
             logger,
             **kwargs):
    ''' Sends an email.

        @param key: the name of the template used for the mail
        @param rcpt: the recipient mail address
        @param **kwargs: all remaining arguments are passed to the template
    '''

    # Load the template
    template = self.__environment.get_template(key)

    # Open SMTP connection
    try:
      smtp = smtplib.SMTP(host = config.smtp.host,
                          port = config.smtp.port,
                          timeout = 20)

    except:
      logger.error('Failed to contact the SMTP server at %s:%s (template %s)' %
                   config.smtp.host,
                   config.smtp.port,
                   key)
      raise

    else:
      try:
        # Send mail
        smtp.sendmail(config.contact.email,
                      [rcpt],
                      template.render(rcpt = rcpt,
                                      config = config,
                                      **kwargs))

      except:
        logger.error('Failed to send email to %s (template %s)' %
                     rcpt,
                     key)
        raise

      finally:
        # Close SMTP connection
        smtp.quit()


  def to_user(self,
              key,
              user,
              **kwargs):
    self.__send(key = key,
                rcpt = user.email,
                user = user,
                **kwargs)


  @require(config = 'dynserver.config:Config')
  def to_admin(self,
               key,
               config,
               **kwargs):
    self.__send(key = key,
                rcpt = config.contact.email,
                **kwargs)
