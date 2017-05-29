# To run 100 jobs for 12 hours :
#   parallel --jobs 100 --arg-sep ,, python download_worker.py 12 100 ,, {0..99}
# To kill every jobs :
#   kill $(ps aux | grep download_worker.py | awk '{print $2}')
# In /etc/crontab :
# 00 21   * * *   michel  /usr/bin/zsh -c "/usr/bin/parallel --jobs 90 --arg-sep ,, /home/michel/.virtualenvs/solar/bin/python /home/michel/solar/solml/solml/compute/download_worker.py 6 90 ,, {0..89} >> /home/michel/log_cron 2>&1"

import sys
import os.path
import time

from solml.compute import compute_angle

nb_hours = int(sys.argv[1])
nb_worker = int(sys.argv[2])
id_worker = int(sys.argv[3])

duration_in_seconds = nb_hours * 3#600
start_time = time.time()
end_time = start_time + duration_in_seconds

while(time.time() < end_time):
    compute_angle.process_building(nb_worker, id_worker)
