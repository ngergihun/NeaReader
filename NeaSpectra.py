import numpy as np
import os

class NeaSpectrum:
    def __init__(self) -> None:
        self.filename = None # Full path with name
        # data from all the channels
        self.data = None
        # Other parameters from info txt -  Dictionary
        self.parameters = None

    def readNeaSpectrum(self,filename):
        # reader tested for neascan version 2.1.10719.0
        self.filename = filename
        fid = open(filename,errors='replace')
        data = {}
        params = {}

        linestring = fid.readline()
        Nlines = 1

        while 'Row' not in linestring:
            Nlines += 1
            linestring = fid.readline()
            if Nlines > 1:
                ct = linestring.split('\t')
                fieldname = ct[0][2:-1]
                fieldname = fieldname.replace(' ', '')

                if 'Scanner Center Position' in linestring:
                    fieldname = fieldname[:-5]
                    params[fieldname] = [float(ct[2]), float(ct[3])]

                elif 'Scan Area' in linestring:
                    fieldname = fieldname[:-7]
                    params[fieldname] = [float(ct[2]), float(ct[3]), float(ct[4])]

                elif 'Pixel Area' in linestring:
                    fieldname = fieldname[:-7]
                    params[fieldname] = [int(ct[2]), int(ct[3]), int(ct[4])]

                elif 'Interferometer Center/Distance' in linestring:
                    fieldname = fieldname.replace('/', '')
                    params[fieldname] = [float(ct[2]), float(ct[3])]

                elif 'Regulator' in linestring:
                    fieldname = fieldname[:-7]
                    params[fieldname] = [float(ct[2]), float(ct[3]), float(ct[4])]

                elif 'Q-Factor' in linestring:
                    fieldname = fieldname.replace('-', '')
                    params[fieldname] = float(ct[2])

                else:
                    fieldname = ct[0][2:-1]
                    fieldname = fieldname.replace(' ', '')
                    val = ct[2]
                    val = val.replace(',','')
                    try:
                        params[fieldname] = float(val)
                    except:
                        params[fieldname] = val.strip()

        channels = linestring.split('\t')
        self.parameters = params
        fid.close()

        if "PTE+" in params['Scan']:
            C_data = np.genfromtxt(filename, skip_header=Nlines, encoding='utf-8')
        else:
            C_data = np.genfromtxt(filename, skip_header=Nlines)

        for i in range(len(channels)-2):
            if params['PixelArea'][1] and params['PixelArea'][0] == 1:
                if "PTE+" in params['Scan']:
                    data[channels[i]] = np.reshape(C_data[:,i], (params['PixelArea'][2]))
                else:
                    data[channels[i]] = np.reshape(C_data[:,i], (params['PixelArea'][2]*2))
            else:
                if "PTE+" in params['Scan']:
                    data[channels[i]] = np.reshape(C_data[:,i], (params['PixelArea'][0], params['PixelArea'][1], params['PixelArea'][2]))
                else:
                    data[channels[i]] = np.reshape(C_data[:,i], (params['PixelArea'][0], params['PixelArea'][1], params['PixelArea'][2]*2))
        self.data = data

    def SaveSpectraToDAT(self,channelname):
        fname = f'{self.filename[0:-4]}.dat'
        M = np.array([self.data["Wavenumber"],self.data[channelname]])
        np.savetxt(fname, M.T)