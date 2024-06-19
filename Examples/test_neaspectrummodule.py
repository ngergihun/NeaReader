import matplotlib.pyplot as plt
import os, sys
sys.path.append(os.getcwd())
import NeaSpectra as neas
import numpy as np

# Choose a measurement file
current_folder = os.getcwd()
file_name = os.path.join(current_folder,'Examples\\testspectrum.txt')

# Create NeaSpectrom object and load data
s = neas.NeaSpectrum()
s.readNeaSpectrum(file_name)

# List all key of params dictionary
print(list(s.parameters.keys()))
# List all keys of data dictionary
print(list(s.data.keys()))
# Check the project and measurement name from parameters
print(s.parameters["Project"])
print(s.parameters["Description"])
# Check scan (measurement) type
print(s.parameters["Scan"])
# Check data size and plot some spectrum
print(np.shape(s.data["O2A"]))
plt.plot(s.data["Wavenumber"][:], s.data["O2A"][:])
plt.show()

# To save a specific data channel: (this will save the wavenumber and the choosen channel to a dat file columnwise)
s.SaveSpectraToDAT("O2A")