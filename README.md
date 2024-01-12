# General description
This repository is just a collection of useful Python code for SNOM data processing. Not all the implemented procedures are finished and tested.

# NeaSpectrum class
The NeaSpectra.py implements a base class for nano-FTIR, TERS, PTE, and PsHetPoint Spectroscopy data collected by NeaSNOM/NeaSCOPE instruments. `readNeaSpectrum` method of the NeaSpectrum class read the measurement parameter and the measurement data channels for the measurement `.txt` file.

## Usage
`test_neaspectrummodule.py` provides an example of creating a NeaSpectrum object and the measurement load data:
```python
import NeaSpectra as neas
s = neas.NeaSpectrum()
s.readNeaSpectrum(file_name)
```
The `parameters` attribute of the NeaSpectrum object is a dictionary containing the measurement parameters. For example:
```python
print(s.parameters["Project"])
print(s.parameters["Description"])
```
The `data` attribute is also a dictionary containing the measurement channels as key-value pairs. For example:
```python
s.data["Wavenumber"][0,0,:]
s.data["PTE"][0,0,:]
s.data["O3P"][0,0,:]
```
In case of hyperspectral measurement (linescan or areascan) the data channels are 3D numpy arrays, while in case of single spectra it is a simple numpy array with only one index.
