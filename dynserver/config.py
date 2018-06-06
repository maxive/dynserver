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

import configparser as configparser

import collections
import contextlib

from require import export



def parse_bool(value):
    """ Helper function to parse boolean config values.
    """
    return value.lower() in ['y', 'yes', 't', 'true', 1, 'on']



@export()
class ConfigDeclaration(object):
  ''' Declaration of the configuration.

      The declaration consists of sections where each section can contain
      arbitrary options.

      An option must have a converter which is a function used to convert the
      raw string value from the configuration file to a value. Additionally, a
      default value can be specified, which makes the option optional.
  '''

  REQUIRED = object()
  ''' Special value for the default field of a option making it required. '''


  Option = collections.namedtuple('Option', ['conv',
                                             'default'])
  ''' Declaration of an option. '''


  def __init__(self):
    self.__sections = {}


  @contextlib.contextmanager
  def declare(self, section_name):
    ''' Declare a section.

        The section declaration is a context manager where the context is a
        function, which can be used to declare a option. Example:

        with config_decl.declare('my_section') as my:
          my('my_option',
             conv = str,
             default = 'my_default')
          ...
    '''

    # Create a section declaration if it does not exists
    if section_name not in self.__sections:
      section = self.__sections[section_name] = {}

    else:
      section = self.__sections[section_name]

    # The option declaration function returned as the context
    def declarator(option_name,
                   conv = str,
                   default = self.REQUIRED):
      # Check if the section already contains the option
      if option_name in section:
        raise KeyError('Duplicated option declaration %s:%s' % (section_name, option_name))

      # Add the option to the section
      self.__sections[section_name][option_name] = self.Option(conv = conv,
                                                               default = default)

    # Return the function as context
    yield declarator


  @property
  def declarations(self):
    ''' Returns the declarations. '''
    return self.__sections




class Namespace(object):
  def __getitem__(self, key):
    return self.__dict__[key]


  def __setitem__(self, key, value):
    self.__dict__[key] = value


  def __contains__(self, key):
    return key in self.__dict__


  __getattr__ = __getitem__
  __setattr__ = __setitem__




@export(config_decl = 'dynserver.config:ConfigDeclaration')
def Config(config_decl):
  ''' Parses a configuration file.

      The configuration declaration is used to parse the configuration file.
  '''

  # Create a namespace object containing the parsed configuration
  ns = Namespace()

  # Opens and loads the configuration file
  config_file = configparser.SafeConfigParser()
  config_file.read('/etc/dynserver/dynserver.conf')

  # Parse all sections
  for section_name, options in config_decl.declarations.items():
    # Ensure a namespace object for the section exists
    if section_name in ns:
      nss = ns[section_name]

    else:
      nss = ns[section_name] = Namespace()

    # Parse the options in the section
    for option_name, option in options.items():
      if config_file.has_option(section_name, option_name):
        # Load the raw value from the config file
        raw_value = config_file.get(section_name, option_name)

        # Parse the value
        value = option.conv(raw_value)

      elif option.default != config_decl.REQUIRED:
        # Use the default value as value
        value = option.default

      else:
        # Value is required - throwing an exception
        raise KeyError('Missing option %s:%s' % (section_name, option_name))

      # Set the value to the section namespace
      nss[option_name] = value

  return ns
