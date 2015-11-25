import rpy2.robjects as robjects
import rpy2.robjects.numpy2ri
import numpy as np
from scipy import stats
import tables
import random
import wx


class Anova:

    """ TODO: translate to english
    Calculation of Anovas across time and/or Space using formating H5 files (See H5 format for information)
    Anovas is caculating unsing aov R function linked with python using Rpy2
    """

    def __init__(self, H5, parent):
        """ Reading H5 Files to extract Factor infrmations and creating R formula"""
        # Reading H5 File
        rpy2.robjects.numpy2ri.activate()
        self.Cancel = False
        self.parent = parent
        self.file = tables.openFile(H5, mode='a')
        # TableFactor is a vector with n dimenssion wher n = number of Terms incuding Subject
        TableFactor=self.file.getNode('/Model').read()
        #exporting information (name of Factor, type of factor, create the Formula)
        FormulaModel=[]
        FormulaErrorTerm =[]
        for t in TableFactor:
            FactorName=t[0]
            FactorType=t[1]
            FactorData=t[2]
            # sending Data to Glbal variable in R (Factor definition for Subject, Within or Between Type and FloatVector for Covariate
            if FactorType=='Covariate':
                tmp=robjects.FloatVector(FactorData)
                robjects.globalenv[FactorName]=tmp
            else:
                tmp=robjects.r.factor(FactorData)
                robjects.globalenv[FactorName]=tmp
            # Creating Fromula for R Defferent treatement for Within and between subject Factor
            if FactorType=='Subject':
                SubjectName=FactorName
                self.FactorSubject=FactorData
            elif FactorType=='Within':
                FormulaModel.append(FactorName)
                FormulaErrorTerm.append(FactorName)
            else:
                FormulaModel.append(FactorName)
        # Wrting Formula
        if FormulaErrorTerm!=[]:
            self.Formule = "".join(["DataR~","*".join(FormulaModel),'+ Error(',SubjectName,'/(',"*".join(FormulaErrorTerm),'))'])
        else:
            self.Formule = "".join(["DataR~","*".join(FormulaModel)]) 


    def Param(self, DataGFP=False):
        # Extracting GFP or All Data
        if DataGFP:
            Data=self.file.getNode('/Data/GFP')
        else:
            Data=self.file.getNode('/Data/All')
        ShapeOriginalData=self.file.getnode('/Shape').read()
            
        # Calculating the number of Annova percycle to avoid Memory problem
        NbAnova = int(Data.shape[0])
        Byte = np.array(Data.shape).prod()
        Cycle = int(Byte / 10000)
        try:
            NbAnovaCycle = NbAnova / Cycle
        except:
            NbAnovaCycle = NbAnova
  
        # Performed one Anova to Extract Terms Names
        Raw=self.CalculatingAovR(Data[0,:],Formule)
        # Terms Extraction
        Terms=[]
        # Len(Raw)=1 if not repeated measur !=2 if repeated Measure
        if len(Raw)==1:
            for r in Raw:
                    tmp=r.rownames
                    for t in tmp[0:-1]:
                        Terms.append(t.replace(' ',''))
        else:
            for i in Raw:
                for r in i:
                    tmp=r.rownames
                    for t in tmp[0:-1]:
                        Terms.append(t.replace(' ',''))

        # Terms is a list containing the order of th P different statistical output Name
        # Anova caculation using R
        Maximum = NbAnova
        dlg = wx.ProgressDialog('Parametric Anova',
                                'Calculation in progress : 0 %',
                                maximum=Maximum,
                                parent=self.parent,
                                style=wx.PD_CAN_ABORT |
                                wx.PD_AUTO_HIDE | wx.PD_REMAINING_TIME)
        dlg.SetSize((200, 175))
        n = 0
        end = 0
        # Calculation Separated into part to ovoid out of memory
        while fin1 < NbAnova:
            start = n * NbAnovaCycle
            end = (n + 1) * NbAnovaCycle
            n += 1
            if fin1 > NbAnova:
                fin1 = NbAnova
            # Calculating Anovas
            Raw=self.CalculatingAovR(Data[start:end,:],Formule)
            P,F=self.ExtractingStat(Raw)
            if n==0:
                PValue=P
                FValue=F
            else:
                PValue=np.append(PValue,P,axis=0)
                FValue=np.append(FValue,F,axis=0)
            #Dialog box for timing
            pourcent = str(100.0 * end / (NbAnova))
            pourcent = pourcent[0:pourcent.find('.') + 3]
            Cancel = dlg.Update(end, " ".join(['Progression  :', pourcent, ' %']))
            if Cancel[0] == False:
                dlgQuest = wx.MessageDialog(
                    None,
                    "Do you really want to cancel?",
                    "Confirm Cancel",
                    wx.OK | wx.CANCEL | wx.ICON_QUESTION)
                result = dlgQuest.ShowModal()
                dlgQuest.Destroy()
                if result == wx.ID_OK:
                    self.Cancel = True
                    break
                else:
                    self.Cancel = False
                    dlg.Resume()
        # Saving Results
        if DataGFP:
            Res=self.file.getNode('/Result/GFP/Anova')
        else:
            Res=self.file.getNode('/Result/All/Anova')
        PValue=PValue.reshape((ShapeOriginalData[0], ShapeOriginalData[1],len(Terms)))
        FValue=FValue.reshape((ShapeOriginalData[0], ShapeOriginalData[1],len(Terms)))
        dlg.Close()
        dlg.Destroy()
        
    def NonParam(self, Iter, DataGFP=False):
        Iter=int(Iter)
        # Extracting GFP or All Data
        if DataGFP:
            Data=self.file.getNode('/Data/GFP')
        else:
            Data=self.file.getNode('/Data/All')
        ShapeOriginalData=self.file.getnode('/Shape').read()
        # Calculating the number of Annova percycle to avoid Memory problem
        NbAnova = int(Data.shape[0])
        Byte = np.array(Data.shape).prod()
        Cycle = int(Byte / 10000)
        try:
            NbAnovaCycle = NbAnova / Cycle
        except:
            NbAnovaCycle = NbAnova
  
        # Performed one Anova to Extract Terms Names
        Raw=self.CalculatingAovR(Data[0,:],Formule)
        # Terms Extraction
        Terms=[]
        # Len(Raw)=1 if not repeated measur !=2 if repeated Measure
        if len(Raw)==1:
            for r in Raw:
                    tmp=r.rownames
                    for t in tmp[0:-1]:
                        Terms.append(t.replace(' ',''))
        else:
            for i in Raw:
                for r in i:
                    tmp=r.rownames
                    for t in tmp[0:-1]:
                        Terms.append(t.replace(' ',''))

        # Terms is a list containing the order of th P different statistical output Name
        # Anova caculation using R
        Maximum = NbAnova
        dlg = wx.ProgressDialog('Non Parametric Anova',
                                'Calculation in progress : 0 %',
                                maximum=Maximum,
                                parent=self.parent,
                                style=wx.PD_CAN_ABORT |
                                wx.PD_AUTO_HIDE | wx.PD_REMAINING_TIME)
        dlg.SetSize((200, 175))
        n = 0
        end = 0
        # Calculation Separated into part to ovoid out of memory
        while fin1 < NbAnova:
            #Originla Order Data                 
            start = n * NbAnovaCycle
            end = (n + 1) * NbAnovaCycle
            n += 1
            if fin1 > NbAnova:
                fin1 = NbAnova
            # Calculating Anovas
            Raw=self.CalculatingAovR(Data[start:end,:],Formule)
            P,FReal=self.ExtractingStat(Raw)
            Count=np.zeros(FReal.shape)
            # BootStraping Data
            for i in range(Iter):
                # Creating Bootstraping and permutation Data
                DataBoot=BootstrapedData(Data[start:end,:],FactorSubject)
                # Calculating F Value with Bootstraping Data
                Raw=self.CalculatingAovR(DataBoot,Formule)
                P,FBoot=self.ExtractingStat(Raw)
                # Count Anova by Anova if Fboot is bigger than FReal To difine PValue
                Diff=FBoot-FReal
                Count[Diff>=0]+=1
            P=Count/float(Iter)
            if n==0:
                PValue=P
                FValue=F
            else:
                PValue=np.append(PValue,P,axis=0)
                FValue=np.append(FValue,F,axis=0)
            #Dialog box for timing
            pourcent = str(100.0 * end / (NbAnova))
            pourcent = pourcent[0:pourcent.find('.') + 3]
            Cancel = dlg.Update(end, " ".join(['Progression  :', pourcent, ' %']))
            if Cancel[0] == False:
                dlgQuest = wx.MessageDialog(
                    None,
                    "Do you really want to cancel?",
                    "Confirm Cancel",
                    wx.OK | wx.CANCEL | wx.ICON_QUESTION)
                result = dlgQuest.ShowModal()
                dlgQuest.Destroy()
                if result == wx.ID_OK:
                    self.Cancel = True
                    break
                else:
                    self.Cancel = False
                    dlg.Resume()
        # Saving Results
        if DataGFP:
            Res=self.file.getNode('/Result/GFP/Anova')
        else:
            Res=self.file.getNode('/Result/All/Anova')
        PValue=PValue.reshape((ShapeOriginalData[0], ShapeOriginalData[1],len(Terms)))
        FValue=FValue.reshape((ShapeOriginalData[0], ShapeOriginalData[1],len(Terms)))
        dlg.Close()
        dlg.Destroy()  

    def ExtractingStat(Raw):
        for i,r in enumerate(Raw):
            Dat=np.array(r)
            if i==0:
                P=Dat[:,4,0:-1]
                F=Dat[:,3,0:-1]
            else:
                P=np.append(P,Dat[:,4,0:-1],axis=1)
                F=np.append(F,Dat[:,3,0:-1],axis=1)
        P[np.isnan(P)]=1
        F[np.isnan(F)]=0
        return P,F

    def CalculatingAovR(Data,Formula):
        DataR = robjects.Matrix(Data.T)
        robjects.globalenv["DataR"] = DataR
        TextR = ['aov(', Formula, ')']
        express = rpy2.robjects.r.parse(text="".join(TextR))
        Fit = rpy2.robjects.r.eval(express)
        robjects.globalenv["Fit"] = Fit
        # calcul Anova
        Raw = robjects.r.summary(Fit)
        return Raw
    def BootstrapedData(Data,FactorSubject):
        NbSubject=FactorSubject.max()
        SubjectLabel=np.arange(1,NbSubject+1)
        Order=[]
        for r in range(NbSubject):
            np.random.shuffle(SubjectLabel)
            Drawing=np.nonzero(FactorSubject==SubjectLabel[0])[0]
            # Shuffle the Subject Label to permute within subject Factor within each Subject. If their is no within Subject factor len(Drawing)=1
            np.random.shuffle(Drawing)
            Order.append(Drawing)
        Order=np.array(Order)
        # reshape Order to correspond to SubjectFactor style Subject 1= subect NbSubjt+1,...
        Order=np.int64(np.reshape(Order.T,np.array(Order.shape).prod()))
        return Data[:,Order]

