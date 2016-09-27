import wx
import tables
import itertools
import numpy as np
import multiprocessing
from scipy import stats
import rpy2.robjects as robjects
import rpy2.robjects.numpy2ri as numpy2ri
from datetime import datetime

class Anova:

    """
    Calculation of Anovas across time and/or Space using data from the H5 files
    Anovas is caculating unsing aov R function linked with python using Rpy2
    """

    def __init__(self, H5, parent):
        """
        Reading H5 Files to extract factor information and creating R formula
        """

        # Specify relevant variables
        self.cancel = False
        self.parent = parent

        # Reading H5 File
        self.file = tables.openFile(H5, mode='a')

        # Numerical Factor Information from the Datatable
        self.tableFactor = self.file.getNode('/Model').read()

        # Extraction of relevant factor information from tableFactor
        formulaModel, formulaErrorTerm, subjectName = self.extractTableFactor(
            self.tableFactor)
        # Wrting Formula
        if formulaErrorTerm != []:
            self.Formula = 'DataR~%s+Error(%s/(%s))' % (
                "*".join(formulaModel), subjectName,
                "*".join(formulaErrorTerm))
        else:
            self.Formula = 'DataR~%s + Error(%s)' % ("*".join(formulaModel),subjectName)

    def Param(self, DataGFP=False):

        # Extracting GFP or All Data
        if DataGFP:
            data = self.file.getNode('/Data/GFP')
            shapeOrigData = self.file.getNode('/Shape').read()
            shapeOrigData[1] = 1
        else:
            data = self.file.getNode('/Data/All')
            shapeOrigData = self.file.getNode('/Shape').read()

        # Calculating the Anova using R and multiprocessing (=parallel)
        n_jobs = multiprocessing.cpu_count()
        pool = multiprocessing.Pool(n_jobs)
        blockSize = 100
        boundaries = range(0, data.shape[0]-1, blockSize) + [data.shape[0]]
        cutList = [boundaries[i:i + 2] for i in range(len(boundaries) - 1)]
        results = [(cut[0], pool.apply_async(calculatingAovR, (
            self.tableFactor, data[cut[0]:cut[1], :],
            self.Formula))) for cut in cutList]
        results = [r[1] for r in sorted(results)]
        # Update window
        dlg = wx.ProgressDialog(
            'Parametric Anova', 'Time remaining for Calculation:',
            maximum=len(results), parent=self.parent,
            style=wx.PD_CAN_ABORT | wx.PD_AUTO_HIDE | wx.PD_ELAPSED_TIME |
            wx.PD_REMAINING_TIME | wx.PD_SMOOTH)
        dlg.SetSize((200, 175))

        # Aggregate the results
        tic=datetime.now()
        for i, r in enumerate(results):
            P, F, _ = r.get()
            if i == 0:
                pValues = P
                FValues = F
            else:
                pValues = np.vstack((pValues, P))
                FValues = np.vstack((FValues, F))

            dlg.Update(i)
            toc=datetime.now()
        self.elapsedTime=toc-tic
