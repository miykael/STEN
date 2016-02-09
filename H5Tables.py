import tables
import numpy as np


class WriteDatatable:

    """
    Write the datatable content to H5 file
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
    Read the datatable from an H5 file
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
            self.TF = int(header[1])
            self.FS = float(header[2])
        self.data = np.loadtxt(filename, skiprows=1)
        self.GFP = self.data.std(axis=1)


class ReadDataset:

    """
    Read complet dataset from H5 file, including content of EPH files

    # /Data/All
    #       using createEArray('/','AllData',tables.Float32Atom(),
    #       (TF,electrodes,0))
    # /Data/GFP
    #       using createEArray('/','AllData',tables.Float32Atom(),(TF,1,0))
    # /Model
    #       using a tables with col= {Name of the factor, Value of factor
    #       (Vector), type of Factor (Within,between, covariate, subject)
    # /Info
    #       using a tables that contain all the information in the "ExcelSheet"
    # /Result/All/Anova
    #       Tables with col ={Name of the effect (i.e main effect,
    #       interaction, ..), P Data(Without any threshold (alpha, consecpoits,
    #       ...),F Data}
    # /Result/All/IntermediateResult
    #       Tabes with Col = {Condition name, Type (Mean, pearson correaltion,
    #       Standard error,...),Data Corresponding in Type}
    # /Result/All/PostHoc
    #       Tabes with Col = {Name,P,T}
    # /Result/GFP/Anova
    #       Tables with col ={Name of the effect (i.e main effect,
    #       interaction, ..),P Data(Without any threshold (alpha, consecpoits,
    #       ...),F Data}
    # /Result/GFP/IntermediateResult
    #       Tabes with Col = {Condition name, Type (Mean,pearson correaltion,
    #       Standard error,...)}
    # /Result/GFP/PostHoc
    #       Tabes with Col = {Name,P,T}
    """

    def __init__(self, name, dataset):

        # TODO: check and rewrite this section

        # Simulation of reading grid
        subjectName = dataset['Subject'][0]
        subjectID = dataset['Subject'][1]
        # TODO: make sure that multiple variables are considered
        groupName = dataset['BetweenFactor'][0][0]
        groupID = dataset['BetweenFactor'][0][1]
        # TODO: make sure that multiple variables are considered
        covariateName = dataset['Covariate'][0][0]
        covariateID = dataset['Covariate'][0][1]

        # Geneating a Dict containing the grid info with artifical col name
        # coming from grid
        InfoDict = {subjectName: subjectID,
                    groupName: groupID,
                    covariateName: covariateID}

        for i, e in enumerate(dataset['WithinFactor']):
            fName = e[0].replace('.', '_').replace(' ', '')
            InfoDict[fName] = e[2]

        NbLine = len(subjectID)

        AllEph = np.ravel([e[2] for e in dataset['WithinFactor']])

        SubjectFactor = np.ravel([subjectID] * NbLine)
        Covariate = np.ravel([covariateID] * NbLine)
        Between = np.ravel([groupID] * NbLine)
        # TODO: not sure if this is the right way
        Within = np.ravel([[int(e[1][1:-1])] * NbLine
                           for i, e in enumerate(dataset['WithinFactor'])])

        # factor Name coming from selecting factor
        SubjectName = {subjectName: SubjectFactor}
        BetweeName = {groupName: Between}
        CovariateName = {covariateName: Covariate}
        WithinName = {'Cond': Within}
        AllFactor = {subjectName: SubjectName, 'Between': BetweeName,
                     'Covariate': CovariateName, 'Within': WithinName}

        # Creation H5 File and differnt group
        H5 = tables.openFile(name, 'r+')
        ResultGrp = H5.createGroup('/', 'Result')
        AllRes = H5.createGroup(ResultGrp, 'All')
        GFPRes = H5.createGroup(ResultGrp, 'GFP')

        # Read EPH files
        ephData = [ReadEPH(eph) for eph in AllEph]
        electrodes = np.stack(
            [eph.electrodes for eph in ephData]).astype('uint16')
        FS = np.stack([eph.FS for eph in ephData]).astype('uint16')
        TF = np.stack([eph.TF for eph in ephData]).astype('uint16')

        # make sure that all eph files have the same dimension and frequency
        # TODO: Have warning message to aborts the whole thing instead of print
        if len(np.unique(electrodes)) == 1:
            electrodes = electrodes[0]
        else:
            print 'Number of electrodes is unequal in EPH files.'
        if len(np.unique(FS)) == 1:
            FS = FS[0]
        else:
            print 'Sampling rate is unequal in EPH files.'
        if len(np.unique(TF)) == 1:
            TF = TF[0]
        else:
            print 'Number of sampling points is unequal in EPH files.'

        DataGroup = H5.createGroup('/', 'Data')
        AllData = H5.createEArray(
            DataGroup, 'All', tables.Float32Atom(), (TF * electrodes, 0))
        GFPData = H5.createEArray(
            DataGroup, 'GFP', tables.Float32Atom(), (TF, 0))

        # Reading EphFile dans store into Tables with EArray
        for e in ephData:
            AllData.append(e.data.reshape(np.array(e.data.shape).prod(), 1))
            GFPData.append(e.GFP.reshape(TF, 1))

        ShapeOriginalData = H5.createArray(
            '/', 'Shape', np.array(e.data.shape))

        ModelParticle = {'Name': tables.StringCol(40),
                         'Value': tables.Float32Col(shape=len(SubjectFactor)),
                         'Type': tables.StringCol(40)}

        InfoParticle = {}
        for c in InfoDict:
            InfoParticle[c] = tables.StringCol(256)

        AnovaAllParticle = {'StatEffect': tables.StringCol(40),
                            'P': tables.Float32Col(shape=(TF, electrodes)),
                            'F': tables.Float32Col(shape=(TF, electrodes))}
        AnovaGFPParticle = {'StatEffect': tables.StringCol(40),
                            'P': tables.Float32Col(shape=(TF, 1)),
                            'F': tables.Float32Col(shape=(TF, 1))}

        IntermediateResultAllParticle = {'CondName': tables.StringCol(40),
                                         'Type': tables.StringCol(40),
                                         'Data': tables.Float32Col(
            shape=(TF, electrodes))}
        IntermediateResultGFPParticle = {'CondName': tables.StringCol(40),
                                         'Type': tables.StringCol(40),
                                         'Data': tables.Float32Col(
            shape=(TF, 1))}

        PostHocAllParticle = {'Name': tables.StringCol(60),
                              'P': tables.Float32Col(shape=(TF, electrodes)),
                              'T': tables.Float32Col(shape=(TF, electrodes))}
        PostHocGFPParticle = {'Name': tables.StringCol(60),
                              'P': tables.Float32Col(shape=(TF, 1)),
                              'T': tables.Float32Col(shape=(TF, 1))}

        # crating tables for model
        TablesModel = H5.createTable('/', 'Model', ModelParticle)

        # writing Model informations
        NewRow = TablesModel.row
        for t in AllFactor:
            for n in AllFactor[t]:
                NewRow['Name'] = n
                NewRow['Value'] = AllFactor[t][n]
                NewRow['Type'] = t
                NewRow.append()

        # Creating info Table
        TablesInfo = H5.createTable('/', 'Info', InfoParticle)

        # writing Model informations
        NewRow = TablesInfo.row
        for l in range(NbLine):
            for c in InfoDict:
                NewRow[c] = InfoDict[c][l]
            NewRow.append()

        # Creating Result Tables
        H5.createTable(AllRes, 'Anova', AnovaAllParticle)
        H5.createTable(GFPRes, 'Anova', AnovaGFPParticle)
        H5.createTable(
            AllRes, 'IntermediateResult', IntermediateResultAllParticle)
        H5.createTable(
            GFPRes, 'IntermediateResult', IntermediateResultGFPParticle)
        H5.createTable(AllRes, 'PostHoc', PostHocAllParticle)
        H5.createTable(GFPRes, 'PostHoc', PostHocGFPParticle)

        # Create Progress Table
        H5.createTable('/', 'Progress', {'Text': tables.StringCol(256)})

        # Close H5 file
        H5.close()
