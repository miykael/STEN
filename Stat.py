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
            self.Formula = 'DataR~%s+Error(%s/(%s))' % ("*".join(FormulaModel), SubjectName, "*".join(FormulaErrorTerm))
        else:
            self.Formula = 'DataR~%s' % "*".join(FormulaModel)


    def Param(self, DataGFP=False):
        # Extracting GFP or All Data
        if DataGFP:
            Data=self.file.getNode('/Data/GFP')
            ShapeOriginalData=self.file.getNode('/Shape').read()
            ShapeOriginalData[1]=1
        else:
            Data=self.file.getNode('/Data/All')
            ShapeOriginalData=self.file.getNode('/Shape').read()
        
            
        # Calculating the number of Annova percycle to avoid Memory problem
        NbAnova = int(Data.shape[0])
        Byte = np.array(Data.shape).prod()
        Cycle = int(Byte / 10000)
        try:
            NbAnovaCycle = NbAnova / Cycle
        except:
            NbAnovaCycle = NbAnova
  
        # Performed one Anova to Extract Terms Names
        Raw=self.CalculatingAovR(Data[0,:],self.Formula)
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
                                wx.PD_AUTO_HIDE | wx.PD_REMAINING_TIME | wx.PD_ELAPSED_TIME)
        dlg.SetSize((200, 175))
        n = 0
        end = 0
        # Calculation Separated into part to ovoid out of memory
        while end < NbAnova:
            start = n * NbAnovaCycle
            end = (n + 1) * NbAnovaCycle
            
            if end >= NbAnova:
                end = NbAnova
            # Calculating Anovas
            Raw=self.CalculatingAovR(Data[start:end,:],self.Formula)
            P,F=self.ExtractingStat(Raw)
            if n==0:
                PValue=P
                FValue=F
            else:
                PValue=np.append(PValue,P,axis=0)
                FValue=np.append(FValue,F,axis=0)
            n += 1
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

        self.elapsedTime = str(dlg.GetChildren()[3].Label)

        # Saving Results
        if DataGFP:
            Res=self.file.getNode('/Result/GFP/Anova')
            PValue=PValue.reshape((ShapeOriginalData[0], 1, len(Terms)))
            FValue=FValue.reshape((ShapeOriginalData[0], 1, len(Terms)))
        else:
            Res=self.file.getNode('/Result/All/Anova')
            PValue=PValue.reshape((ShapeOriginalData[0], ShapeOriginalData[1],len(Terms)))
            FValue=FValue.reshape((ShapeOriginalData[0], ShapeOriginalData[1],len(Terms)))

        NewRow=Res.row
        for i,t in enumerate(Terms):
            if t.find(':')!=-1: # interaction Term
                ConditionName="_".join(['Interaction',"-".join(t.split(':'))])
            else:# Main Effect
                ConditionName="_".join(['Main Effect',t])
            NewRow['StatEffect']=ConditionName
            NewRow['P']=PValue[:,:,i]
            NewRow['F']=FValue[:,:,i]
            NewRow.append()
        dlg.Close()
        dlg.Destroy()
                
    def NonParam(self, Iter, DataGFP=False):
        Iter=int(Iter)
        # Extracting GFP or All Data
        if DataGFP:
            Data=self.file.getNode('/Data/GFP')
            ShapeOriginalData=self.file.getNode('/Shape').read()
            ShapeOriginalData[1]=1
        else:
            Data=self.file.getNode('/Data/All')
            ShapeOriginalData=self.file.getNode('/Shape').read()
        # Calculating the number of Annova percycle to avoid Memory problem
        NbAnova = int(Data.shape[0])
        Byte = np.array(Data.shape).prod()
        Cycle = int(Byte / 10000)
        try:
            NbAnovaCycle = NbAnova / Cycle
        except:
            NbAnovaCycle = NbAnova
  
        # Performed one Anova to Extract Terms Names
        Raw=self.CalculatingAovR(Data[0,:],self.Formula)
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
                                wx.PD_AUTO_HIDE | wx.PD_REMAINING_TIME | wx.PD_ELAPSED_TIME)
        dlg.SetSize((200, 175))
        n = 0
        end = 0
        # Calculation Separated into part to ovoid out of memory
        while end < NbAnova:
            #Originla Order Data                 
            start = n * NbAnovaCycle
            end = (n + 1) * NbAnovaCycle
            
            if end >= NbAnova:
                end = NbAnova
            # Calculating Anovas
            Raw=self.CalculatingAovR(Data[start:end,:],self.Formula)
            P,FReal=self.ExtractingStat(Raw)
            Count=np.zeros(FReal.shape)
            # BootStraping Data
            for i in range(Iter):
                # Creating Bootstraping and permutation Data
                DataBoot=self.BootstrapedData(Data[start:end,:],self.FactorSubject)
                # Calculating F Value with Bootstraping Data
                Raw=self.CalculatingAovR(DataBoot,self.Formula)
                P,FBoot=self.ExtractingStat(Raw)
                # Count Anova by Anova if Fboot is bigger than FReal To difine PValue
                Diff=FBoot-FReal
                Count[Diff>=0]+=1
            P=Count/float(Iter)
            if n==0:
                PValue=P
                FValue=FReal
            else:
                PValue=np.append(PValue,P,axis=0)
                FValue=np.append(FValue,FReal,axis=0)
            n += 1
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

        self.elapsedTime = str(dlg.GetChildren()[3].Label)

        # Saving Results
        if DataGFP:
            Res=self.file.getNode('/Result/GFP/Anova')
            PValue=PValue.reshape((ShapeOriginalData[0], 1, len(Terms)))
            FValue=FValue.reshape((ShapeOriginalData[0], 1, len(Terms)))
        else:
            Res=self.file.getNode('/Result/All/Anova')
            PValue=PValue.reshape((ShapeOriginalData[0], ShapeOriginalData[1],len(Terms)))
            FValue=FValue.reshape((ShapeOriginalData[0], ShapeOriginalData[1],len(Terms)))

        NewRow=Res.row
        for i,t in enumerate(Terms):
            if t.find(':')!=-1: # interaction Term
                ConditionName="_".join(['Interaction',"-".join(t.split(':'))])
            else:# Main Effect
                ConditionName="_".join(['Main Effect',t])
            NewRow['StatEffect']=ConditionName
            NewRow['P']=PValue[:,:,i]
            NewRow['F']=FValue[:,:,i]
            NewRow.append()
        dlg.Close()
        dlg.Destroy()

    def ExtractingStat(self, Raw):
        """Extracts P and F values from Raw R output"""
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

    def CalculatingAovR(self, Data, Formula):
        """Computes and fits an Analysis of Variance Model"""
        DataR = robjects.Matrix(Data.T)
        robjects.globalenv["DataR"] = DataR
        TextR = 'aov(%s)' % Formula
        express = rpy2.robjects.r.parse(text=TextR)
        Fit = rpy2.robjects.r.eval(express)
        robjects.globalenv["Fit"] = Fit
        Raw = robjects.r.summary(Fit)
        return Raw

    def BootstrapedData(self, Data,FactorSubject):
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

