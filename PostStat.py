import numpy as np
import tables
import wx
import os

# ClassMultiple testing correction using mathematical morphology
##Tables definition
##
##tables:
##/Shape # Keep the shape of the Data, to reshape after calculation # simple array
##/Data/All #using createEArray('/','AllData',tables.Float64Atom(),(TF,Electrodes,0))
##/Data/GFP #using createEArray('/','AllData',tables.Float64Atom(),(TF,1,0))
##/Model #using a tables with col= {Name of the factor, Value of factor (Vector), type of Factor (Within,between, covariate, subject)
##/Info # using a tables that contain all the information in the "ExcelSheet"
##/Result/All/Anova # Tables with col ={Name of the effect (i.e main effect, interaction, ..),P Data(Without any threshold (alpha, consecpoits, ...),F Data}
##/Result/All/IntermediateResult # Tabes with Col = {Condition name, Type (Mean,pearson correaltion,Sandard error,...),Data Corresponding in Type}
##/Result/All/PostHoc # Tabes with Col = {Name,P,T}
##/Result/GFP/Anova # Tables with col ={Name of the effect (i.e main effect, interaction, ..),P Data(Without any threshold (alpha, consecpoits, ...),F Data}
##/Result/GFP/IntermediateResult # Tabes with Col = {Condition name, Type (Mean,pearson correaltion,Sandard error,...)}
##/Result/GFP/PostHoc # Tabes with Col = {Name,P,T}

