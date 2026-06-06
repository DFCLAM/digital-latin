from env import *
import mariadb, sys

connection_properties = {
        'user' : mariadb_alim_php7_user,
        'password' : mariadb_alim_php7_psw,
        'host' : mariadb_alim_php7_host,
        'port' : int(mariadb_alim_php7_port),
        'database' : mariadb_alim_php7_db
}
print (connection_properties)

query = '''
  -- The query use windows functions to get the last version of each book with not empty XML
  WITH agora_book_version_last AS (
    SELECT DISTINCT id, MAX(version) OVER (PARTITION BY id) AS max_version FROM agora_book_version WHERE length(n7tra_xml_content) > 0
  )
  SELECT
    b1.id
  , b1.title
  , b1.author
  , b1.is_document
  , b1.consistenza
  , b1.metadata
  , b1.n7tra_xml_content 
  FROM agora_book_version b1
  JOIN agora_book_version_last b2 ON b2.id = b1.id AND b2.max_version = b1.version
  WHERE NOT b1.alim_plus
  -- WHERE b1.id = 13147
  -- LIMIT 200
  '''

with mariadb.connect(**connection_properties) as conn:
    with conn.cursor() as cur:
        cur.execute(query)
        for row in cur:
            print (row[0], row[1], len(row[6]))