##        self.elapsedTime = str(dlg.GetChildren()[3].Label)

        # Check if the computation was canceled
        if not dlg.Update(i)[0]:
            self.cancel = True
        
        dlg.Destroy()

        # Saving results to H5 file
        _, _, terms = calculatingAovR(self.tableFactor, data[0, :],
                                      self.Formula)

        if DataGFP:
            res = self.file.getNode('/Result/GFP/Anova')
            pValues = pValues.reshape((shapeOrigData[0], 1, len(terms)))
            FValues = FValues.reshape((shapeOrigData[0], 1, len(terms)))
        else:
            res = self.file.getNode('/Result/All/Anova')
            pValues = pValues.reshape((shapeOrigData[0], shapeOrigData[1],
                                      len(terms)))
            FValues = FValues.reshape((shapeOrigData[0], shapeOrigData[1],
                                      len(terms)))

        newRow = res.row
        for i, t in enumerate(terms):

            if t.find(':') != -1:
                condType = 'Interaction'
            else:
                condType = 'Main_Effect'

            conditionName = "_".join([condType, t]).replace(':', '-')
            newRow['StatEffect'] = conditionName
            newRow['P'] = pValues[:, :, i]
            newRow['F'] = FValues[:, :, i]
            newRow.append()

    def NonParam(self, nIteration, DataGFP=False):

        # Extracting GFP or All Data
        if DataGFP:
            data = self.file.getNode('/Data/GFP')
            shapeOrigData = self.file.getNode('/Shape').read()
            shapeOrigData[1] = 1
        else:
            data = self.file.getNode('/Data/All')
            shapeOrigData = self.file.getNode('/Shape').read()

        # Update window
        dlg = wx.ProgressDialog(
            'Non Parametric Anova', 'Time remaining for Calculation:',
            maximum=nIteration + 1, parent=self.parent,
            style=wx.PD_CAN_ABORT | wx.PD_AUTO_HIDE | wx.PD_ELAPSED_TIME |
            wx.PD_REMAINING_TIME | wx.PD_SMOOTH)
        dlg.SetSize((200, 175))

        # Calculating the Anova using R and multiprocessing (=parallel)
        tic=datetime.now()
        n_jobs = multiprocessing.cpu_count()
        pool = multiprocessing.Pool(n_jobs)
        blockSize = 100
        boundaries = range(0, data.shape[0]-1, blockSize) + [data.shape[0]]
        cutList = [boundaries[i:i + 2] for i in range(len(boundaries) - 1)]
        resultsReal = [(cut[0], pool.apply_async(calculatingAovR, (
            self.tableFactor, data[cut[0]:cut[1], :],
            self.Formula))) for cut in cutList]
        resultsReal = [r[1] for r in sorted(resultsReal)]

        # Aggregate the resultsReal
        for i, r in enumerate(resultsReal):
            _, FReal, _ = r.get()
            if i == 0:
                FRealList = FReal
            else:
                FRealList = np.vstack((FRealList, FReal))

        occurrence = np.zeros(FRealList.shape)

        for itID in xrange(nIteration):
            dataBoot = self.bootstrapData(data[:], self.FactorSubject)

            resultsBoot = [(cut[0], pool.apply_async(calculatingAovR, (
                self.tableFactor, dataBoot[cut[0]:cut[1], :],
                self.Formula))) for cut in cutList]
            resultsBoot = [r[1] for r in sorted(resultsBoot)]

            # Aggregate the resultsBoot
            for i, r in enumerate(resultsBoot):
                _, FBoot, _ = r.get()
                if i == 0:
                    FBootList = FBoot
                else:
                    FBootList = np.vstack((FBootList, FBoot))

            # Count occurrence where Boot has higher F-value than Real
            occurrence[FBootList - FRealList >= 0] += 1
            dlg.Update(itID)
        toc=datetime.now()
        self.elapsedTim=toc-tic
##        self.elapsedTime = str(dlg.GetChildren()[3].Label)

        # Check if the computation was canceled
        if not dlg.Update(i)[0]:
            self.cancel = True

        dlg.Destroy()

        # Saving results to H5 file
        pValues = occurrence/float(nIteration)
        _, _, terms = calculatingAovR(self.tableFactor, data[0, :],
                                      self.Formula)

        if DataGFP:
            res = self.file.getNode('/Result/GFP/Anova')
            pValues = pValues.reshape((shapeOrigData[0], 1, len(terms)))
            FValues = FRealList.reshape((shapeOrigData[0], 1, len(terms)))
        else:
            res = self.file.getNode('/Result/All/Anova')
            pValues = pValues.reshape((shapeOrigData[0], shapeOrigData[1],
                                      len(terms)))
            FValues = FRealList.reshape((shapeOrigData[0], shapeOrigData[1],
                                        len(terms)))

        newRow = res.row
        for i, t in enumerate(terms):

            if t.find(':') != -1:
                condType = 'Interaction'
            else:
                condType = 'Main_Effect'

            conditionName = "_".join([condType, t]).replace(':', '-')
            newRow['StatEffect'] = conditionName
            newRow['P'] = pValues[:, :, i]
            newRow['F'] = FValues[:, :, i]
            newRow.append()

    def bootstrapData(self, data, factorSubject):
        NbSubject = factorSubject.max()
        subjectLabel = np.arange(1, NbSubject + 1)
        order = []
        for r in range(NbSubject):
            np.random.shuffle(subjectLabel)
            drawing = np.nonzero(factorSubject == subjectLabel[0])[0]
            # Shuffle the subjectLabel to permute within subject Factor within
            # each Subject. If their is no within Subject factor len(drawing)=1
            np.random.shuffle(drawing)
            order.append(drawing)

        # reshape order to correspond to factorSubject style
        order = np.array(order)
        order = np.reshape(order.T, np.array(order.shape).prod())
        return data[:, order]

    def extractTableFactor(self, tableFactor):
        formulaModel = []
        formulaErrorTerm = []

        numpy2ri.activate()
        for t in self.tableFactor:
            factorName = t[0]
            factorType = t[1]
            factorData = t[2]
            # sending Data to global variable in R (Factor definition for
            # Subject, Within or Between Type and FloatVector for Covariate
            if factorType == 'Covariate':
                tmp = robjects.FloatVector(factorData)
                robjects.globalenv[factorName] = tmp
            else:
                tmp = robjects.r.factor(factorData)
                robjects.globalenv[factorName] = tmp
            # Creating Fromula for R - different treatement for within and
            # between subject Factor
            if factorType == 'Subject':
                subjectName = factorName
                self.FactorSubject = factorData
            elif factorType == 'Within':
                formulaModel.append(factorName)
                formulaErrorTerm.append(factorName)
            else:
                formulaModel.append(factorName)

        return formulaModel, formulaErrorTerm, subjectName


