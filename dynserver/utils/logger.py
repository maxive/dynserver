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

import sys
import logging

from require import extend, export

from dynserver.config import parse_bool



@extend('dynserver.config:ConfigDeclaration')
def config_logging(config_decl):
  with config_decl.declare('logging') as s:
    s('verbose',
      conv = parse_bool,
      default = False)
    s('file',
      conv = str,
      default = '/var/log/dynserver.log')


@export(config = 'dynserver.config:Config')
def Logger(config):
  logging.root.addHandler(logging.FileHandler(filename = config.logging.file))

  if config.logging.verbose:
    logging.root.addHandler(logging.StreamHandler(stream = sys.stderr))
    logging.root.setLevel(logging.DEBUG)

  return logging.getLogger('dynserver')
