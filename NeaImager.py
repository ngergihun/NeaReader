import gwyfile
import numpy as np
import copy
import math, cmath

class NeaImage:
    def __init__(self) -> None:
        # Name regarding file and neaSCAN project
        self.filename = None # Full path with name
        self.channel_name = None
        # Important measurement parameters from gwyddion file
        self.xreal = None
        self.yreal = None
        self.xoff = None
        self.yoff = None
        self.xres = None
        self.yres = None
        self.isamp  = None # Amplitude -True or phase/topography - false - VERY IMPORTANT
        # Data/Image itself
        self.data = None
        # Other parameters from info txt -  Dictionary
        self.parameters = None

    def read_from_gwyfile(self,filename: str, channelname: str):
        self.filename = filename
        self.channel_name = channelname
        gwyobj = gwyfile.load(self.filename)
        channels = gwyfile.util.get_datafields(gwyobj)
        channel = channels[self.channel_name]
        self.isAmplitude()

        # Set a basic attributes from gwyddion field
        for key in channel:
            if key in dir(self):
                setattr(self,key,channel[key])
        self.data = channel.data

    def isAmplitude(self):
        if 'A' in self.channel_name:
            self.isamp = True
        else:
            self.isamp = False

    def read_info_file(self,filename):
        # reader tested for neascan version 2.1.10719.0
        fid = open(filename,errors='replace')
        infodict = {}

        linestring = ''
        Nlines = 0

        while 'Version:' not in linestring:
            Nlines += 1
            linestring = fid.readline()
            if Nlines > 1:
                ct = linestring.split('\t')
                fieldname = ct[0][2:-1]
                fieldname = fieldname.replace(' ', '')

                if 'Scanner Center Position' in linestring:
                    fieldname = fieldname[:-5]
                    infodict[fieldname] = [float(ct[2]), float(ct[3])]

                elif 'Scan Area' in linestring:
                    fieldname = fieldname[:-7]
                    infodict[fieldname] = [float(ct[2]), float(ct[3]), float(ct[4])]

                elif 'Pixel Area' in linestring:
                    fieldname = fieldname[:-7]
                    infodict[fieldname] = [int(ct[2]), int(ct[3]), int(ct[4])]

                elif 'Interferometer Center/Distance' in linestring:
                    fieldname = fieldname.replace('/', '')
                    infodict[fieldname] = [float(ct[2]), float(ct[3])]

                elif 'Regulator' in linestring:
                    fieldname = fieldname[:-7]
                    infodict[fieldname] = [float(ct[2]), float(ct[3]), float(ct[4])]

                elif 'Q-Factor' in linestring:
                    fieldname = fieldname.replace('-', '')
                    infodict[fieldname] = float(ct[2])

                else:
                    fieldname = ct[0][2:-1]
                    fieldname = fieldname.replace(' ', '')
                    val = ct[2]
                    val = val.replace(',','')
                    try:
                        infodict[fieldname] = float(val)
                    except:
                        infodict[fieldname] = val.strip()
        fid.close()
        return infodict

######### Correction functions ######
# Line leveling
def LineLevel(inputobj: NeaImage, mtype: str):
    outputobj = copy.deepcopy(inputobj)
    match mtype:
        case 'median':
            for i in range(inputobj.data.shape[0]):
                if inputobj.isamp:
                    outputobj.data[i][:] = inputobj.data[i][:]/np.median(inputobj.data[i][:])
                else:
                    outputobj.data[i][:] = inputobj.data[i][:]-np.median(inputobj.data[i][:])
        case 'average':
            for i in range(inputobj.data.shape[0]):
                if inputobj.isamp:
                    outputobj.data[i][:] = inputobj.data[i][:]/np.mean(inputobj.data[i][:])
                else:
                    outputobj.data[i][:] = inputobj.data[i][:]-np.mean(inputobj.data[i][:])
        case 'difference':
            for i in range(inputobj.data.shape[0]-1):
                if inputobj.isamp:
                    c = np.median(inputobj.data[i+1][:]/inputobj.data[i][:])
                    outputobj.data[i][:] = inputobj.data[i][:]/c
                else:
                    c = np.median(inputobj.data[i+1][:]-inputobj.data[i][:])
                    outputobj.data[i][:] = inputobj.data[i][:]-c
    return outputobj

def BackgroundPolyFit(inputobj: NeaImage, xorder: int, yorder: int):
    outputobj = copy.deepcopy(inputobj)
    Z = copy.deepcopy(outputobj.data)
    x = list(range(0, outputobj.xres))
    y = list(range(0, outputobj.yres))
    X, Y = np.meshgrid(x,y)
    x, y = X.ravel(), Y.ravel()

    def get_basis(x, y, max_order_x=1, max_order_y=1):
        """Return the fit basis polynomials: 1, x, x^2, ..., xy, x^2y, ... etc."""
        basis = []
        for i in range(max_order_y+1):
            # for j in range(max_order_x - i +1):
            for j in range(max_order_x+1):
                basis.append(x**j * y**i)
        return basis

    basis = get_basis(x, y, xorder, yorder)
    A = np.vstack(basis).T
    b = Z.ravel()
    c, r, rank, s = np.linalg.lstsq(A, b, rcond=None)

    background = np.sum(c[:, None, None] * np.array(get_basis(X, Y, xorder, yorder)).reshape(len(basis), *X.shape), axis=0)

    if inputobj.isamp:
        outputobj.data = Z/background
    else:
        outputobj.data = Z-background

    return outputobj, background

def RotatePhase(inputobj: NeaImage, degree: float):
    outputobj = copy.deepcopy(inputobj)

    # Load amplitude image
    if inputobj.isAmplitude():
        pass
    else:
        ampIm = NeaImage()
        channelname = inputobj.channel_name
        new_channelname = channelname.replace('P','A')
        ampIm.read_from_gwyfile(inputobj.filename,new_channelname)
        ampIm.parameters = inputobj.parameters

        # Complex map
        C = ampIm.data * np.exp(inputobj.data*complex(1j))
        # Rotate and extract phase
        outputobj.data = np.angle(C*np.exp(np.deg2rad(degree)*complex(1j)))

    return outputobj

def SelfReferencing(inputobj: NeaImage, order: int):
    # Load amplitude image
    outputobj = NeaImage()
    if inputobj.isAmplitude():
        channelname = f'O{order}A raw'
    else:
        channelname = f'O{order}P raw'

    outputobj.read_from_gwyfile(inputobj.filename,channelname)
    outputobj.parameters = inputobj.parameters

    if inputobj.isAmplitude():
        outputobj.data = np.divide(inputobj.data,outputobj.data)
    else:
        outputobj.data = inputobj.data-outputobj.data

    return outputobj

def SimpleNormalize(inputobj: NeaImage, mtype: str, value = 1):
    outputobj = copy.deepcopy(inputobj)
    match mtype:
        case 'median':
            if inputobj.isAmplitude():
                outputobj.data = inputobj.data / np.median(inputobj.data)
            else:
                outputobj.data = inputobj.data - np.median(inputobj.data)
        case 'manual':
            if inputobj.isAmplitude():
                outputobj.data = inputobj.data / value
            else:
                outputobj.data = inputobj.data - value
    return outputobj