import gwyfile
import matplotlib.pyplot as plt
import NeaImager as neaim

# Load a Gwyddion file into memory
fname = r'C:\Users\ngerg\OneDrive\Python\NeaReader\testPsHetImage.gwy'
info_fname = 'testinfofile.txt'
channelname = 'O3P raw'
meas = neaim.NeaImage()
meas.read_from_gwyfile(fname,channelname)
meas.parameters = meas.read_info_file(info_fname)

print(vars(meas))
print(meas.parameters["Project"])