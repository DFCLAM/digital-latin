import os

# ALIM DB (copy)
mariadb_alim_php7_host = os.getenv('mariadb_alim_php7_host'.upper(), '127.0.0.1')
mariadb_alim_php7_port = os.getenv('mariadb_alim_php7_port'.upper(), '3307')
mariadb_alim_php7_db = os.getenv('mariadb_alim_php7_db'.upper(), 'alim_php7')
mariadb_alim_php7_user = os.getenv('mariadb_alim_php7_user'.upper(), 'root')
mariadb_alim_php7_psw = os.getenv('mariadb_alim_php7_psw'.upper(), None)

