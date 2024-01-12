import matplotlib.pyplot as plt
import NeaSpectra as neas

# Load a test measurement
import os
current_folder = os.getcwd()
file_name = os.path.join(current_folder,'pte1.txt')

s = neas.NeaSpectrum()
s.readNeaSpectrum(file_name)

# Check the project and measurement name from parameters
print(s.parameters["Project"])
print(s.parameters["Description"])
# Check scan (measurement) type
print(s.parameters["Scan"])
plt.plot(s.data["Wavenumber"][0,0,:], s.data["PTE"][0,0,:])
plt.show()