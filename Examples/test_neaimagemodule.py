import os, sys
# parent_dir = os.path.dirname(os.getcwd())
sys.path.append(os.getcwd())
import NeaImager as neaim

# Load a Gwyddion file into memory
current_folder = os.getcwd()
file_name = os.path.join(current_folder,'Examples\\testPsHetImage.gwy')
info_fname = os.path.join(current_folder,'Examples\\testinfofile.txt')
channelname = 'O3P raw'
meas = neaim.NeaImage()
meas.read_from_gwyfile(file_name,channelname)
meas.parameters = meas.read_info_file(info_fname)

print(vars(meas))
print(meas.parameters["Project"])