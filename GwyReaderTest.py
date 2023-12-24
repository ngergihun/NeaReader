import gwyfile
import matplotlib.pyplot as plt

# Load a Gwyddion file into memory
obj = gwyfile.load('2022-04-09 123828 PH PLT-EV-niceplace_spectrum_1665_cm-1.gwy')
# Return a dictionary with the datafield titles as keys and the
# datafield objects as values.
channels = gwyfile.util.get_datafields(obj)
channel = channels['O3A raw']
# Datafield objects have a `data` property to access their
# two-dimensional data as numpy arrays.
print(list(channel.keys()))
print(type(channel))

# Plot the data using matplotlib.
fig, ax = plt.subplots()
ax.imshow(channel.data, interpolation='none', origin='upper', extent=(0, channel.xreal, 0, channel.yreal))
plt.show()
