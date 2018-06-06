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

from require import export, extend, require

import functools
import jinja2



@export()
class TemplateManager(object):
  def __init__(self):
    self.__environment = jinja2.Environment(loader = jinja2.PackageLoader('dynserver.resources',
                                                                          'templates'),
                                            autoescape = True)

    self.__globals = {}


  def __getitem__(self, key):
    ''' Returns a template render function for the requested template.

        @param key: the name of the template
    '''

    # Generate the globals and get the template from the environment
    template = self.__environment.get_template(key)

    c = self.__globals['config']()

    # Return the render function of the template
    return functools.partial(template.render, **{name : func()
                                                 for name, func
                                                 in self.__globals.items()})


  @property
  def globals(self):
    ''' The registered globals to inject in each template.

        All values of this dict must be functions returning the global.
    '''

    return self.__globals



@extend('dynserver.interface.template:TemplateManager')
def template_config(templates):
  @require(config = 'dynserver.config:Config')
  def __(config):
    return config

  templates.globals['config'] = __
