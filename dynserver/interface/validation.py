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

import re
import bottle
import string

import formencode

from formencode.validators import (FancyValidator,
                                   FieldsMatch,  # @UnusedImport: for exporting
                                   Email,  # @UnusedImport: for exporting
                                   IPAddress,  # @UnusedImport: for exporting
                                   String,  # @UnusedImport: for exporting
                                   Int)  # @UnusedImport: for exporting

from require import require, extend



def validate(__on_error__ = '/',
             **kwargs):
  ''' Input validation wrapper that builds a validation schema.

      The given **kwargs are used to create a validation schema. Each post field
      is mapped against the key of the schema and validated using the keys
      validator.

      The special parameter '__on_error__' is used as a redirect target if the
      validation fails.

      If the validation was successful, the POST parameters are transformed into
      arguments with the same name and passed to the wrapped function.

      @param __on_error__: the redirect target used if tha valiadtion fails
      @param **kwargs: a mapping of names and validators
  '''

  # Build schema class
  Schema = type('Schema',
                (formencode.Schema,),
                kwargs)

  # Value container
  class Values(object):
    def __init__(self, values):
      self.__dict__.update(values)

  def wrapper(func):
    @require(messages = 'dynserver.interface.message:MessageManager')
    def wrapped(messages, *args, **kwargs):
      validator = Schema()

      try:
        # Validate the POST values using the schema
        data = validator().to_python({k : bottle.request.POST.get(k)
                                      for k
                                      in bottle.request.POST})

        func(*args,
             data = Values(data),
             **kwargs)

      except formencode.Invalid as e:
        for msg in e.error_dict.values():
          messages.error(msg)

      bottle.redirect(__on_error__)

    return wrapped
  return wrapper



@extend('dynserver.config:ConfigDeclaration')
def config_reserved(config_decl):
  with config_decl.declare('dns') as s:
    s('reserved',
      conv = lambda values: set(filter(None, (value.strip() for value in values.splitlines()))),
      default = set())



class ValidHostname(FancyValidator):
  ''' Check for valid hostname. '''

  messages = {
    'too_short': 'Hostname can not be empty',
    'too_long': 'Hostname can not exceed 63 characters',
    'non_letter': 'Hostname can only consist of a-z, 0-9 or the minus (-) character',
    'invalid_start': 'Hostnames must start with an aplhanumeric character',
    'not_allowed': 'Sorry, this hostname is reserved by the administrator.'
  }

  letter_regex = re.compile(r'^[a-z0-9\-]+$')

  @require(config = 'dynserver.config:Config')
  def validate_python(self,
                      value,
                      state,
                      config):
    if value in config.dns.reserved:
      raise formencode.Invalid(self.message('not_allowed', state),
                               value,
                               state)

    if len(value) < 1:
      raise formencode.Invalid(self.message("too_short",
                                            value),
                               value,
                               state)

    if len(value) > 63:
      raise formencode.Invalid(self.message("too_long",
                                            value),
                               value,
                               state)

    if not self.letter_regex.match(value):
      raise formencode.Invalid(self.message('non_letter',
                                            value),
                               value,
                               state)

    if value[0] == '-':
      raise formencode.Invalid(self.message('invalid_start',
                                            value),
                               value,
                               state)



class UniqueHostname(FancyValidator):
  ''' Check whether the hostname entered is unique
      in the given zone (suffix). '''

  messages = {
    'not_uniq': 'Sorry, this hostname already exists.'
  }

  hostname = suffix = None

  __unpackargs__ = ('hostname', 'suffix')

  @require(db = 'dynserver.db:Database')
  def validate_python(self,
                      field_dict,
                      state,
                      db):
    with db.cursor() as cur:
      cur.execute('''
          SELECT 1
          FROM `hosts` AS `host`
          LEFT JOIN `suffixes` AS `suffix`
            ON ( `suffix`.`id` = `host`.`suffix_id` )
          WHERE `host`.`hostname` = %(hostname)s
            AND `host`.`suffix_id` = %(suffix_id)s
      ''', {'hostname': field_dict[self.hostname],
            'suffix_id': field_dict[self.suffix]})
      result = cur.fetchone()

    if result != None:
      msg = self.message('not_uniq', state)
      raise formencode.Invalid(msg,
                               field_dict,
                               state,
                               error_dict = {field_dict[self.hostname]: msg})



class ValidUsername(FancyValidator):
  ''' Check whether a valid username was entered. '''

  messages = {
    'too_short': 'Username can not be empty',
    'too_long': 'Username can not exceed 255 characters.',
    'non_letter': 'Username can only consist of a-z, 0-9, -, .',
  }

  letter_regex = re.compile(r'^[A-Za-z0-9\-\.]+$')

  def validate_python(self, value, state):
    if len(value) < 1:
      raise formencode.Invalid(self.message('too_short',
                                            value),
                               value,
                               state)

    if len(value) > 255:
      raise formencode.Invalid(self.message('too_long',
                                            value),
                               value,
                               state)

    if not self.letter_regex.match(value):
      raise formencode.Invalid(self.message('non_letter',
                                            value),
                               value,
                               state)