def calculatingAovR(tableFactor, Data, Formula):
    """Computes and fits an Analysis of Variance Model"""
    numpy2ri.activate()
    for t in tableFactor:
        factorName = t[0]
        factorType = t[1]
        factorData = t[2]
        # sending Data to global variable in R (Factor definition for
        # Subject, Within or Between Type and FloatVector for Covariate
        if factorType == 'Covariate':
            tmp = robjects.FloatVector(factorData)
            robjects.globalenv[factorName] = tmp
        else:
            tmp = robjects.r.factor(factorData)
            robjects.globalenv[factorName] = tmp

    DataR = robjects.Matrix(Data.T)
    robjects.globalenv["DataR"] = DataR
    TextR = 'aov(%s)' % Formula
    express = robjects.r.parse(text=TextR)
    Fit = robjects.r.eval(express)
    robjects.globalenv["Fit"] = Fit
    raw = robjects.r.summary(Fit)
    print(raw)
    pValue = np.hstack([np.array([c[4][:-1] for c in r]) for r in raw])
    FValue = np.hstack([np.array([c[3][:-1] for c in r]) for r in raw])

    terms = []
    if len(raw) == 1:
        for r in raw[0]:
            for t in r.rownames[0:-1]:
                terms.append(t.replace(' ', ''))
    else:
        for i in raw:
            for r in i:
                for t in r.rownames[0:-1]:
                    terms.append(t.replace(' ', ''))

    return pValue, FValue, terms