class MultipleTestingCorrection:
    def __init__(self, H5, parent,Anova=True,DataGFP=False,TF=1,Alpha=0.05,SpaceCont=1,SpaceFile=None):
        """ Initialisation for multiple testing correction analysis
            H5 = H5 File
            Parent = Parent windows
            Anova = True extracting Anova Result, False = Extracting PastHoc Result
            We need this because Criteria (Time or Space) Could be different between Anova and PostHoc
            DataGFP = is it performing on GFP Data
            TF = Number of consecutive Time frame entered by usr
            Alpha = Statistical Thesjold Difine by usr
            SpaceCont = Contigous space point define by usr
            SpaceFiel File with 3d coodonate to determine distance
        """
        self.parent = parent
        self.file = tables.openFile(H5, mode='a')
        if DataGFP:
            if Anova:
                self.Data=self.file.getNode('/Result/GFP/Anova')
            else:
                self.Data=self.file.getNode('/Result/GFP/PostHoc')
            ShapeOriginalData=self.file.getNode('/Shape').read()
            ShapeOriginalData[1]=1
        else:
            if Anova:
                self.Data=self.file.getNode('/Result/All/Anova')
            else:
                self.Data=self.file.getNode('/Result/All/PostHoc')
            ShapeOriginalData=self.file.getNode('/Shape').read()
        # extrating infromion usefull
        self.TF=TF
        self.SpaceCont=SpaceCont
        if SpaceFile is not None:
            self.MatrixDist(SpaceFile)
        self.Alpha=Alpha
        # used for user interface feed back
        # number of terms in Anova or in PostHoc mulipled by the number of TF* number of space point muliply * 2(Erosion/Dilatation)
        self.NbCalcul=len(Data)*ShapeOriginalData.prod()*2
    def MathematicalMorphology(self,Dilate=True):
        """Calulation of the Mathematical Morphology (Erosion and Dilatation)
            The infromation like BinaryData, Number on Conseq TF , Number of Contigouis points, and the Amtrix Distance are in self
         """
        # Definition of problematic time point that correspond to time border
        TimeStart = (self.TF - 1) / 2
        TimeEnd = self.TF - TimeStart
        # creation of a Mask of 0 and size of the Bianary Data
        Mask = np.zeros(self.BinaryData)
        # erosion
        if self.BinaryData.sum() != 0:# if their is no significant point we don't need mathematical morphology
            #loop over all time point
            for time in range(sefl.BinaryData.shape[0]):
                # checking if the times of interest (composed of the time value +/- TF) exist Border problem
                BeginTime = time - TimeStart
                EndTime = time + TimeEnd
                if BeginTime < 0:
                    BeginTime = 0
                    EndTime = self.TF
                elif EndTime > self.BinaryData.shape[0]:
                    BeginTime = self.BinaryData.shape[0] - self.TF
                    EndTime = self.BinaryData.shape[0]
                # Loop over all space points
                for dim in range(self.BinaryData.shape[1]):
                    # Extract the Distance of the point in space of interest in the matrix of all Distance
                    # Space is a mvector containting all the distance between the point dim to the other point
                    space = self.Distance[dim, :]
                    # sort these distance and extract the index from the colser (itself) to the farer
                    space = space.argsort()
                    # keep only the pn poitns correcponding to the criteria choosen by the user
                    space = space[0:SpaceCriteria]
                    # element is a subset of interest containting the time and the sapce of interest
                    # element is a boolean subset where true means significatif points and 0 means no significative points
                    element = self.BinaryData[BeginTime:EndTime, space] ==1
                    if Dilate:# dilatatioon
                        if element.any():
                            # if at least one point in element is significant mask at time =time and space =dim => 1 else leave 0
                            Mask[time, dim]=1
                    else: #Erosion
                        if element.all():
                            # if all poitns of element = 1 mask at time =time and space =dim => 1  else leave a 0
                            Mask[time, dim]=1
                    self.n += 1
                    pourcent = str(100.0 * (n) / (self.NbCaclul))
                    pourcent = pourcent[0:pourcent.find('.') + 3]
                    self.dlg.Update(self.n, " ".join(['Progression  :',
                                           pourcent, ' %']))
        self.Mask=Mask

    def Calculation(self):
        """ Calucualtion of mathematical morpholgy on all results anova and PostHoc"""
        #Dictionary Correction Anova Contain the mask of All Anova Mask Keys = statistical Condition name
        self.dlg = wx.ProgressDialog(
                    'Multiple Test Correction',
                    'Calculation in progress : 0 %',
                    NbCaclul, parent=self.parent,
                    style=wx.PD_AUTO_HIDE | wx.PD_REMAINING_TIME)
        self.dlg.SetSize((200, 130))
        self.n=0
        CorrectedMask={}
        # applaying test on Data (Anova or PostHoc)
        for a in self.Data:
            P=a[1]
            Name=a[2]
            # adapt the conseutive number of time frame and the contigous criteria to the length o Data
            # in case of the user made a mistake.
            # if their is only one TF we cannot have a TF value !=1
            # same remark for the contigous criteria
            if P.shape[0]==1:
                self.TF=1
            if P.shape[1] == 1: 
                SpaceCriteria = 1
            # we compute an openning more restrictive that means errosion folwed by a dilatation
            # the BinaryData is all the pvalue lower than Alpha
            self.BinaryData=np.zeros(P.shape)
            self.BinaryData[P<self.Alpha]=1
            # Erosion
            self.MathematicalMorphology(self,Dilate=False)
            # the BinaryData is the Mask the come from the errosion
            self.BinaryData=self.Mask
            # Dilatation
            self.MathematicalMorphology(self,Dilate=True)
            CorrectedMask[Name]=self.Mask
        # Corrected Mask is a Dicionary tha containe all the binarymask
        self.CorrectedMask=CorrectedMask

       
