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
with mariadb.connect(**connection_properties) as conn:
    with conn.cursor() as cur:
        cur.execute("select title, author, n7tra_html_content from agora_book")
        for (title, author, xml) in cur:
            print (title, author)
        pass
