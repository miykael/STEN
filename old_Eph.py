import numpy as np


# TODO - translate to english:
# lire les Eph, puis faire les claluls dessus (GFP, ST, ..:)

class Eph:

    """ TODO: translate to english
    lecture: path eph/eph name"""

    def __init__(self, PathEph):
        """ TODO: translate to english
        on initialise l'objet eph
        soit on lis des EPH 2 parametres
        1) PathEph = lieu de l'eph
        2) NameEph = nom de l'eph
        """
        header = open(PathEph).readline()
        header = header.split('\t')
        if len(header) == 1:
            header = open(PathEph).readline()
            header = header.split(' ')
        self.electrodes = int(header[0])
        self.tf = int(header[1])
        try:
            self.fs = int(header[2])
        except:
            self.fs = float(header[2])
        self.data = np.loadtxt(PathEph, skiprows=1)