class PostHoc:

    """PostHoc Analysis using data from the H5 files"""

    def __init__(self, H5, parent):

        """
        Reading H5 Files to extract factor information and creating R formula
        """

        # Specify relevant variables
        self.cancel = False
        self.parent = parent

        # Reading H5 File
        self.file = tables.openFile(H5, mode='a')

        # Numerical Factor Information from the Datatable
        self.tableFactor = self.file.getNode('/Model').read()

        # Extraction of relevant factor information from tableFactor
        self.between = {}
        self.within = {}
        self.betweenName = []
        self.withinName = []
        # Generating within and between dictionary with condition name
        for t in self.tableFactor:
            factorName = t[0]
            factorType = t[1]
            factorData = t[2]
            if factorType == 'Between':
                self.between[factorName] = factorData
                self.betweenName.append(factorName)
            elif factorType == 'Within':
                self.within[factorName] = factorData
                self.withinName.append(factorName)
            elif factorType == 'Subject':
                self.subject = factorData

        # Transform dict into matrix for easy use
        self.within = np.array(self.within.values())
        self.between = np.array(self.between.values())

        # Extract different levels for each between subject factor
        levelsBetween = self.between.max(axis=1).astype('int')

        # Cacluate all possible combinations using the max number of levels
        allCombinationBetween = itertools.product(
            range(1, levelsBetween.max() + 1), repeat=len(levelsBetween))

        # Reduce combination to only existing ones
        existingCombi = []
        for c in allCombinationBetween:
            combinations = np.array(c)
            # existing combinations
            if (levelsBetween - combinations < 0).sum() == 0:
                existingCombi.append(combinations)
        existingCombi = np.array(existingCombi)

        # Create all possible combinations and extract the booleans
        # corresponding to it.
        allCombiBool = {}
        condName = []
        for e in existingCombi:
            boolBetween = []
            tmpNameBetween = []
            for c, l in enumerate(e):
                boolBetween.append(self.between[c, :] == l)
                tmpNameBetween.append("-".join([self.betweenName[c],
                                      str(int(l))]))
            boolBetween = np.array(boolBetween)

            withinCombi = self.within[:, self.subject == 1].T
            for w in withinCombi:
                boolWithin = []
                tmpNameWithin = []
                for c, l in enumerate(w):
                    boolWithin.append(self.within[c, :] == l)
                    tmpNameWithin.append("-".join([self.withinName[c],
                                         str(int(l))]))
                boolWithin = np.array(boolWithin)
                bools = np.append(boolBetween, boolWithin, axis=0)
                # name of the arrangement
                tmpName = ".".join([".".join(tmpNameBetween),
                                    ".".join(tmpNameWithin)])
                condName.append(tmpName)
                allCombiBool[tmpName] = bools.prod(axis=0) == 1

        # Dictionary of boolean correcponding to all arangements
        self.Arrangement = allCombiBool

        # Creation of all combinations with the 2 arrangements for the t-test
        self.combination = itertools.combinations(condName, 2)

        # Number of tests using combinatory calculation for the progression bar
        self.nbTest = len([t for t in itertools.combinations(condName, 2)])


        print 'DONE. Till here.'



    def CalculationTTest(self, data,Combination,SubjectFactor,Arrangement,NonParam=False):
        # H5 array don't be acces with bool
        Cond=np.arange(0,data.shape[1])
        # Value1 and Value2 = Bolean vector correponding to the condition for the t-test based on name in Combination
        Value1= Arrangement[Combination[0]]
        Value2= Arrangement[Combination[1]]
        # extracted the subject lable for the 2 condtions
        Subj1=SubjectFactor[Value1]
        Subj2=SubjectFactor[Value2]
        #sort the subject label to be sure they are in a same way for comparison
        Subj1.sort()
        Subj2.sort()
        # if number of element in Condition1 != number of element in Condition2 => unpaired, if Subject Value are identical Paired
        if Value1.sum()==Value2.sum():
            TestPaired=SubjectFactor[Value1]-SubjectFactor[Value2]==0
        else:
            # a numpy array with Tue and false because the test is on TestPaired.all()
            TestPaired=np.array([True,False])
        
        if TestPaired.all():
            if NonParam:
                # extracting the label of each condition
                C1=Cond[Value1]
                C2=Cond[Value2]
                # C1 and C2 as same size
                NbC=len(C1)
                Label=np.arange(0,NbC)
                C1Boot=[]
                C2Boot=[]
                for r in Label:
                    np.random.shuffle(Label)
                    Sbj=Label[0]
                    if np.random.rand()<=0.5:# permutation between 2
                        C1Boot.append(C1[Sbj])
                        C2Boot.append(C2[Sbj])
                    else:
                        # c1 became C1 adn vice and vera
                        C2Boot.append(C1[Sbj])
                        C1Boot.append(C2[Sbj])
                # Randomization procidure (Paired) (Bootstrapping Subject then permutation within subject)
                t,p=stats.ttest_rel(data[:,C1Boot],data[:,C2Boot],axis=1)
                
            else:
                t,p=stats.ttest_rel(data[:,Cond[Value1]],data[:,Cond[Value2]],axis=1)
        else:
            if NonParam:
                # extracting the label of each condition
                C1=Cond[Value1]
                C2=Cond[Value2]
                NbC1=len(C1)
                NbC2=len(C2)
                AllC=np.append(C1,C2)
                Label=np.arange(0,NbC1+NbC2)
                # Randomization procidure (Un Paired)(Bootstraping)
                BootLabel=[]
                for r in Label:
                    np.random.shuffle(Label)
                    BootLabel.append(Label[0])
                C1Boot=BootLabel[0:NbC1]
                C2Boot=BootLabel[NbC1:NbC1+NbC2]
                
                t,p=stats.ttest_ind(data[:,C1Boot],data[:,C2Boot],axis=1)
            else:
               t,p=stats.ttest_ind(data[:,Cond[Value1]],data[:,Cond[Value2]],axis=1)
        return t,p

    def Param(self, DataGFP=False):
        # Extracting GFP or All Data
        if DataGFP:
            data=self.file.getNode('/Data/GFP')
            shapeOrigData=self.file.getNode('/Shape').read()
            Res=self.file.getNode('/Result/GFP/PostHoc')
            shapeOrigData[1]=1
        else:
            data=self.file.getNode('/Data/All')
            shapeOrigData=self.file.getNode('/Shape').read()
            Res=self.file.getNode('/Result/All/PostHoc')
        dlg = wx.ProgressDialog('Parametric T-test',
                                "/".join(['PostHoc T-Test : 0',
                                          str(self.nbTest)]),
                                self.nbTest,
                                parent=self.parent,
                                style=wx.PD_CAN_ABORT |
                                wx.PD_AUTO_HIDE | wx.PD_REMAINING_TIME | wx.PD_ELAPSED_TIME)
        dlg.SetSize((200, 175))
        tic=datetime.now()
        n=0
        NewRow=Res.row
        for Combination in self.combination:
            t,p=self.CalculationTTest(data,Combination,self.subject,self.Arrangement)
            # Reshaping Data
            t=t.reshape((shapeOrigData[0], shapeOrigData[1]))
            p=p.reshape((shapeOrigData[0], shapeOrigData[1]))
            # Saving Result into the H5
            NewRow['Name']='_'.join(Combination)
            NewRow['P']=p
            NewRow['T']=t
            NewRow.append()
            # update the remaing time dilog box
            
            n+=1
            prog = "".join(['PostHoc T-Test : ', str(n), '/', str(self.nbTest)])
            Cancel = dlg.Update(n, prog)
            if Cancel[0] == False:
                dlgQuest = wx.MessageDialog(None,
                                                "Do you really want to cancel?",
                                                "Confirm Cancel",
                                                wx.OK | wx.CANCEL | wx.ICON_QUESTION)
                result = dlgQuest.ShowModal()
                dlgQuest.Destroy()
                if result == wx.ID_OK:
                    self.cancel = True
                    break
                else:
                    self.cancel = False
                    dlg.Resume()
        toc=datetime.now()
        self.elapsedTime=toc-tic
