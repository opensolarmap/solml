# To run 100 jobs for 12 hours :
#   parallel --jobs 100 --arg-sep ,, python download_worker.py 12 100 ,, {0..99}
# To kill every jobs :
#   kill $(ps aux | grep download_worker.py | awk '{print $2}')
# In /etc/crontab :
# 00 21   * * *   michel  /usr/bin/zsh -c "/usr/bin/parallel --jobs 90 --arg-sep ,, /home/michel/.virtualenvs/solar/bin/python /home/michel/solar/solml/solml/compute/download_worker.py 6 90 ,, {0..89} >> /home/michel/log_cron 2>&1"

import sys
import os.path
import time
import configparser

import psycopg2
import postgis

from solml.compute import compute_angle


# Read config

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.ini'))
database_host = config['main']['database_host']
database_port = config['main']['database_port']
database_name = config['main']['database_name']
database_username = config['main']['database_username']
database_password = config['main']['database_password']
assert database_host == 'localhost'
assert database_port == '1234'


nb_hours = int(sys.argv[1])
nb_worker = int(sys.argv[2])
id_worker = int(sys.argv[3])

duration_in_seconds = nb_hours #* 3600
start_time = time.time()
end_time = start_time + duration_in_seconds


# Open connection
connection = psycopg2.connect(dbname=database_name, user=database_username, password=database_password)
cursor = connection.cursor()
postgis.register(cursor)

cursor.execute('set enable_seqscan = off;')

while(time.time() < end_time):
    compute_angle.process_building(connection, cursor, nb_worker, id_worker)


cursor.close()
connection.close()