##############            
class WriteData:
    # Writing Intermediate Result and Result
    def write(self, ResultFolder, DataGFP=False):
        """ Write Estimator, not real slope and
        real mean depending on design"""

        # Create result Folder
        IntermediateResultPath = "\\".join([ResultFolder, 'ItermediateResult'])
        try:
            pwd.mkdir(IntermediateResultPath)
        except:
            pass
        IntermediateResults = self.file.listNodes(
            '/Result/IntermediateResult/')
        if IntermediateResults == []:
            if DataGFP:
                CoefTerms = self.file.getNode('/Result/Anova/GFP/CoefTerms')
                CoefTerms = CoefTerms.read()
                CoefValue = self.file.getNode('/Result/Anova/GFP/CoefValue')

            else:
                CoefTerms = self.file.getNode('/Result/Anova/All/CoefTerms')
                CoefTerms = CoefTerms.read()
                CoefValue = self.file.getNode('/Result/Anova/All/CoefValue')

            NameBetween = self.file.getNode('/Names/Between')
            NameBetween = NameBetween.read()
            if not NameBetween:
                NameBetween = []
            NameCovariate = self.file.getNode('/Names/Covariate')
            NameCovariate = NameCovariate.read()
            if not NameCovariate:
                NameCovariate = []
            NameWithin = self.file.getNode('/Names/Within')
            NameWithin = NameWithin.read()
            if not NameWithin:
                NameWithin = []
            Subject = self.file.getNode('/Model/Subject')
            Subject = Subject.read()

            SheetValue = self.file.getNode('/Sheet/Value')
            SheetValue = SheetValue.read()
            NbRow = len(SheetValue[0])

            Between = self.file.getNode('/Model/Between')
            Between = np.array(Between.read())
            Covariate = self.file.getNode('/Model/Covariate')
            Covariate = np.array(Covariate.read())
            Within = self.file.getNode('/Model/Within')
            Within = Within.read()

            # Write real Mean and Real slope
            Covariate = self.file.getNode('/Model/Covariate')
            Covariate = np.array(Covariate.read())

            # Simple Regression only Covariate
            if NameWithin == [] and NameBetween == []:
                # Extracting Data
                Data = []
                for s in Subject:
                    if DataGFP:
                        text = [
                            '/DataGFP/Subject', str(int(s - 1)), '/Condition0']
                        DataTmp = self.file.getNode("".join(text))
                        DataTmp = DataTmp.read()
                        Data.append(DataTmp)
                        EphFile = ['GFP-Level']
                    else:
                        text = [
                            '/Data/Subject', str(int(s - 1)), '/Condition0']
                        DataTmp = self.file.getNode("".join(text))
                        DataTmp = DataTmp.read()
                        Data.append(DataTmp)
                        if self.shape[1] < 500:
                            EphFile = ['WaveForm-Level']
                        else:
                            EphFile = ['BrainSpace-Level']
                Data = np.array(Data)

                # Caclulate slope for all covariate terms
                CovData = ['Cov']
                if len(Covariate.shape) == 1:
                    Covariate = Covariate.reshape((Covariate.shape[0], 1))

                for j, cov in enumerate(NameCovariate):
                    CovariateTmp = Covariate[:, j]
                    CovariateTmp = np.vstack(
                        [CovariateTmp.T, np.ones(len(CovariateTmp))]).T
                    Shape = list(Data.shape)
                    Shape = np.array(Shape[1:len(Shape)])
                    DataCov = Data.reshape((Data.shape[0], Shape.prod()))
                    Slope, intercept = np.linalg.lstsq(
                        CovariateTmp, DataCov)[0]
                    Slope = Slope.reshape(tuple(Shape))
                    RTmp = []
                    for t in DataCov.T:
                        RTmp.append(np.corrcoef(CovariateTmp[:, 0], t)[0, 1])
                    test = np.corrcoef(CovariateTmp[:, 0], DataCov[:, 161])
                    CovData.append(str(j))
                    SlopeGroup = self.file.createGroup(
                        '/Result/IntermediateResult/', "".join(CovData))
                    tmp = CovData.pop(-1)
                    EphFile.append('txt')
                    EphFile.append(cov)
                    NameFile = self.file.createArray(
                        SlopeGroup, 'Name', EphFile)
                    tmp = EphFile.pop(-1)
# SlopeData=self.file.createArray(SlopeGroup,'Slope',tables.Float64Atom(),(self.shape[0],self.shape[1],0))
# R=self.file.createArray(SlopeGroup,'R',tables.Float64Atom(),(self.shape[0],self.shape[1],0))
                    RTmp = np.array(RTmp)
                    RTmp = RTmp.reshape((self.shape[0], self.shape[1]))
                    Slope = Slope.reshape((self.shape[0], self.shape[1]))
                    Slope = self.file.createArray(SlopeGroup, 'Slope', Slope)
                    R = self.file.createArray(SlopeGroup, 'R', RTmp)