class UniqueUsername(ValidUsername):
  ''' Check whether the username entered is unique. '''

  messages = {
    'not_uniq': 'This username already exists.'
  }

  @require(users = 'dynserver.interface.user:UserManager')
  def validate_python(self,
                      value,
                      state,
                      users):
    ValidUsername.validate_python(self, value, state)

    user = users[value]

    if user:
      raise formencode.Invalid(self.message('not_uniq',
                                            value),
                               value,
                               state)


class ExistendUsername(ValidUsername):
  messages = {
    'not_existend': 'This username does not exist.'
  }


  @require(users = 'dynserver.interface.user:UserManager')
  def validate_python(self,
                      value,
                      state,
                      users):
    ValidUsername.validate_python(self, value, state)

    user = users[value]

    if not user:
      raise formencode.Invalid(self.message('not_existend',
                                            value),
                               value,
                               state)



class SecurePassword(FancyValidator):
  ''' Check whether the password entered is a good password. '''

  messages = {
    'too_short': 'Password must be at least %(min_chars)s characters long'
  }

  @require(config = 'dynserver.config:Config')
  def validate_python(self,
                      value,
                      state,
                      config):
    min_chars = config.auth.password_min_chars
    if len(value) < min_chars:
      raise formencode.Invalid(self.message('too_short',
                                            value,
                                            min_chars = min_chars),
                               value,
                               state)



class ValidSuffix(FancyValidator):
  ''' Check for valid suffix. '''

  # TODO: validate hostname, tld, at least one dot, ...

  messages = {
    'too_short': 'The name of the zone can not be empty',
    'too_long': 'The name of the zone can not exceed 255 characters',
    'non_letter': 'The name of the zone can only consist of a-z, 0-9, -, .'
  }

  letter_regex = re.compile(r'[a-z0-9\-\.]+')

  def validate_python(self,
                      value,
                      state):
    if len(value) < 1:
      raise formencode.Invalid(self.message("too_short",
                                            value),
                               value,
                               state)

    if len(value) > self.max:
      raise formencode.Invalid(self.message("too_long",
                                            value),
                               value,
                               state)

    if not self.letter_regex.match(value):
      raise formencode.Invalid(self.message('non_letter',
                                            value),
                               value,
                               state)



class UniqueSuffix(ValidSuffix):
  ''' Check whether the zone name entered is unique. '''

  messages = {
    'not_uniq': 'This zone already exists.'
  }

  @require(db = 'dynserver.db:Database')
  def validate_python(self,
                      value,
                      state,
                      db):
    ValidSuffix.validate_python(self, value, state)

    with db.cursor() as cur:
      cur.execute('''
          SELECT name
          FROM suffixes
          WHERE name = %(suffixname)s
      ''', {'suffixname': value})
      result = cur.fetchone()

    if result != None:
      raise formencode.Invalid(self.message('not_uniq',
                                            value),
                               value,
                               state)

class IPv6Address(FancyValidator):
  """ Check whether the IPv6 address entered is valid.
      Note: IPv4-Embedded IPv6 addresses are not supported at the moment
  """

  messages = {
    'badFormat': 'Please enter a valid IPv6 address',
    'doubleColon': "IPv6 address can only have a single '::'",
    'IPv4Embedded': "Sorry, IPv4-Embedded IPv6 addresses are not supported at the moment",
    'illegalSegment': "IPv6 segments must be hexadecimal values within range of 0-FFFF, (not %(segment)r)"
  }

  def validate_python(self,
                      value,
                      state):
    try:
        parts = value.split(':')

        # An IPv6 address needs at least 2 colons (3 parts).
        if len(parts) < 3:
            raise ValueError

        # If the address has an IPv4-style suffix, is it valid.
        # This is not supported at the moment, as I do not want to write a test
        if '.' in parts[-1]:
          raise formencode.Invalid(self.message('IPv4Embedded', state), value, state)

        # can't have leading or trailing singular colons
        if (not parts[0] and parts[1]) or (not parts[-1] and parts[-2]):
            raise ValueError

        # Disregarding the endpoints, find if '::' with nothing in between.
        # This indicates that a run of zeros has been skipped.
        skip_index = None
        for i in range(1, len(parts) - 1):
            if not parts[i]:
                if skip_index is not None:
                    # Can't have more than one '::'
                    raise formencode.Invalid(self.message('doubleColon', state), value, state)
                skip_index = i

        if skip_index is not None:
            if len(parts) > 8 and parts[skip_index - 1] and parts[skip_index + 1]:
                raise ValueError
        else:
            if len(parts) != 8:
                raise ValueError

        # Validate each hex value
        hex_digits = frozenset(string.hexdigits)
        for hex_val in parts:
            if hex_val.startswith('0') and hex_val != '0':
                if not self.leading_zeros:
                    raise formencode.Invalid(
                        self.message('leadingZeros', state), value, state)

            hex_val = hex_val.lstrip('0')

            if not hex_digits.issuperset(hex_val) or len(hex_val) > 4:
                raise formencode.Invalid(
                    self.message('illegalSegment', state, segment=hex_val), value, state)

    except ValueError:
        raise formencode.Invalid(self.message('badFormat', state), value, state)