##        self.elapsedTime = str(dlg.GetChildren()[3].Label)

        dlg.Close()
        dlg.Destroy()

    def NonParam(self, Iter, DataGFP=False):
         # Extracting GFP or All Data
        if DataGFP:
            data=self.file.getNode('/Data/GFP')
            shapeOrigData=self.file.getNode('/Shape').read()
            Res=self.file.getNode('/Result/GFP/PostHoc')
            shapeOrigData[1]=1
        else:
            data=self.file.getNode('/Data/All')
            shapeOrigData=self.file.getNode('/Shape').read()
            Res=self.file.getNode('/Result/All/PostHoc')
        dlg = wx.ProgressDialog('Parametric T-test',
                                "/".join(['PostHoc T-Test : 0',
                                          str(self.nbTest)]),
                                self.nbTest,
                                parent=self.parent,
                                style=wx.PD_CAN_ABORT |
                                wx.PD_AUTO_HIDE | wx.PD_REMAINING_TIME | wx.PD_ELAPSED_TIME)
        dlg.SetSize((200, 175))
        n=0
        NewRow=Res.row
        
        for Combination in self.combination:
            t,p=self.CalculationTTest(data,Combination,self.subject,self.Arrangement)
            TReal=t
            Count=np.zeros(TReal.shape)
            for i in range(Iter):
                t,p=self.CalculationTTest(data,Combination,self.subject,self.Arrangement,NonParam=True)
                TBoot=t
                Diff=TBoot-TReal
                Count[Diff>0]+=1
            p=Count/flot(Iter)
            # Reshaping Data
            t=TReal.reshape((shapeOrigData[0], shapeOrigData[1]))
            p=p.reshape((shapeOrigData[0], shapeOrigData[1]))
            # Saving Result into the H5
            NewRow['Name']=Combination
            NewRow['P']=p
            NewRow['T']=t
            NewRow.append()
            # update the remaing time dilog box
            
            n+=1
            prog = "".join(['PostHoc T-Test : ', str(n), '/', str(self.nbTest)])
            Cancel = dlg.Update(n, prog)
            if Cancel[0] == False:
                dlgQuest = wx.MessageDialog(None,
                                                "Do you really want to cancel?",
                                                "Confirm Cancel",
                                                wx.OK | wx.CANCEL | wx.ICON_QUESTION)
                result = dlgQuest.ShowModal()
                dlgQuest.Destroy()
                if result == wx.ID_OK:
                    self.cancel = True
                    break
                else:
                    self.cancel = False
                    dlg.Resume()
        dlg.Close()
        dlg.Destroy()
