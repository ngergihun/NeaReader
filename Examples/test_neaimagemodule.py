import gwyfile
import matplotlib.pyplot as plt
import NeaImager as neaim

# Load a Gwyddion file into memory
import os
current_folder = os.getcwd()
file_name = os.path.join(current_folder,'testPsHetImage.gwy')
info_fname = os.path.join(current_folder,'testinfofile.txt')
channelname = 'O3P raw'
meas = neaim.NeaImage()
meas.read_from_gwyfile(file_name,channelname)
meas.parameters = meas.read_info_file(info_fname)

print(vars(meas))
print(meas.parameters["Project"])