###Done until this part I have to test on real Data Need to check PostHoc

import itertools

class PostHoc:

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
        Between={}
        Within={}
        BetweenName=[]
        WithinName=[]
        for t in TableFactor:
            FactorName=t[0]
            FactorType=t[1]
            FactorData=t[2]
            # Generating Within and Between Dictionary with condition Name
            if FactorType=='Between':
                Between[FactorName]=FactorData
                BetweenName.append(FactorName)
            elif FactorType=='Within':
                Within[FactorName]=FactorData
                WithinName.append(FactorName)
            elif FactorType=='Subject':
                Subject=FactorData
        # Extract all within subject possibilities using subject 1
        # transform Dict into matrix easy to use
        self.Within=np.array(Within.values())
        WithinCombi=Within[:,Subject==1].T
        self.Between=np.array(Between.values())
        # extracting different levels for each Between Subject factor
        LevelsBetween=self.Between.max(axis=1)
        # cacluate all possible Combination using the max number of levels
        AllCombinationBetween=itertools.product(range(1,LevelsBetween.max()+1),repeat=len(LevelsBetween))
        # reduce combination with only existing one 
        ExistingCombi=[]
        for c in AllCombinationBetween:
            Combi=np.array(c)
            if (LevelsBetween-Combi<0).sum()==0: # existing combination
                ExistingCombi.append(Combi)
        ExistingCombi=np.array(ExistingCombi)
        BetweenCombi=ExistingCombi
        AllCombiBool={}
        CondName=[]
        # create all arrangement and extract the booleaan coresponding to the arrangement
        # us a Ductionary that containe bool value correcponding to the condition
        # the key of the dictionary correspond to the arrangement 
        for b in BetweenCombi:
            BoolBetween=[]
            NameBetweentmp=[]
            for c,l in enumerate(b):
                BoolBetween.append(Between[c,:]==l)
                NameBetweentmp.append("-".join([BetweenName[c],str(int(l))]))
            BoolBetween=np.array(BoolBetween)
            for w in WithinCombi:
                BoolWithin=[]
                NameWithintmp=[]
                for c,l in enumerate(w):
                    BoolWithin.append(Within[c,:]==l)
                    NameWithintmp.append("-".join([WithinName[c],str(int(l))]))
                BoolWithin=np.array(BoolWithin)
                Bool=np.append(BoolBetween,BoolWithin,axis=0)
                # name of the arrangement
                Nametmp=".".join([".".join(NameBetweentmp),".".join(NameWithintmp)])
                CondName.append(Nametmp)
                AllCombiBool[NameTmp]=Bool.prod(axis=0)==1
        #Creation of all the combination with the 2 arrangements for the t-test
        AllCombiName=itertools.combinations(CondName,2)
        # number of test using combinatory calculation use for the progression bar
        sefl.Nbtest=int(np.math.factorial(len(CondName))/(np.math.factorial(len(CondName)-2)*np.math.factorial(2)))
        # Keep subject Factor to determine if it will be paired on un paired t-test
        self.Subject=Subject
        # Dictionary of boolean correcponding to alla arangement
        self.Arrangement=AllCombiBool
        # all combinasion of T-test 2 by 2
        self.Combi=AllCombiName
    def CalculationTTest(Data,Combination,SubjectFactor,Arrangement,NonParam=False):
        # H5 array don't be acces with bool
        Cond=np.arange(0,Data.shape[1])
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
                t,p=stats.ttest_rel(Data[:,C1Boot],Data[:,C2Boot],axis=1)
                
            else:
                t,p=stats.ttest_rel(Data[:,Cond[Value1]],Data[:,Cond[Value2]],axis=1)
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
                
                t,p=stats.ttest_ind(Data[:,C1Boot],Data[:,C2Boot],axis=1)
            else:
               t,p=stats.ttest_ind(Data[:,Cond[Value1]],Data[:,Cond[Value2]],axis=1)
        return t,p

    def Param(self, DataGFP=False):
        # Extracting GFP or All Data
        if DataGFP:
            Data=self.file.getNode('/Data/GFP')
            ShapeOriginalData=self.file.getNode('/Shape').read()
            Res=self.file.getNode('/Result/GFP/PostHoc')
            ShapeOriginalData[1]=1
        else:
            Data=self.file.getNode('/Data/All')
            ShapeOriginalData=self.file.getNode('/Shape').read()
            Res=self.file.getNode('/Result/All/PostHoc')
        dlg = wx.ProgressDialog('Parametric T-test',
                                "/".join(['PostHoc T-Test : 0',
                                          str(sefl.Nbtest)]),
                                NbTest,
                                parent=self.Parent,
                                style=wx.PD_CAN_ABORT |
                                wx.PD_AUTO_HIDE | wx.PD_REMAINING_TIME | wx.PD_ELAPSED_TIME)
        dlg.SetSize((200, 175))
        n=0
        NewRow=Res.row
        for Combination in self.Combi:
            t,p=CalculationTTest(Data,Combination,self.Subject,self.Arrangement)
            # Reshaping Data
            t=t.reshape((ShapeOriginalData[0], ShapeOriginalData[1]))
            p=p.reshape((ShapeOriginalData[0], ShapeOriginalData[1]))
            # Saving Result into the H5
            NewRow['Name']=Combination
            NewRow['P']=p
            NewRow['T']=t
            NewRow.append()
            # update the remaing time dilog box
            
            n+=1
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

        self.elapsedTime = str(dlg.GetChildren()[3].Label)

        dlg.Close()
        dlg.Destroy()

    def NonParam(self, Iter, DataGFP=False):
         # Extracting GFP or All Data
        if DataGFP:
            Data=self.file.getNode('/Data/GFP')
            ShapeOriginalData=self.file.getNode('/Shape').read()
            Res=self.file.getNode('/Result/GFP/PostHoc')
            ShapeOriginalData[1]=1
        else:
            Data=self.file.getNode('/Data/All')
            ShapeOriginalData=self.file.getNode('/Shape').read()
            Res=self.file.getNode('/Result/All/PostHoc')
        dlg = wx.ProgressDialog('Parametric T-test',
                                "/".join(['PostHoc T-Test : 0',
                                          str(sefl.Nbtest)]),
                                NbTest,
                                parent=self.Parent,
                                style=wx.PD_CAN_ABORT |
                                wx.PD_AUTO_HIDE | wx.PD_REMAINING_TIME | wx.PD_ELAPSED_TIME)
        dlg.SetSize((200, 175))
        n=0
        NewRow=Res.row
        
        for Combination in self.Combi:
            t,p=CalculationTTest(Data,Combination,self.Subject,self.Arrangement)
            TReal=t
            Count=np.zeros(TReal.shape)
            for i in range(Iter):
                t,p=CalculationTTest(Data,Combination,self.Subject,self.Arrangement,NonParam=True)
                TBoot=t
                Diff=TBoot-TReal
                Count[Diff>0]+=1
            p=Count/flot(Iter)
            # Reshaping Data
            t=TReal.reshape((ShapeOriginalData[0], ShapeOriginalData[1]))
            p=p.reshape((ShapeOriginalData[0], ShapeOriginalData[1]))
            # Saving Result into the H5
            NewRow['Name']=Combination
            NewRow['P']=p
            NewRow['T']=t
            NewRow.append()
            # update the remaing time dilog box
            
            n+=1
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
        dlg.Close()
        dlg.Destroy()