###Done until this part I have to test on real Data
                

class ExtractDataNonParam:

    def __init__(self, file, debut, fin, GFP, OrderSubject, OrderCond):
        if GFP:
            shape = file.getNode('/Info/ShapeGFP')
        else:
            shape = file.getNode('/Info/Shape')
        shape = shape.read()
        NbSujet = int(shape[len(shape) - 1])
        NbCond = int(shape[len(shape) - 2])
        NbAnovaCycle = fin - debut
        DataTmp = np.zeros((NbAnovaCycle, NbCond, NbSujet))
        for i, s in enumerate(OrderSubject):
            for c in OrderCond[i]:
                if GFP:
                    location = [
                        '/DataGFP/Subject', str(s), '/Condition', str(c)]
                else:
                    location = ['/Data/Subject', str(s), '/Condition', str(c)]
                tmp = file.getNode("".join(location))
                tmp = tmp.read()
                NbAnova = tmp.shape
                NbAnova = np.array(NbAnova)
                tmp = tmp.reshape(NbAnova.prod())
                DataTmp[:, c, s] = tmp[debut:fin]
        # DataTmp=DataTmp.reshape((NbAnovaCycle,NbCond*NbSujet))
        self.extract = DataTmp
        del(DataTmp)


class PostHoc:

    def __init__(self, H5, Parent):
        self.Parent = Parent
        self.file = tables.openFile(H5, mode='r+')
        # models
        Between = self.file.getNode('/Model/Between')
        self.Between = np.array(Between.read())
        Within = self.file.getNode('/Model/Within')
        self.Within = np.array(Within.read())
        Subject = self.file.getNode('/Model/Subject')
        self.Subject = Subject.read()
        # Names
        NameBetween = self.file.getNode('/Names/Between')
        self.NameBetween = NameBetween.read()
        NameWithin = self.file.getNode('/Names/Within')
        self.NameWithin = NameWithin.read()
        self.Cancel = False

    def Param(self, DataGFP=False):
        if DataGFP:
            shape = self.file.getNode('/Info/ShapeGFP')
        else:
            shape = self.file.getNode('/Info/Shape')
        shape = shape.read()
        # Mettre le veteur sujet en 2 dimentions, afin d'etre sur que la
        # deuxième dimention existe
        if len(self.Subject.shape) == 1:
            self.Subject = self.Subject.reshape((self.Subject.shape[0], 1))
        NbSubject = self.Subject.max()
        LevelWithin = self.file.getNode('/Info/Level')
        LevelWithin = LevelWithin.read()
        NbConditionWithin = LevelWithin.prod()
        # test il y a un facteur Within
        if self.Within.any():
            ConditionNumber = np.array([])
            for i in range(NbConditionWithin):
                tmp = np.ones((NbSubject))
                tmp = tmp * (i + 1)
                ConditionNumber = np.concatenate((ConditionNumber, tmp))
            ConditionNumber = ConditionNumber.reshape(
                (ConditionNumber.shape[0], 1))
        else:
            # il n'y a pas de facteur Within
            ConditionNumber = np.ones((NbSubject))
        # Mettre le veteur Between en 2 dimentions, afin d'etre sur que la
        # deuxième dimention existe
        if self.Between.any():
            if len(self.Between.shape) == 1:
                self.Between = self.Between.reshape((self.Between.shape[0], 1))

        fs = self.file.getNode('/Info/FS')
        fs = fs.read()

        # cree la list CondionTxt, contenant le nom des facteurs within puis between pour les noms en sortie
        # creation de la liste level contenant le niveau de chaque facteur
        # d'abord within puis between
        ConditionTxt = []
        Level = []
        if self.Within.any():
            for i, w in enumerate(self.NameWithin):
                try:
                    NbLevel = int(self.Within[:, i].max())
                except:
                    NbLevel = int(self.Within.max())
                Level.append(NbLevel)
                for j in range(NbLevel):
                    text = [w, str(j + 1), '=0']
                    exec("".join(text))
                ConditionTxt.append(w)
        if self.Between.any():
            for i, w in enumerate(self.NameBetween):
                try:
                    NbLevel = int(self.Between[:, i].max())
                except:
                    NbLevel = int(self.Between.max())
                Level.append(NbLevel)
                for j in range(NbLevel):
                    text = [w, str(j + 1), '=0']
                    exec("".join(text))
                ConditionTxt.append(w)

        Level = np.array(Level)
        NbCondition = Level.prod()
        # creation de la list combinaison regroupant toute les combinaison
        # possible aves les facteurs within et between
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

        # creation de la matrice condition avec les veteurs/matrice within et/ou between.
        # Ces matrice sont composer de valeur 1,2, nb niveau par niveau matrice utiliser pour le model dans R
        # facteur within et Between
        if self.Within.any() and self.Between.any():
            Condition = np.concatenate((self.Within, self.Between), axis=1)
        # Pas de facteur Between
        elif self.Within.any():
            Condition = self.Within
        # Pas de facteur within que Between
        elif self.Between.any():
            Condition = self.Between

        NbTest = np.array(range(len(Combinaison))).sum()
        dlg = wx.ProgressDialog('Parametric T-test',
                                "/".join(['PostHoc T-Test : 0',
                                          str(NbTest)]),
                                NbTest,
                                parent=self.Parent,
                                style=wx.PD_CAN_ABORT |
                                wx.PD_AUTO_HIDE | wx.PD_REMAINING_TIME)
        dlg.SetSize((200, 175))
        # lecture des donnees dans le H5 pour cree les matrices permettant le
        # calcul des t-test
        NbFactorWithin = self.Within.shape[1]
        Name = []
        n = 0
        if DataGFP:  # c'est sur le GFP
            ResultP = self.file.createEArray('/Result/PostHoc/GFP',
                                             'P',
                                             tables.Float64Atom(),
                                             (shape[0] * shape[1], 0))
            ResultT = self.file.createEArray(
                '/Result/PostHoc/GFP',
                'T',
                tables.Float64Atom(),
                (shape[0] * shape[1], 0))
        else:  # c'est sur toutes les electrodes
            ResultP = self.file.createEArray(
                '/Result/PostHoc/All',
                'P',
                tables.Float64Atom(),
                (shape[0] * shape[1], 0))
            ResultT = self.file.createEArray(
                '/Result/PostHoc/All',
                'T',
                tables.Float64Atom(),
                (shape[0] * shape[1], 0))
        for Nbc, c1 in enumerate(Combinaison):
            tmp = (Condition == c1).sum(axis=1) == len(c1)
            SubjectTmp = self.Subject[tmp]
            ConditionTmp = ConditionNumber[tmp]
            Data1 = []
            for i, s in enumerate(SubjectTmp):
                if DataGFP:
                    text = ['/DataGFP/Subject',
                            str(int(s - 1)),
                            '/Condition',
                            str(int(ConditionTmp[i] - 1))]
                    DataTmp = self.file.getNode("".join(text))
                    DataTmp = DataTmp.read()
                    Data1.append(DataTmp)
                else:
                    text = ['/Data/Subject',
                            str(int(s - 1)),
                            '/Condition',
                            str(int(ConditionTmp[i] - 1))]
                    DataTmp = self.file.getNode("".join(text))
                    DataTmp = DataTmp.read()
                    Data1.append(DataTmp)
            Data1 = np.array(Data1)
            EphFile = []
            for i, combi in enumerate(c1):
                txt = [ConditionTxt[i], str(int(combi))]
                EphFile.append("-".join(txt))
            EphFile.append('vs')
            for c in range(Nbc + 1, len(Combinaison)):
                c2 = Combinaison[c]
                tmp = (Condition == c2).sum(axis=1) == len(c2)
                SubjectTmp = self.Subject[tmp]
                ConditionTmp = ConditionNumber[tmp]
                Data2 = []
                for i, s in enumerate(SubjectTmp):
                    if DataGFP:
                        text = ['/DataGFP/Subject',
                                str(int(s - 1)),
                                '/Condition',
                                str(int(ConditionTmp[i] - 1))]
                        DataTmp = self.file.getNode("".join(text))
                        DataTmp = DataTmp.read()
                        Data2.append(DataTmp)
                    else:
                        text = ['/Data/Subject',
                                str(int(s - 1)),
                                '/Condition',
                                str(int(ConditionTmp[i] - 1))]
                        DataTmp = self.file.getNode("".join(text))
                        DataTmp = DataTmp.read()
                        Data2.append(DataTmp)
                Data2 = np.array(Data2)
                for i, combi in enumerate(c2):
                    txt = [ConditionTxt[i], str(int(combi))]
                    EphFile.append("-".join(txt))

                # que des paired T-test car pas de facteur Bewtween
                if self.NameBetween == []:
                    EphFile.insert(0, 'Paired-Ttest')
                    res = stats.ttest_rel(Data1, Data2, axis=0)
                    Name.append("".join(EphFile))
                    EphFile.remove('Paired-Ttest')
                # que des unpaired T-test car pas de facteur Within
                elif self.NameWithin == []:
                    EphFile.insert(0, 'UnPaired-Ttest')
                    res = stats.ttest_ind(Data1, Data2, axis=0)
                    Name.append(".".join(EphFile))
                    EphFile.remove('UnPaired-Ttest')
                # parend et un paired dependant du facteur between
                else:
                    # on test que tout les niveau des facteurs between soit les meme si c'est le cas on a du paired sinon unpaired
                    # on compare si les conditions between on les même niveau, on somme pui si cette somme est strictement egale
                    # au nombre total de condtions - nb de facteur within
                    # (nombre de facteur between) alos paired
                    # if true = paired
                    if (c2[NbFactorWithin:len(c2)] == c1[NbFactorWithin:len(c2)]).sum() == len(c1) - NbFactorWithin:
                        EphFile.insert(0, 'Paired-Ttest')
                        res = stats.ttest_rel(Data1, Data2, axis=0)
                        Name.append(".".join(EphFile))
                        EphFile.remove('Paired-Ttest')
                    else:
                        EphFile.insert(0, 'UnPaired-Ttest')
                        res = stats.ttest_ind(Data1, Data2, axis=0)
                        Name.append(".".join(EphFile))
                        EphFile.remove('UnPaired-Ttest')
                if len(res[1].shape) == 1:
                    taille = res[1].shape[0]
                    P = res[1].reshape((taille, 1))
                    T = res[0].reshape((taille, 1))
                else:
                    P = res[1]
                    T = res[0]

                ShapeData = P.shape
                ShapeData = np.array(ShapeData)
                P = P.reshape((ShapeData.prod(), 1))
                T = T.reshape((ShapeData.prod(), 1))
                ResultP.append(P)
                ResultT.append(T)
                n += 1
                EphFile = EphFile[0:EphFile.index('vs')]
                EphFile.append('vs')
                prog = "".join(['PostHoc T-Test : ', str(n), '/', str(NbTest)])
                Cancel = dlg.Update(n, prog)
                if Cancel[0] == False:
                    dlgQuest = wx.MessageDialog(None,
                                                "Do you really want to cancel?",
                                                "Confirm Cancel",
                                                wx.OK | wx.CANCEL | wx.ICON_QUESTION)
                    result = dlgQuest.ShowModal()
                    dlgQuest.Destroy()
                    if result == wx.ID_OK:
                        self.Cancel = True
                        break

                    else:
                        self.Cancel = False
                        dlg.Resume()

        if DataGFP:
            self.file.createArray('/Result/PostHoc/GFP', 'Terms', Name)
        else:
            self.file.createArray('/Result/PostHoc/All', 'Terms', Name)

    def NonParam(self, iter, DataGFP=False):
        if DataGFP:
            shape = self.file.getNode('/Info/ShapeGFP')
        else:
            shape = self.file.getNode('/Info/Shape')
        shape = shape.read()
        # Mettre le veteur sujet en 2 dimentions, afin d'etre sur que la
        # deuxième dimention existe
        if len(self.Subject.shape) == 1:
            self.Subject = self.Subject.reshape((self.Subject.shape[0], 1))
        NbSubject = self.Subject.max()
        LevelWithin = self.file.getNode('/Info/Level')
        LevelWithin = LevelWithin.read()
        NbConditionWithin = LevelWithin.prod()
        # test il y a un facteur Within
        if self.Within.any():
            ConditionNumber = np.array([])
            for i in range(NbConditionWithin):
                tmp = np.ones((NbSubject))
                tmp = tmp * (i + 1)
                ConditionNumber = np.concatenate((ConditionNumber, tmp))
            ConditionNumber = ConditionNumber.reshape(
                (ConditionNumber.shape[0], 1))
        else:
            # il n'y a pas de facteur Within
            ConditionNumber = np.ones((NbSubject))
        # Mettre le veteur Between en 2 dimentions, afin d'etre sur que la
        # deuxième dimention existe
        if self.Between.any():
            if len(self.Between.shape) == 1:
                self.Between = self.Between.reshape((self.Between.shape[0], 1))

        fs = self.file.getNode('/Info/FS')
        fs = fs.read()

        # cree la list CondionTxt, contenant le nom des facteurs within puis between pour les noms en sortie
        # creation de la liste level contenant le niveau de chaque facteur
        # d'abord within puis between
        ConditionTxt = []
        Level = []
        if self.Within.any():
            for i, w in enumerate(self.NameWithin):
                try:
                    NbLevel = int(self.Within[:, i].max())
                except:
                    NbLevel = int(self.Within.max())
                Level.append(NbLevel)
                for j in range(NbLevel):
                    text = [w, str(j + 1), '=0']
                    exec("".join(text))
                ConditionTxt.append(w)
        if self.Between.any():
            for i, w in enumerate(self.NameBetween):
                try:
                    NbLevel = int(self.Between[:, i].max())
                except:
                    NbLevel = int(self.Between.max())
                Level.append(NbLevel)
                for j in range(NbLevel):
                    text = [w, str(j + 1), '=0']
                    exec("".join(text))
                ConditionTxt.append(w)

        Level = np.array(Level)
        NbCondition = Level.prod()
        # creation de la list combinaison regroupant toute les combinaison
        # possible aves les facteurs within et between
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

        # creation de la matrice condition avec les veteurs/matrice within et/ou between.
        # Ces matrice sont composer de valeur 1,2, nb niveau par niveau matrice utiliser pour le model dans R
        # facteur within et Between
        if self.Within.any() and self.Between.any():
            Condition = np.concatenate((self.Within, self.Between), axis=1)
        # Pas de facteur Between
        elif self.Within.any():
            Condition = self.Within
        # Pas de facteur within que Between
        elif self.Between.any():
            Condition = self.Between

        NbTest = np.array(range(len(Combinaison))).sum()
        dlg = wx.ProgressDialog('Non-Parametric T-test',
                                "/".join(['PostHoc T-Test : 0',
                                          str(NbTest)]),
                                NbTest,
                                parent=self.Parent,
                                style=wx.PD_CAN_ABORT |
                                wx.PD_AUTO_HIDE | wx.PD_REMAINING_TIME)
        dlg.SetSize((200, 175))
        # lecture des donnees dans le H5 pour cree les matrices permettant le
        # calcul des t-test
        NbFactorWithin = self.Within.shape[1]
        Name = []
        n = 0
        if DataGFP:  # c'est sur le GFP
            ResultP = self.file.createEArray('/Result/PostHoc/GFP',
                                             'P',
                                             tables.Float64Atom(),
                                             (shape[0] * shape[1], 0))
            ResultT = self.file.createEArray('/Result/PostHoc/GFP',
                                             'T',
                                             tables.Float64Atom(),
                                             (shape[0] * shape[1], 0))
        else:  # c'est sur toutes les electrodes
            ResultP = self.file.createEArray('/Result/PostHoc/All',
                                             'P',
                                             tables.Float64Atom(),
                                             (shape[0] * shape[1], 0))
            ResultT = self.file.createEArray('/Result/PostHoc/All',
                                             'T',
                                             tables.Float64Atom(),
                                             (shape[0] * shape[1], 0))
        for Nbc, c1 in enumerate(Combinaison):
            tmp = (Condition == c1).sum(axis=1) == len(c1)
            SubjectTmp = self.Subject[tmp]
            ConditionTmp = ConditionNumber[tmp]
            Data1 = []
            text1 = []
            for i, s in enumerate(SubjectTmp):
                if DataGFP:
                    text = ['/DataGFP/Subject',
                            str(int(s - 1)),
                            '/Condition',
                            str(int(ConditionTmp[i] - 1))]
                    DataTmp = self.file.getNode("".join(text))
                    DataTmp = DataTmp.read()
                    Data1.append(DataTmp)
                else:
                    text = ['/Data/Subject',
                            str(int(s - 1)),
                            '/Condition',
                            str(int(ConditionTmp[i] - 1))]
                    DataTmp = self.file.getNode("".join(text))
                    DataTmp = DataTmp.read()
                    Data1.append(DataTmp)
                text1.append(text)
            Data1 = np.array(Data1)
            EphFile = []
            for i, combi in enumerate(c1):
                txt = [ConditionTxt[i], str(int(combi))]
                EphFile.append("-".join(txt))
            EphFile.append('vs')
            for c in range(Nbc + 1, len(Combinaison)):
                c2 = Combinaison[c]
                tmp = (Condition == c2).sum(axis=1) == len(c2)
                SubjectTmp = self.Subject[tmp]
                ConditionTmp = ConditionNumber[tmp]
                text2 = []
                Data2 = []
                for i, s in enumerate(SubjectTmp):
                    if DataGFP:
                        text = ['/DataGFP/Subject',
                                str(int(s - 1)),
                                '/Condition',
                                str(int(ConditionTmp[i] - 1))]
                        DataTmp = self.file.getNode("".join(text))
                        DataTmp = DataTmp.read()
                        Data2.append(DataTmp)
                    else:
                        text = ['/Data/Subject',
                                str(int(s - 1)),
                                '/Condition',
                                str(int(ConditionTmp[i] - 1))]
                        DataTmp = self.file.getNode("".join(text))
                        DataTmp = DataTmp.read()
                        Data2.append(DataTmp)
                    text2.append(text)
                Data2 = np.array(Data2)

                for i, combi in enumerate(c2):
                    txt = [ConditionTxt[i], str(int(combi))]
                    EphFile.append("-".join(txt))

                # que des paired T-test car pas de facteur Bewtween
                if self.NameBetween == []:
                    EphFile.insert(0, 'Paired-Ttest')
                    res = stats.ttest_rel(Data1, Data2, axis=0)
                    Name.append("".join(EphFile))
                    EphFile.remove('Paired-Ttest')
                # que des unpaired T-test car pas de facteur Within
                elif self.NameWithin == []:
                    EphFile.insert(0, 'UnPaired-Ttest')
                    res = stats.ttest_ind(Data1, Data2, axis=0)
                    Name.append(".".join(EphFile))
                    EphFile.remove('UnPaired-Ttest')
                # parend et un paired dependant du facteur between
                else:
                    # on test que tout les niveau des facteurs between soit les meme si c'est le cas on a du paired sinon unpaired
                    # on compare si les conditions between on les même niveau, on somme pui si cette somme est strictement egale
                    # au nombre total de condtions - nb de facteur within
                    # (nombre de facteur between) alos paired
                    # if true = paired
                    if (c2[NbFactorWithin:len(c2)] == c1[NbFactorWithin:len(c2)]).sum() == len(c1) - NbFactorWithin:
                        EphFile.insert(0, 'Paired-Ttest')
                        res = stats.ttest_rel(Data1, Data2, axis=0)
                        Name.append(".".join(EphFile))
                        EphFile.remove('Paired-Ttest')
                    else:
                        EphFile.insert(0, 'UnPaired-Ttest')
                        res = stats.ttest_ind(Data1, Data2, axis=0)
                        Name.append(".".join(EphFile))
                        EphFile.remove('UnPaired-Ttest')
                EphFile = EphFile[0:EphFile.index('vs')]
                EphFile.append('vs')
                TReal = res[0]
                Count = np.zeros(TReal.shape)
                iter = int(iter)
                for i in range(iter):
                    Data1 = []
                    Data2 = []
                    if self.NameBetween == []:
                        for s in range(len(text1)):
                            Subject = [random.randint(0, (len(text1)) - 1)]
                            if random.randint(0, 1) == 0:
                                DataTmp = self.file.getNode(
                                    "".join(text1[Subject[0]]))
                                DataTmp = DataTmp.read()
                                Data1.append(DataTmp)
                                DataTmp = self.file.getNode(
                                    "".join(text2[Subject[0]]))
                                DataTmp = DataTmp.read()
                                Data2.append(DataTmp)
                            else:
                                DataTmp = self.file.getNode(
                                    "".join(text2[Subject[0]]))
                                DataTmp = DataTmp.read()
                                Data1.append(DataTmp)
                                DataTmp = self.file.getNode(
                                    "".join(text1[Subject[0]]))
                                DataTmp = DataTmp.read()
                                Data2.append(DataTmp)
                        Data1 = np.array(Data1)
                        Data2 = np.array(Data2)
                        res = stats.ttest_rel(Data1, Data2, axis=0)
                    # que des unpaired T-test car pas de facteur Within
                    elif self.NameWithin == []:
                        text = []
                        text.extend(text1)
                        text.extend(text2)
                        for s in range(len(text1)):
                            Subject = [random.randint(0, (len(text)) - 1)]
                            DataTmp = self.file.getNode(
                                "".join(text[Subject[0]]))
                            DataTmp = DataTmp.read()
                            Data1.append(DataTmp)
                        for s in range(len(text2)):
                            Subject = [random.randint(0, (len(text)) - 1)]
                            DataTmp = self.file.getNode(
                                "".join(text[Subject[0]]))
                            DataTmp = DataTmp.read()
                            Data2.append(DataTmp)
                        Data1 = np.array(Data1)
                        Data2 = np.array(Data2)
                        res = stats.ttest_ind(Data1, Data2, axis=0)
                    # paired and un paired dependant du facteur between
                    else:
                        # on test que tout les niveau des facteurs between soit les meme si c'est le cas on a du paired sinon unpaired
                        # on compare si les conditions between on les même niveau, on somme pui si cette somme est strictement egale
                        # au nombre total de condtions - nb de facteur within
                        # (nombre de facteur between) alos paired
                        # if true = paired
                        if (c2[NbFactorWithin:len(c2)] == c1[NbFactorWithin:len(c2)]).sum() == len(c1) - NbFactorWithin:
                            for s in range(len(text1)):
                                Subject = [random.randint(0, (len(text1)) - 1)]
                                if random.randint(0, 1) == 0:
                                    DataTmp = self.file.getNode(
                                        "".join(text1[Subject[0]]))
                                    DataTmp = DataTmp.read()
                                    Data1.append(DataTmp)
                                    DataTmp = self.file.getNode(
                                        "".join(text2[Subject[0]]))
                                    DataTmp = DataTmp.read()
                                    Data2.append(DataTmp)
                                else:
                                    DataTmp = self.file.getNode(
                                        "".join(text2[Subject[0]]))
                                    DataTmp = DataTmp.read()
                                    Data1.append(DataTmp)
                                    DataTmp = self.file.getNode(
                                        "".join(text1[Subject[0]]))
                                    DataTmp = DataTmp.read()
                                    Data2.append(DataTmp)
                            Data1 = np.array(Data1)
                            Data2 = np.array(Data2)
                            res = stats.ttest_rel(Data1, Data2, axis=0)
                        else:
                            text = []
                            text.extend(text1)
                            text.extend(text2)
                            for s in range(len(text1)):
                                Subject = [random.randint(0, (len(text)) - 1)]
                                DataTmp = self.file.getNode(
                                    "".join(text[Subject[0]]))
                                DataTmp = DataTmp.read()
                                Data1.append(DataTmp)
                            for s in range(len(text2)):
                                Subject = [random.randint(0, (len(text)) - 1)]
                                DataTmp = self.file.getNode(
                                    "".join(text[Subject[0]]))
                                DataTmp = DataTmp.read()
                                Data2.append(DataTmp)
                            Data1 = np.array(Data1)
                            Data2 = np.array(Data2)
                            res = stats.ttest_ind(Data1, Data2, axis=0)
                    TBoot = res[0]
                    diff = TBoot - TReal
                    CountTmp = np.zeros(diff.shape)
                    CountTmp[diff > 0] = 1
                    Count += CountTmp
                P = Count / iter

                if len(res[1].shape) == 1:
                    taille = res[1].shape[0]
                    P = res[1].reshape((taille, 1))
                    T = res[0].reshape((taille, 1))
                else:
                    P = res[1]
                    T = res[0]
                ShapeData = P.shape
                ShapeData = np.array(ShapeData)
                P = P.reshape((ShapeData.prod(), 1))
                T = T.reshape((ShapeData.prod(), 1))
                ResultP.append(P)
                ResultT.append(T)
                n += 1
                prog = "".join(['PostHoc T-Test : ', str(n), '/', str(NbTest)])
                Cancel = dlg.Update(n, prog)
                if Cancel[0] == False:
                    dlgQuest = wx.MessageDialog(None,
                                                "Do you really want to cancel?",
                                                "Confirm Cancel",
                                                wx.OK | wx.CANCEL | wx.ICON_QUESTION)
                    result = dlgQuest.ShowModal()
                    dlgQuest.Destroy()
                    if result == wx.ID_OK:
                        self.Cancel = True
                        break

                    else:
                        self.Cancel = False
                        dlg.Resume()

        if DataGFP:
            self.file.createArray('/Result/PostHoc/GFP', 'Terms', Name)
        else:
            self.file.createArray('/Result/PostHoc/All', 'Terms', Name)

       
