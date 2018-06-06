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

import itertools
import collections



class FieldDeclaration(object):
  ''' Declaration of a message field. '''

  def __init__(self, name, conv):
    ''' Declares a field.

        @param name: the name of the field - this name is used as property name
                     of parsed messages
        @param conv: the type converter function used to parse the field - the
                     function must accept a string and return a value
    '''

    self.__name = name
    self.__conv = conv


  @property
  def name(self):
    ''' Returns the name of the field. '''
    return self.__name


  def lex(self, value):
    ''' Lex the field. '''

    return self.__conv(value)


  def format(self, value):
    ''' Format the field. '''

    return str(value)



class MessageDeclaration(object):
  ''' Declaration of a message type. '''


  def __init__(self, tag, *fields):
    ''' Declares a message.

        @param tag: the tag used to identify the message type
        @param fields: the fields declared for the message
    '''

    self.__tag = tag
    self.__fields = fields

    self.__type = collections.namedtuple(self.__tag, ['tag'] + [field.name
                                                                for field
                                                                in self.__fields])


  @property
  def tag(self):
    ''' Returns the tag. '''

    return self.__tag


  def lex(self, load):
    ''' Lex the message. '''

    return self(**{field.name : field.lex(value)
                   for field, value
                   in zip(self.__fields,
                          load)})


  def format(self, message):
    ''' Format the message. '''

    # Format the values in the message skipping the first value as it is the tag
    return [field.format(value)
            for field, value
            in zip(self.__fields,
                   message[1:])]


  def __call__(self, *args, **kwargs):
    return self.__type(tag = self.__tag, *args, **kwargs)



class LexerDeclaration(object):
  ''' Declaration of a lexer. '''

  def __init__(self, messages, splitter = ' '):
    ''' Declares a protocol.

        @param splitter: the character used to separate field in messages
        @param messages: the messages declared for this protocol
    '''

    self.__splitter = splitter
    self.__messages = {message.tag : message
                       for message
                       in messages}


  def __call__(self, line):
    ''' Lex the line. '''

    # Strip of surrounding white spaces and tailing new line and split the
    # message into parts separated by the splitting character
    message = line.strip().split(self.__splitter)

    # Split message in tag and values
    tag, values = message[0], message[1:]

    # Find message declaration for tag and lex the values using this message
    # declaration or return None if the tag is unknown
    if tag in self.__messages:
      return self.__messages[tag].lex(values)

    else:
      return None


  def __getattr__(self, key):
    ''' Returns a message declaration for the given key. '''

    return self.__messages[key]



class FormatterDeclaration(object):
  def __init__(self, messages, splitter = ' '):
    self.__splitter = splitter
    self.__messages = {message.tag : message
                       for message
                       in messages}


  def __call__(self, message):
    # Find the message declaration for tag and format the values using this
    # message declaration
    load = self.__messages[message.tag].format(message)

    # Join the message parts separated by the splitter character
    return self.__splitter.join([message.tag] + load)



  def __getattr__(self, key):
    ''' Returns a message declaration for the given key. '''

    return self.__messages[key]


