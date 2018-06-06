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

import sys

from require import require, extend

from dynserver.utils.txtprot import (LexerDeclaration,
                                    FormatterDeclaration,
                                    MessageDeclaration,
                                    FieldDeclaration)


# See http://doc.powerdns.com/html/backends-detail.html#pipebackend
# for further protocol specification


# Declaration of the PowerDNS pipe protocol
lexer = LexerDeclaration(splitter='\t',
                         messages=(MessageDeclaration('HELO',
                                                      FieldDeclaration('version', int)),

                                   MessageDeclaration('Q',
                                                      FieldDeclaration('qname', str),
                                                      FieldDeclaration('qclass', str),
                                                      FieldDeclaration('qtype', str),
                                                      FieldDeclaration('id', int),
                                                      FieldDeclaration('remote', str)),

                                   MessageDeclaration('AXFR',
                                                      FieldDeclaration('id', int)),

                                   MessageDeclaration('PING')))


formatter = FormatterDeclaration(splitter='\t',
                                 messages=(MessageDeclaration('OK',
                                                              FieldDeclaration('banner', str)),

                                           MessageDeclaration('DATA',
                                                              FieldDeclaration('qname', str),
                                                              FieldDeclaration('qclass', str),
                                                              FieldDeclaration('qtype', str),
                                                              FieldDeclaration('ttl', str),
                                                              FieldDeclaration('id', int),
                                                              FieldDeclaration('content', str)),

                                           MessageDeclaration('LOG',
                                                              FieldDeclaration('message', str)),

                                           MessageDeclaration('END'),
                                           MessageDeclaration('FAIL')))


@extend('dynserver.config:ConfigDeclaration')
def config_dns(config_decl):
  with config_decl.declare('dns') as s:
    s('ttl',
      conv=int,
      default=60)


@require(logger='dynserver.utils.logger:Logger')
def receiver(logger):
  """ Receive and process messages from PowerDNS
  """

  while True:
    # Read a line
    line = sys.stdin.readline()
    if not line:
      break

    # Lex the line
    message = lexer(line)

    # Check if we got a message
    if message is None:
      logger.error('recursor: Unknown tag: %s', line)
      continue

    logger.debug('recursor: Received message: %s', message)

    # Forward the message
    yield message


@require(logger='dynserver.utils.logger:Logger')
def send(cls,
         logger,
         **kwargs):
  """ Send responses to PowerDNS
  """

  # Create message
  message = cls(**kwargs)

  logger.debug('recursor: Responding message: %s', message)

  # Format the response
  line = formatter(message)

  # Send line to standard output
  sys.stdout.write(line + '\n')
  sys.stdout.flush()


@require(db='dynserver.db:Database')
def answer_soa(query,
               db):
  """ Handle SOA records and respond with defined suffixes
  """

  with db.cursor() as cur:
    cur.execute('''
      SELECT *
      FROM `suffixes`
      WHERE `name` = %(name)s
    ''', {'name': query.qname})
    suffix = cur.fetchone()

    if suffix:
      send(formatter.DATA, qname=query.qname,
                           qclass=query.qclass,
                           qtype='SOA',
                           ttl=3600,
                           id=query.id,
                           content=' '.join(('ns.' + query.qname,
                                             'webmaster.' + query.qname,
                                             '0',
                                             '86400',     # 24h
                                             '7200',      # 2h
                                             '3600000',   # 1000h
                                             '172800')))  # 2d


@require(db='dynserver.db:Database',
         config='dynserver.config:Config')
def answer_a(query,
             db,
             config):
  """ Handle A records
  """

  with db.cursor() as cur:
    cur.execute('''
        SELECT
          `host`.`hostname` AS `hostname`,
          `suffix`.`name` AS `suffix`,
          `host`.`address` AS `address`
        FROM `hosts` AS `host`
        LEFT JOIN `suffixes` AS `suffix`
          ON ( `suffix`.`id` = `host`.`suffix_id` )
        WHERE `host`.`address` IS NOT NULL
          AND CONCAT(`host`.`hostname`, '.', `suffix`.`name`) = %(name)s
    ''', {'name': query.qname})
    host = cur.fetchone()

    if host:
      send(formatter.DATA, qname=query.qname,
                           qclass=query.qclass,
                           qtype='A',
                           ttl=config.dns.ttl,
                           id=query.id,
                           content=host['address'])


@require(db='dynserver.db:Database',
         config='dynserver.config:Config')
def answer_aaaa(query,
                db,
                config):
  """ Handle AAAA records
  """

  with db.cursor() as cur:
    cur.execute('''
        SELECT
          `host`.`hostname` AS `hostname`,
          `suffix`.`name` AS `suffix`,
          `host`.`address_v6` AS `address_v6`
        FROM `hosts` AS `host`
        LEFT JOIN `suffixes` AS `suffix`
          ON ( `suffix`.`id` = `host`.`suffix_id` )
        WHERE `host`.`address_v6` IS NOT NULL
          AND CONCAT(`host`.`hostname`, '.', `suffix`.`name`) = %(name)s
    ''', {'name': query.qname})
    host = cur.fetchone()

    if host:
      send(formatter.DATA, qname=query.qname,
                           qclass=query.qclass,
                           qtype='AAAA',
                           ttl=config.dns.ttl,
                           id=query.id,
                           content=host['address_v6'])


def answer(query):
  """ Determine query type and respond to it
  """

  if query.qtype == 'SOA' or query.qtype == 'ANY':
    answer_soa(query)

  if query.qtype == 'A' or query.qtype == 'ANY':
    answer_a(query)

  if query.qtype == 'AAAA' or query.qtype == 'ANY':
    answer_aaaa(query)

  else:
    # Ignore all other queries
    pass



@require(logger='dynserver.utils.logger:Logger')
def main(logger):
  messages = receiver()

  # Handle messages until HELO was received
  for message in messages:
    # Handle HELO message
    if message.tag == 'HELO':
      # Expecting ABI version 1
      if message.version != 1:
        logger.error('recursor: Unappropriate ABI version: %s', message.version)
        send(formatter.FAIL)

      send(formatter.OK,
           banner='dynserver')
      break

    else:
      logger.error('recursor: Missing HELO before command: %s', message.tag)
      send(formatter.FAIL)

  # Handle all messages after HELO
  for message in messages:
    if message.tag == 'HELO':
      logger.error('recursor: Duplicated HELO')
      send(formatter.FAIL)

    elif message.tag == 'Q':
      # Handle query
      answer(query=message)

      send(formatter.END)

    elif message.tag == 'AXFR':
      # We do not support transfer by now
      send(formatter.END)

    elif message.tag == 'PING':
      # Ping does not require any data response
      send(formatter.END)

    else:
      logger.error('recursor: Unhandled message tag: %s', message)
      send(formatter.FAIL)


if __name__ == '__main__':
  main()
