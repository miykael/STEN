import tables
import numpy as np


class WriteDatatable:

    """
    Write the dataset content to H5 file
    """

    def __init__(self, name, dataset):

        # Get Dataset Size
        nRows = dataset['Table']['nRows']
        nCols = dataset['Table']['nCols']
        nFact = len(dataset['Factors'][0])
        nBetw = len(dataset['BetweenFactor']) \
            if dataset['BetweenFactor'] != [] else 1
        nCova = len(dataset['Covariate']) \
            if dataset['Covariate'] != [] else 1
        nWith = len(dataset['WithinFactor'])

        # Create PyTables Description Object
        class Information(tables.IsDescription):

            subjectLabel = tables.StringCol(16)
            subjectList = tables.UInt16Col(shape=(nRows))

            factorsName = tables.StringCol(16, shape=(nFact))
            factorsLevel = tables.UInt16Col(shape=(nFact))

            withinLabel = tables.StringCol(16, shape=(nWith))
            withinFactor = tables.StringCol(16, shape=(nWith))
            withinPaths = tables.StringCol(256, shape=(nWith, nRows))

            betweenLabel = tables.StringCol(16, shape=(nBetw))
            betweenList = tables.UInt16Col(shape=(nBetw, nRows))

            covariateLabel = tables.StringCol(16, shape=(nCova))
            covariateList = tables.Float64Col(shape=(nCova, nRows))

            tableNRows = tables.UInt16Col()
            tableNCols = tables.UInt16Col()
            tableLabels = tables.StringCol(16, shape=(nCols))
            tableContent = tables.StringCol(256, shape=(nCols, nRows))

        # Create H5 File to store dataset information
        with tables.open_file(name, mode='w', title='Test file') as h5file:
            table = h5file.create_table('/', 'Datatable', Information,
                                        'Dataset Information')

            # Write dataset content into H5 file
            table.row['subjectLabel'] = dataset['Subject'][0]
            table.row['subjectList'] = dataset['Subject'][1]

            table.row['factorsName'] = dataset['Factors'][0]
            table.row['factorsLevel'] = dataset['Factors'][1]

            table.row['withinLabel'] = [dataset['WithinFactor'][i][0]
                                        for i in range(nWith)]
            table.row['withinFactor'] = [dataset['WithinFactor'][i][1]
                                         for i in range(nWith)]
            table.row['withinPaths'] = [dataset['WithinFactor'][i][2]
                                        for i in range(nWith)]
            betweenFactor = dataset['BetweenFactor']
            table.row['betweenLabel'] = [e[0] for e in betweenFactor] \
                if betweenFactor != [] else ''
            table.row['betweenList'] = [e[1] for e in betweenFactor] \
                if betweenFactor != [] else 0
            covariateFactor = dataset['Covariate']
            table.row['covariateLabel'] = [e[0] for e in covariateFactor] \
                if covariateFactor != [] else ''
            table.row['covariateList'] = [e[1] for e in covariateFactor] \
                if covariateFactor != [] else 0
            table.row['tableContent'] = dataset['Table']['content']
            table.row['tableNRows'] = dataset['Table']['nRows']
            table.row['tableNCols'] = dataset['Table']['nCols']
            table.row['tableLabels'] = dataset['Table']['labels']

            # Save and close H5 file
            table.row.append()
            table.flush()


class ReadDatatable:

    """
    Read the dataset from an H5 file
    """

    def __init__(self, name):

        # Load the dataset information
        with tables.openFile(name, 'r') as h5file:
            datatable = dict(zip(h5file.root.Datatable.colnames,
                                 h5file.root.Datatable.read()[0]))

            # Reformat the data content
            dataset = {}
            dataset['Subject'] = [unicode(datatable['subjectLabel']),
                                  datatable['subjectList'].tolist()]
            dataset['Factors'] = [
                [unicode(e) for e in datatable['factorsName']],
                datatable['factorsLevel'].tolist()]
            dataset['WithinFactor'] = zip(
                [unicode(e) for e in datatable['withinLabel']],
                [unicode(e) for e in datatable['withinFactor']],
                [[unicode(e) for e in l.tolist()]
                 for l in datatable['withinPaths']])
            dataset['Covariate'] = zip(
                [unicode(e) for e in datatable['covariateLabel']],
                datatable['covariateList'].tolist()) \
                if datatable['covariateLabel'][0] != '' else []
            dataset['BetweenFactor'] = zip(
                [unicode(e) for e in datatable['betweenLabel']],
                datatable['betweenList'].tolist()) \
                if datatable['betweenLabel'][0] != '' else []
            dataset['Table'] = {}
            dataset['Table']['nRows'] = datatable['tableNRows']
            dataset['Table']['nCols'] = datatable['tableNCols']
            dataset['Table']['labels'] = [unicode(e)
                                          for e in datatable['tableLabels']]
            dataset['Table']['content'] = [[unicode(e) for e in l.tolist()]
                                           for l in datatable['tableContent']]

            self.inputTable = dataset


class ReadEPH:

    """
    Read an EPH file
    """

    def __init__(self, filename):

        with open(filename, 'r') as ephfile:
            tmp = ephfile.readlines()
            header = tmp[0].split()
            self.electrodes = int(header[0])
            self.tf = int(header[1])
            self.fs = float(header[2])
        self.data = np.loadtxt(filename, skiprows=1)
        self.GFP = self.data.std(axis=1)
