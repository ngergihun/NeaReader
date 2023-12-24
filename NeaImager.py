import gwyfile

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

    def read_from_gwyfile(self):
        gwyobj = gwyfile.load(self.filename)
        channels = gwyfile.util.get_datafields(gwyobj)
        channel = channels[self.channel_name]

        # Set a basic attributes from gwyddion field
        for key in channel:
            if key in dir(self):
                setattr(self,key,channel[key])

    ######## OTHER FUNCTIONS ################
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
    