# R.append(RTmp)
# SlopeData.append(Slope)

            # Within/Between Subject Factor and or not and covariate
            else:

                LevelWithin = self.file.getNode('/Info/Level')
                LevelWithin = LevelWithin.read()
                LevelWithin = np.array(LevelWithin)
                if LevelWithin.any():
                    NbConditionWithin = LevelWithin.prod()
                else:
                    NbConditionWithin = 1

                if len(Subject.shape) == 1:
                    Subject = Subject.reshape((Subject.shape[0], 1))
                NbSubject = int(Subject.max())
                if NbSubject != NbRow:
                    NbSubject = NbRow

                # No WithinSubject Factors

                if NameWithin != []:
                    ConditionNumber = np.array([])
                    for i in range(NbConditionWithin):
                        tmp = np.ones((NbSubject))
                        tmp = tmp * (i + 1)
                        ConditionNumber = np.concatenate(
                            (ConditionNumber, tmp))
                    ConditionNumber = ConditionNumber.reshape(
                        (ConditionNumber.shape[0], 1))
                # their is at list one withinsubject factor
                else:
                    ConditionNumber = np.ones((NbSubject))
                # if their is only one between subject factor transfomring into
                # 2d matrix
                if len(Between.shape) == 1:
                    Between = Between.reshape((Between.shape[0], 1))
                # if their is only one Covariate factor transfomring into 2d
                # matrix
                if len(Covariate.shape) == 1:
                    Covariate = Covariate.reshape((Covariate.shape[0], 1))

                fs = self.file.getNode('/Info/FS')
                fs = fs.read()

                # Generating Varaible named with Within and Between subject
                # name and their levels
                ConditionTxt = []
                Level = []

                for i, w in enumerate(NameWithin):
                    try:
                        NbLevel = int(Within[:, i].max())
                    except:
                        NbLevel = int(Within.max())
                    Level.append(NbLevel)
                    for j in range(NbLevel):
                        text = [w, str(j + 1), '=0']
                        exec("".join(text))
                    ConditionTxt.append(w)
                for i, w in enumerate(NameBetween):
                    try:
                        NbLevel = int(Between[:, i].max())
                    except:
                        NbLevel = int(Between.max())

                    Level.append(NbLevel)
                    for j in range(NbLevel):
                        text = [w, str(j + 1), '=0']
                        exec("".join(text))
                    ConditionTxt.append(w)
                Level = np.array(Level)

                # Generating all combinaison between and within subject factors
                NbCondition = Level.prod()
                Combinaison = np.zeros((NbCondition, len(Level)))
                for k, i in enumerate(Level):
                    repet = NbCondition / i
                    NbCondition = repet
                    for j in range(i):
                        fact = np.ones((repet, 1)) * j + 1
                        debut = j * repet
                        fin = (j + 1) * repet
                        Combinaison[debut:fin, k] = fact[:, 0]
                    n = j
                    while Combinaison[Level.prod() - 1, k] == 0:
                        for j in range(i):
                            n += 1
                            fact = np.ones((repet, 1)) * j + 1
                            debut = n * repet
                            fin = (n + 1) * repet
                            Combinaison[debut:fin, k] = fact[:, 0]
                # no within subject subject factor
                if NameWithin == []:
                    Condition = Between
                # No between subject factor
                elif NameBetween == []:
                    Condition = Within
                else:
                    Condition = np.concatenate((Within, Between), axis=1)

                # Extracting Data for each Combinaison
                if DataGFP:
                    shape = self.file.getNode('/Info/ShapeGFP')
                    shape = shape.read()
                    shape = (shape[0], 1)
                else:
                    shape = self.file.getNode('/Info/Shape')
                    shape = shape.read()
                    shape = (shape[0], shape[1])
                Moyenne = np.zeros(shape)
                SE = np.zeros(shape)
                # /Result/IntermediateResult/{FileName}
                n = 0
                InterceptData = ['Intercept']
                CovData = ['Cov']
                for c in Combinaison:
                    InterceptData = ['Intercept']
                    CovData = ['Cov']
                    tmp = (Condition == c).sum(axis=1) == len(c)
                    SubjectTmp = Subject[tmp]
                    ConditionTmp = ConditionNumber[tmp]
                    InterceptData.append(str(n))
                    CovData.append(str(n))
                    n += 1
                    self.CaluclatingIntercept(InterceptData, DataGFP,
                                              SubjectTmp, ConditionTmp,
                                              ConditionTxt, c, Subject)

                    # Covariate
                    for j, cov in enumerate(NameCovariate):
                        EphFile = self.file.getNode(
                            "/".join(['/Result/IntermediateResult/',
                                      "".join(InterceptData), 'Name']))
                        EphFile = EphFile.read()
                        EphFile.append(cov)
                        CovData.append(str(j))
                        self.CalculatingSlope(CovData, SubjectTmp,
                                              ConditionTmp, j, EphFile,
                                              DataGFP, Covariate, tmp)
                        tmp = CovData.pop(-1)
        IntermediateResults = self.file.listNodes(
            '/Result/IntermediateResult/')
        for i in IntermediateResults:
            Name = i.Name.read()
            Name.append('eph')
            Name = ".".join(Name)
            IntTest = str(i)
            IntTest = IntTest.find('Intercept')
            if IntTest == -1:  # covarience Data
                Slope = i.Slope.read()
                self.WriteEphFile(
                    "/".join([IntermediateResultPath,
                              Name.replace('txt', 'Slope')]), Slope)
                R = i.R.read()
                self.WriteEphFile(
                    "/".join([IntermediateResultPath,
                              Name.replace('txt', 'R')]), R)
            else:  # intercept data
                MeanData = i.Mean.read()
                self.WriteEphFile(
                    "/".join([IntermediateResultPath,
                              Name.replace('txt', 'Mean')]), MeanData)
                SE = i.SE.read()
                self.WriteEphFile(
                    "/".join([IntermediateResultPath,
                              Name.replace('txt', 'SE')]), SE)
        # Remove GFP and WaveForm keep only if IS that is long to calculate
        if self.shape[1] < 500 or DataGFP:
            self.file.removeNode('/Result/IntermediateResult', recursive=True)
            self.file.createGroup('/Result/', 'IntermediateResult')

    def WriteEphFile(self, PathName, Data):
        fichier = open(PathName, "w")
        # on prend le header
        fs = self.file.getNode('/Info/FS')
        fs = fs.read()
        shape = Data.shape
        header = [str(int(shape[1])), '\t', str(
            int(shape[0])), '\t', str(int(fs)), '\n']
        # ecrtiture du header
        fichier.write("".join(header))
        # boucle sur les time chaque ligne est un temps
        for time in Data:
            # ecriture ligne par ligne
            time.tofile(fichier, sep="\t", format="%s")
            # saut de ligne
            fichier.write("\n")
        fichier.close()

    def ReadingData(self, SubjectTmp, ConditionTmp, t, DataGFP):
        Data = []
        for i, s in enumerate(SubjectTmp):
            if DataGFP:
                text = [
                    '/DataGFP/Subject', str(int(s - 1)),
                    '/Condition', str(int(ConditionTmp[i] - 1))]
                DataTmp = self.file.getNode("".join(text))
                if self.shape[0] == 1:
                    Data.append(DataTmp.read())
                else:
                    Data.append(DataTmp.read()[t])
            else:
                text = [
                    '/Data/Subject', str(int(s - 1)),
                    '/Condition', str(int(ConditionTmp[i] - 1))]
                DataTmp = self.file.getNode("".join(text))
                if self.shape[0] == 1:
                    Data.append(DataTmp.read())
                else:
                    Data.append(DataTmp.read()[t, :])
        self.Data = np.array(Data)

    def CaluclatingIntercept(self, GroupName, DataGFP, SubjectTmp,
                             ConditionTmp, ConditionTxt,
                             Combinaison, Subject):
        if DataGFP:
            EphFile = ['GFP-Level']
        else:
            if self.shape[1] < 500:
                EphFile = ['WaveForm-Level']
            else:
                EphFile = ['BrainSpace-Level']
        EphFile.append('txt')
        for i, combi in enumerate(Combinaison):
            txt = [ConditionTxt[i], str(int(combi))]
            EphFile.append("-".join(txt))
        InterceptGroup = self.file.createGroup(
            '/Result/IntermediateResult/', "".join(GroupName))
        NameFile = self.file.createArray(InterceptGroup, 'Name', EphFile)
        MeanData = self.file.createEArray(
            InterceptGroup, 'Mean', tables.Float64Atom(), (0, self.shape[1]))
        SE = self.file.createEArray(
            InterceptGroup, 'SE', tables.Float64Atom(), (0, self.shape[1]))
        for t in range(self.shape[0]):
            self.ReadingData(SubjectTmp, ConditionTmp, t, DataGFP)
            MeanTmp = self.Data.mean(axis=0)
            # problem due to Gmean GFP have only one value
            if MeanTmp.shape == ():
                MeanTmp = np.array([MeanTmp])
                MeanTmp = MeanTmp.reshape((1, len(MeanTmp)))
            if len(MeanTmp.shape) == 1:
                MeanTmp = MeanTmp.reshape((1, self.shape[1]))
            MeanData.append(MeanTmp)
            SETmp = self.Data.std(axis=0) / np.sqrt(len(Subject))
            if SETmp.shape == ():
                SETmp = np.array([SETmp])
            if len(SETmp.shape) == 1:
                SETmp = SETmp.reshape((1, len(SETmp)))
            SE.append(SETmp)

    def CalculatingSlope(self, GroupName, SubjectTmp, ConditionTmp,
                         CovLabel, EphFile, DataGFP, Covariate, tmp):

        SlopeGroup = self.file.createGroup(
            '/Result/IntermediateResult/', "".join(GroupName))
        NameFile = self.file.createArray(SlopeGroup, 'Name', EphFile)
        SlopeData = self.file.createEArray(
            SlopeGroup, 'Slope', tables.Float64Atom(), (0, self.shape[1]))
        R = self.file.createEArray(
            SlopeGroup, 'R', tables.Float64Atom(), (0, self.shape[1]))
        for t in range(self.shape[0]):
            self.ReadingData(SubjectTmp, ConditionTmp, t, DataGFP)
            CovariateTmp = Covariate[tmp, CovLabel]
            CovariateTmp = np.vstack(
                [CovariateTmp.T, np.ones(len(CovariateTmp))]).T
            Shape = list(self.Data.shape)
            Shape = np.array(Shape[1:len(Shape)])
            DataCov = self.Data.reshape(
                (int(self.Data.shape[0]), int(Shape.prod())))
            SlopeTmp, intercept = np.linalg.lstsq(CovariateTmp, DataCov)[0]
            SlopeTmp = SlopeTmp.reshape((1, len(SlopeTmp)))
            RTmp = []
            for t in DataCov.T:
                RTmp.append(np.corrcoef(CovariateTmp[:, 0], t)[0, 1])
            RTmp = np.array(RTmp)
            RTmp = RTmp.reshape((1, len(RTmp)))
            R.append(np.array(RTmp))
            SlopeData.append(SlopeTmp)

    def WriteData(self, ResultFolder):
        # Ecrire les resultats en Eph
        """ TODO: translate to english
        ecritrue de l'eph :
        nom de l'eph = name_eph
        path de l'eph = path_result"""
        OutPutFiles = []
        pwd.chdir(ResultFolder)
        if self.Anova:
            for i, Terms in enumerate(self.Terms):
                if self.GFP:
                    FileNameP = ['GFP-Data']
                    FileNameF = ['GFP-Data']
                else:
                    if self.shape[1] < 500:
                        FileNameP = ['WaveForm-Data']
                        FileNameF = ['WaveForm-Data']
                    else:
                        FileNameP = ['BrainSpace-Data']
                        FileNameF = ['BrainSpace-Data']
                if self.Param:
                    FileNameP.append('Param')
                    FileNameF.append('Param')
                else:
                    FileNameP.append('Non-Param')
                    FileNameF.append('Non-Param')

                if Terms.find(':') != -1:  # term interaction
                    FileNameP.append('Interaction')
                    FileNameP.append(Terms.replace(':', '-'))
                    FileNameP.append('P')
                    FileNameP.append('eph')
                    FileNameF.append('Interaction')
                    FileNameF.append(Terms.replace(':', '-'))
                    FileNameF.append('F')
                    FileNameF.append('eph')

                else:  # main effect
                    FileNameP.append('Main Effect')
                    FileNameP.append(Terms)
                    FileNameP.append('P')
                    FileNameP.append('eph')
                    FileNameF.append('Main Effect')
                    FileNameF.append(Terms)
                    FileNameF.append('F')
                    FileNameF.append('eph')
                # creation du fichier P
                OutPutFiles.append(FileNameP)
                if len(".".join(FileNameP)) + len(ResultFolder) > 256:
                    txt = " ".join(
                        ['Path is too long for',
                         ".".join(FileNameP),
                         'File it will be not write'])
                    dlg = wx.MessageDialog(
                        None, txt, "Error", style=wx.OK | wx.ICON_INFORMATION)
                    retour = dlg.ShowModal()
                    dlg.Destroy()
                else:
                    fichier = open(".".join(FileNameP), "w")
                    fs = self.file.getNode('/Info/FS')
                    fs = fs.read()
                    # on prend le header
                    header = [str(int(self.shape[1])), '\t', str(
                        int(self.shape[0])), '\t', str(int(fs)), '\n']
                    # ecrtiture du header
                    fichier.write("".join(header))
                    # boucle sur les time chaque ligne est un temps
                    Raw = np.zeros((self.shape[0], self.shape[1]))
                    Raw = self.P.read()[:, i].reshape(
                        (self.shape[0], self.shape[1]))
                    Raw = 1 - Raw
                    Data = Raw * self.Mask[:, :, i]
                    for time in Data:
                        # ecriture ligne par ligne
                        time.tofile(fichier, sep="\t", format="%s")
                        # saut de ligne
                        fichier.write("\n")
                    fichier.close()

                    # creation du fichier F
                    OutPutFiles.append(FileNameF)
                    fichier = open(".".join(FileNameF), "w")
                    fs = self.file.getNode('/Info/FS')
                    fs = fs.read()
                    # on prend le header
                    header = [str(int(self.shape[1])), '\t', str(
                        int(self.shape[0])), '\t', str(int(fs)), '\n']
                    # ecrtiture du header
                    fichier.write("".join(header))
                    # boucle sur les time chaque ligne est un temps
                    Raw = self.F.read()[:, i].reshape(
                        (self.shape[0], self.shape[1]))
                    Data = Raw * self.Mask[:, :, i]
                    for time in Data:
                        # ecriture ligne par ligne
                        time.tofile(fichier, sep="\t", format="%s")
                        # saut de ligne
                        fichier.write("\n")
                    fichier.close()
        else:
            # write Post-Hoc File

            for i, Terms in enumerate(self.Terms):
                if self.GFP:
                    FileNameP = ['GFP-Data']
                    FileNameT = ['GFP-Data']
                else:
                    if self.shape[1] < 500:
                        FileNameP = ['WaveForm-Data']
                        FileNameT = ['WaveForm-Data']
                    else:
                        FileNameP = ['BrainSpace-Data']
                        FileNameT = ['BrainSpace-Data']
                if self.Param:
                    FileNameP.append('Param')
                    FileNameT.append('Param')
                else:
                    FileNameP.append('Non-Param')
                    FileNameT.append('Non-Param')
                FileNameP.append(Terms)
                FileNameP.append('P')
                FileNameP.append('eph')

                FileNameT.append(Terms)
                FileNameT.append('T')
                FileNameT.append('eph')

                # creation du fichier P
                OutPutFiles.append(FileNameP)
                if len(".".join(FileNameP)) + len(ResultFolder) > 256:
                    txt = " ".join(
                        ['Path is too long for',
                         ".".join(FileNameP),
                         'File it will be not write'])
                    dlg = wx.MessageDialog(
                        None, txt, "Error", style=wx.OK | wx.ICON_INFORMATION)
                    retour = dlg.ShowModal()
                    dlg.Destroy()
                else:
                    fichier = open(".".join(FileNameP), "w")
                    fs = self.file.getNode('/Info/FS')
                    fs = fs.read()
                    # on prend le header
                    header = [str(int(self.shape[1])), '\t', str(
                        int(self.shape[0])), '\t', str(int(fs)), '\n']
                    # ecrtiture du header
                    fichier.write("".join(header))
                    # boucle sur les time chaque ligne est un temps
                    Raw = np.zeros((self.shape[0], self.shape[1]))
                    Raw = self.P.read()[:, i].reshape(
                        (self.shape[0], self.shape[1]))
                    Raw = 1 - Raw
                    Data = Raw * self.Mask[:, :, i]
                    for time in Data:
                        # ecriture ligne par ligne
                        time.tofile(fichier, sep="\t", format="%s")
                        # saut de ligne
                        fichier.write("\n")
                    fichier.close()

                    # creation du fichier F
                    OutPutFiles.append(FileNameT)
                    fichier = open(".".join(FileNameT), "w")
                    fs = self.file.getNode('/Info/FS')
                    fs = fs.read()
                    # on prend le header
                    header = [str(int(self.shape[1])), '\t', str(
                        int(self.shape[0])), '\t', str(int(fs)), '\n']
                    # ecrtiture du header
                    fichier.write("".join(header))
                    # boucle sur les time chaque ligne est un temps
                    Raw = self.F.read()[:, i].reshape(
                        (self.shape[0], self.shape[1]))
                    Data = Raw * self.Mask[:, :, i]
                    for time in Data:
                        # ecriture ligne par ligne
                        time.tofile(fichier, sep="\t", format="%s")
                        # saut de ligne
                        fichier.write("\n")
                    fichier.close()

        self.OutPutFiles = OutPutFiles

