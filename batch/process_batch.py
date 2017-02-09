import pickle
import sys
import os.path

import get_info
import download
import load
import cnn

i_batch = int(sys.argv[1])
print('Processsing batch {}...'.format(i_batch))

# Is there any work to do ?
cnn_cache_dir = '/home/michel/solar/cnn_cache/chunks/'
filename_cnn = cnn_cache_dir + 'chunk_{}.pkl'.format(i_batch)
if os.path.isfile(filename_cnn):
    print('...chunk {} already done.'.format(i_batch))
    sys.exit()


# Get building info
root_dir = '/home/michel/solar/buildings/chunks/'
filename_info = root_dir + 'building_chunk_{:04d}'.format(i_batch)
buildings = get_info.process_building_info(filename_info)
ident_list = get_info.get_available_ident(buildings)

# Compute CNN features
cnn_features = cnn.compute_cnn_features(buildings, ident_list)

# Save CNN features
f = open(filename_cnn, 'wb')
for i, ident in enumerate(ident_list):
    cnn_feature = cnn_features[i, :]
    pickle.dump((ident, cnn_feature), f)
f.close()

print('...finished batch {}.'.format(i_batch))
