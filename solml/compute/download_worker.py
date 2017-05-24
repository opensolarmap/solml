import sys
import os.path

from solml.compute import compute_angle


nb_worker = int(sys.argv[1])
id_worker = int(sys.argv[2])

while(True):
    compute_angle.process_building(nb_worker, id_worker)
