import numpy as np
import tables
import wx
import os as pwd
import scipy.stats
#Stat=scipy.stats.ttest_ind(DataAppris,DataNonAppris,axis=0)# unpaired
#Stat=scipy.stats.ttest_rel(DataAppris,DataNonAppris,axis=0) # paired
###Class de traitement des test multiple.


##        /Result/Anova/All/P # P value for All electrodes and IS
##        /Result/Anova/All/F # F value only in parametric
##        /Result/Anova/GFP/P # P value for GFP
##        /Result/Anova/GFP/F # F value only in parametric
##        /Result/PostHoc/All/P # P value for All electrodes and IS
##        /Result/PostHoc/All/F # F value only in parametric
##        /Result/PostHoc/GFP/P # P value for GFP
##        /Result/PostHoc/GFP/F # F value only in parametric
class Data:
    def __init__(self,H5,parent,Anova=True,DataGFP=False, Param=True):
        self.parent=parent
        self.file=tables.openFile(H5,mode='r+')
        text=['/Result/']
        if Anova:
            text.append('Anova/')
        else:
            text.append('PostHoc/')
            
        if DataGFP:
            text.append('GFP/')
            shape=self.file.getNode('/Info/ShapeGFP')
        else:
            shape=self.file.getNode('/Info/Shape')
            text.append('All/')
        self.shape=shape.read()
        for node in self.file.listNodes("".join(text)):
            if node.name=='Mask':
                self.file.removeNode("".join(["".join(text),'/Mask']))
        self.Mask=self.file.createEArray("".join(text),'Mask',tables.Float64Atom(),(shape[0],shape[1],0))
        text.append('P')
        self.P=self.file.getNode("".join(text))
        if len(self.P.read().shape)>1:
            self.NbTerms=self.P.read().shape[1]
        else:
            self.NbTerms=1
        # P Data before multiple test treatement
        text.remove('P')
        if Anova:
            text.append('F')
        else:
            text.append('T')
        self.F=self.file.getNode("".join(text))
        if Anova:
            if DataGFP:
                Terms=self.file.getNode('/Result/Anova/GFP/Terms')
            else:
                Terms=self.file.getNode('/Result/Anova/All/Terms')
        else:
            if DataGFP:
                Terms=self.file.getNode('/Result/PostHoc/GFP/Terms')
            else:
                Terms=self.file.getNode('/Result/PostHoc/All/Terms')
        self.Terms=Terms.read()
        self.Param=Param
        self.Anova=Anova
        self.GFP=DataGFP
       


        
    def MathematicalMorphology(self,alpha,TF=1,SpaceCriteria=1,SpaceFile=None):
        #Erosition suivit de dilatation = ouverture
        
        if self.shape[0]==1:# test nnumber of time frame
            TF=1
        if self.shape[1]==1:# test number of space point
            SpaceCriteria=1
        if SpaceFile != None:
            self.MatrixDist(SpaceFile)
            Distance=self.Distance
        if TF ==1 and SpaceCriteria==1: # aucun crtitere
            for i in range(self.NbTerms):
                P=np.zeros((self.shape[0],self.shape[1]))
                P=self.P.read()[:,i].reshape((self.shape[0],self.shape[1]))
                Data=np.zeros(P.shape)
                Mask=np.zeros((self.shape[0],self.shape[1],1))
                Data[P<alpha]=1
                Mask[:,:,0]=Data
                self.Mask.append(Mask)
        else: # morphologie mathematique
            if SpaceCriteria==1:# time criteria only
                NbCaclul=(self.NbTerms*self.shape[0]*2)
                dlg=wx.ProgressDialog('Multiple Test Correction','Calculation in progress : 0 %',NbCaclul,parent=self.parent,style=wx.PD_AUTO_HIDE|wx.PD_REMAINING_TIME)
                dlg.SetSize((200,130))
                TimeStart=(TF-1)/2
                TimeEnd=TF-TimeStart
                n=0
                for i in range(self.NbTerms):
                        P=np.zeros((self.shape[0],self.shape[1]))
                        P=self.P.read()[:,i].reshape((self.shape[0],self.shape[1]))
                        Data=np.zeros(P.shape)
                        Mask=np.zeros((self.shape[0],self.shape[1],1))
                        Data[P<alpha]=1
                        # erosion
                        if Data.sum()!=0:
                            for time in range(Data.shape[0]):
                                BeginTime=time-TimeStart
                                EndTime=time+TimeEnd
                                if BeginTime <0:
                                    BeginTime=0
                                    EndTime=TF
                                elif EndTime>Data.shape[0]:
                                    BeginTime=Data.shape[0]-TF
                                    EndTime=Data.shape[0]
                                element=Data[BeginTime:EndTime,:]
                                NbElement=np.array(element.shape[0])
                                Mask[time,element.sum(0)==NbElement,0]=1
                                n+=1
                                pourcent=str(100.0*(n)/(NbCaclul))
                                pourcent=pourcent[0:pourcent.find('.')+3]
                                dlg.Update(n," ".join(['Progression  :',pourcent,' %']))
                                
                        #dilataion
                        Data=Mask[:,:,0]
                        Mask=np.zeros((self.shape[0],self.shape[1],1))
                        if Data.sum()!=0:
                            for time in range(Data.shape[0]):
                                BeginTime=time-TimeStart
                                EndTime=time+TimeEnd
                                if BeginTime <0:
                                    BeginTime=0
                                    EndTime=TF
                                elif EndTime>Data.shape[0]:
                                    BeginTime=Data.shape[0]-TF
                                    EndTime=Data.shape[0]
                                element=Data[BeginTime:EndTime,:]
                                NbElement=np.array(element.shape).prod()
                                Mask[time,element.sum(0)!=0,0]=1
                                n+=1
                                pourcent=str(100.0*(n)/(NbCaclul))
                                pourcent=pourcent[0:pourcent.find('.')+3]
                                dlg.Update(n," ".join(['Progression  :',pourcent,' %']))
                        self.Mask.append(Mask)
                        

            ### sapcial criterai only
            elif TF==1:
                NbCaclul=(self.NbTerms*self.shape[1]*2)
                dlg=wx.ProgressDialog('Multiple Test Correction','Calculation in progress : 0 %',NbCaclul,parent=self.parent,style=wx.PD_AUTO_HIDE|wx.PD_REMAINING_TIME)
                dlg.SetSize((200,130))
                n=0
                for i in range(self.NbTerms):
                        P=np.zeros((self.shape[0],self.shape[1]))
                        P=self.P.read()[:,i].reshape((self.shape[0],self.shape[1]))
                        Data=np.zeros(P.shape)
                        Mask=np.zeros((self.shape[0],self.shape[1],1))
                        Data[P<alpha]=1
                        # erosion
                        if Data.sum()!=0:
                            for dim in range(Data.shape[1]):
                                space=Distance[dim,:]
                                space=space.argsort()
                                space=space[0:SpaceCriteria]
                                element=Data[:,space]
                                Mask[element.sum(1)==SpaceCriteria,dim,0]=1
                                n+=1
                                pourcent=str(100.0*(n)/(NbCaclul))
                                pourcent=pourcent[0:pourcent.find('.')+3]
                                dlg.Update(n," ".join(['Progression  :',pourcent,' %']))
                        #dilataion
                        Data=Mask[:,:,0]
                        Mask=np.zeros((self.shape[0],self.shape[1],1))
                        if Data.sum()!=0:
                            for dim in range(Data.shape[1]):
                                space=Distance[dim,:]
                                space=space.argsort()
                                space=space[0:SpaceCriteria]
                                element=Data[:,space]
                                NbElement=np.array(element.shape[0])
                                Mask[element.sum(1)!=0,dim,0]=1
                                n+=1
                                pourcent=str(100.0*(n)/(NbCaclul))
                                pourcent=pourcent[0:pourcent.find('.')+3]
                                dlg.Update(n," ".join(['Progression  :',pourcent,' %']))
                        self.Mask.append(Mask)
            else:
                NbCaclul=(self.NbTerms*self.shape[1]*self.shape[0]*2)
                dlg=wx.ProgressDialog('Multiple Test Correction','Calculation in progress : 0 %',NbCaclul,parent=self.parent,style=wx.PD_AUTO_HIDE|wx.PD_REMAINING_TIME)
                dlg.SetSize((200,130))
                n=0
                TimeStart=(TF-1)/2
                TimeEnd=TF-TimeStart
                for i in range(self.NbTerms):
                    P=np.zeros((self.shape[0],self.shape[1]))
                    P=self.P.read()[:,i].reshape((self.shape[0],self.shape[1]))
                    Data=np.zeros(P.shape)
                    Mask=np.zeros((self.shape[0],self.shape[1],1))
                    Data[P<alpha]=1
                    # erosion
                    if Data.sum()!=0:
                        for time in range(Data.shape[0]):
                            for dim in range(Data.shape[1]):
                                BeginTime=time-TimeStart
                                EndTime=time+TimeEnd
                                if BeginTime <0:
                                    BeginTime=0
                                    EndTime=TF
                                elif EndTime>Data.shape[0]:
                                    BeginTime=Data.shape[0]-TF
                                    EndTime=Data.shape[0]
                                space=Distance[dim,:]
                                space=space.argsort()
                                space=space[0:SpaceCriteria]
                                element=Data[BeginTime:EndTime,space]
                                NbElement=np.array(element.shape).prod()
                                if NbElement==element.sum():
                                    Mask[time,dim,0]=1
                                n+=1
                                pourcent=str(100.0*(n)/(NbCaclul))
                                pourcent=pourcent[0:pourcent.find('.')+3]
                                dlg.Update(n," ".join(['Progression  :',pourcent,' %']))
                    # dilatation
                    Data=Mask[:,:,0]
                    Mask=np.zeros((self.shape[0],self.shape[1],1))
                    if Data.sum()!=0:
                        for time in range(Data.shape[0]):
                            for dim in range(Data.shape[1]):
                                BeginTime=time-TimeStart
                                EndTime=time+TimeEnd
                                if BeginTime <0:
                                    BeginTime=0
                                elif EndTime>Data.shape[0]:
                                    EndTime=Data.shape[0]
                                space=Distance[dim,:]
                                space=space.argsort()
                                space=space[0:SpaceCriteria]
                                element=Data[BeginTime:EndTime,space]
                                if element.sum()!=0:
                                     Mask[time,dim,0]=1
                                n+=1
                                pourcent=str(100.0*(n)/(NbCaclul))
                                pourcent=pourcent[0:pourcent.find('.')+3]
                                dlg.Update(n," ".join(['Progression  :',pourcent,' %']))
                    self.Mask.append(Mask)
            dlg.Close()
            dlg.Destroy()
    def WriteIntermediateResult(self,ResultFolder,DataGFP=False):
        ##################################################################
        #Write Estimator, not real slope and real mean depending on design
        ##################################################################
        
        ######################
        #Create result Folder
        ######################
        IntermediateResultPath="\\".join([ResultFolder,'ItermediateResult'])
        try:
            pwd.mkdir(IntermediateResultPath)
        except:
            pass
        IntermediateResults=self.file.listNodes('/Result/IntermediateResult/')
        if IntermediateResults==[]:
            if DataGFP:
                CoefTerms=self.file.getNode('/Result/Anova/GFP/CoefTerms')
                CoefTerms=CoefTerms.read()
                CoefValue=self.file.getNode('/Result/Anova/GFP/CoefValue')

            else:
                CoefTerms=self.file.getNode('/Result/Anova/All/CoefTerms')
                CoefTerms=CoefTerms.read()
                CoefValue=self.file.getNode('/Result/Anova/All/CoefValue')

            NameBetween=self.file.getNode('/Names/Between')
            NameBetween=NameBetween.read()
            if NameBetween==False:
                NameBetween=[]
            NameCovariate=self.file.getNode('/Names/Covariate')
            NameCovariate=NameCovariate.read()
            if NameCovariate==False:
                NameCovariate=[]
            NameWithin=self.file.getNode('/Names/Within')
            NameWithin=NameWithin.read()
            if NameWithin==False:
                NameWithin=[]
            Subject=self.file.getNode('/Model/Subject')
            Subject=Subject.read()

            SheetValue=self.file.getNode('/Sheet/Value')
            SheetValue=SheetValue.read()
            NbRow=len(SheetValue[0])


            Between=self.file.getNode('/Model/Between')
            Between=np.array(Between.read())
            Covariate=self.file.getNode('/Model/Covariate')
            Covariate=np.array(Covariate.read())
            Within=self.file.getNode('/Model/Within')
            Within=Within.read()

            ################################
            # Write real Mean and Real slope
            ################################
            
           
           
            Covariate=self.file.getNode('/Model/Covariate')
            Covariate=np.array(Covariate.read())
            
            ###################################
            # Simple Regression only Covariate
            ###################################
            
            if NameWithin == [] and NameBetween==[]:
                # Extracting Data
                Data=[]
                for s in Subject:
                    if DataGFP:
                            text=['/DataGFP/Subject',str(int(s-1)),'/Condition0']
                            DataTmp=self.file.getNode("".join(text))
                            DataTmp=DataTmp.read()
                            Data.append(DataTmp)
                            EphFile=['GFP-Level']
                    else:
                            text=['/Data/Subject',str(int(s-1)),'/Condition0']
                            DataTmp=self.file.getNode("".join(text))
                            DataTmp=DataTmp.read()
                            Data.append(DataTmp)
                            if self.shape[1]<500:
                                EphFile=['WaveForm-Level']
                            else:
                                EphFile=['BrainSpace-Level']
                Data=np.array(Data)

                # Caclulate slope for all covariate terms
                CovData=['Cov']
                if len(Covariate.shape)==1:
                    Covariate=Covariate.reshape((Covariate.shape[0],1))
                    
                for j,cov in enumerate(NameCovariate):
                    CovariateTmp=Covariate[:,j]
                    CovariateTmp=np.vstack([CovariateTmp.T, np.ones(len(CovariateTmp))]).T
                    Shape=list(Data.shape)
                    Shape=np.array(Shape[1:len(Shape)])
                    DataCov=Data.reshape((Data.shape[0],Shape.prod()))
                    Slope,intercept=np.linalg.lstsq(CovariateTmp,DataCov)[0]
                    Slope=Slope.reshape(tuple(Shape))
                    RTmp=[]
                    print(CovariateTmp[:,0])
                    print(DataCov[:,161])
                    for t in DataCov.T:
                            RTmp.append(np.corrcoef(CovariateTmp[:,0],t)[0,1])
                    test=np.corrcoef(CovariateTmp[:,0],DataCov[:,161])
                    print(test)
                    print(RTmp[161])
                    CovData.append(str(j))
                    SlopeGroup=self.file.createGroup('/Result/IntermediateResult/',"".join(CovData))
                    tmp=CovData.pop(-1)
                    EphFile.append('txt')
                    EphFile.append(cov)
                    NameFile=self.file.createArray(SlopeGroup,'Name',EphFile)
                    tmp=EphFile.pop(-1)
##                    SlopeData=self.file.createArray(SlopeGroup,'Slope',tables.Float64Atom(),(self.shape[0],self.shape[1],0))
##                    R=self.file.createArray(SlopeGroup,'R',tables.Float64Atom(),(self.shape[0],self.shape[1],0))
                    RTmp=np.array(RTmp)
                    RTmp=RTmp.reshape((self.shape[0],self.shape[1]))
                    Slope=Slope.reshape((self.shape[0],self.shape[1]))
                    Slope=self.file.createArray(SlopeGroup,'Slope',Slope)
                    R=self.file.createArray(SlopeGroup,'R',RTmp)
##                    R.append(RTmp)
##                    SlopeData.append(Slope)
            #########################################################
            # Within/Between Subject Factor and or not and covariate
            #########################################################
            else:

                
                LevelWithin=self.file.getNode('/Info/Level')
                LevelWithin=LevelWithin.read()
                LevelWithin=np.array(LevelWithin)
                if LevelWithin.any():
                    NbConditionWithin=LevelWithin.prod()
                else:
                    NbConditionWithin=1
                    
                
                if len(Subject.shape)==1:
                    Subject=Subject.reshape((Subject.shape[0],1))
                NbSubject=int(Subject.max())
                if NbSubject!=NbRow:
                    NbSubject=NbRow
                
                # No WithinSubject Factors

                if NameWithin !=[]:
                    ConditionNumber=np.array([])
                    for i in range(NbConditionWithin):
                        tmp=np.ones((NbSubject))
                        tmp=tmp*(i+1)
                        ConditionNumber=np.concatenate((ConditionNumber,tmp))
                    ConditionNumber=ConditionNumber.reshape((ConditionNumber.shape[0],1))
                # their is at list one withinsubject factor
                else:
                    ConditionNumber=np.ones((NbSubject))
                # if their is only one between subject factor transfomring into 2d matrix
                if len(Between.shape)==1:
                    Between=Between.reshape((Between.shape[0],1))
                # if their is only one Covariate factor transfomring into 2d matrix 
                if len(Covariate.shape)==1:
                    Covariate=Covariate.reshape((Covariate.shape[0],1))
               

                fs=self.file.getNode('/Info/FS')
                fs=fs.read()
                #################################################################################
                #Generating Varaible named with Within and Between subject name and their levels
                #################################################################################
                ConditionTxt=[]
                Level=[]
                
                for i,w in enumerate(NameWithin):
                    try:
                        NbLevel=int(Within[:,i].max())
                    except:
                        NbLevel=int(Within.max())
                    Level.append(NbLevel)
                    for j in range(NbLevel):
                        text=[w,str(j+1),'=0']
                        exec("".join(text))
                    ConditionTxt.append(w)
                for i,w in enumerate(NameBetween):
                    try:
                        NbLevel=int(Between[:,i].max())
                    except:
                        NbLevel=int(Between.max())
                    Cond=[]
                    Level.append(NbLevel)
                    for j in range(NbLevel):
                        text=[w,str(j+1),'=0']
                        exec("".join(text))
                    ConditionTxt.append(w)
                Level=np.array(Level)
                ##############################################################
                #Generating all combinaison between and within subject factors
                ##############################################################
                NbCondition=Level.prod()
                Combinaison=np.zeros((NbCondition,len(Level)))
                for k,i in enumerate(Level):
                    repet=NbCondition/i
                    NbCondition=repet
                    for j in range(i):
                        fact=np.ones((repet,1))*j+1
                        debut=j*repet
                        fin=(j+1)*repet
                        Combinaison[debut:fin,k]=fact[:,0]
                    n=j
                    while Combinaison[Level.prod()-1,k]==0:
                            for j in range(i):
                                n+=1
                                fact=np.ones((repet,1))*j+1
                                debut=n*repet
                                fin=(n+1)*repet
                                Combinaison[debut:fin,k]=fact[:,0]
                #no within subject subject factor
                if NameWithin==[]:
                    Condition=Between
                #No between subject factor
                elif NameBetween==[]:
                    Condition=Within
                else:
                    Condition=np.concatenate((Within,Between),axis=1)
                #####################################
                #Extracting Data for each Combinaison 
                #####################################
                if DataGFP:
                    shape=self.file.getNode('/Info/ShapeGFP')
                    shape=shape.read()
                    shape=(shape[0],1)
                else:
                    shape=self.file.getNode('/Info/Shape')
                    shape=shape.read()
                    shape=(shape[0],shape[1])
                Moyenne=np.zeros(shape)
                SE=np.zeros(shape)
               #/Result/IntermediateResult/{FileName}
                n=0
                InterceptData=['Intercept']
                CovData=['Cov']
                for c in Combinaison:
                    InterceptData=['Intercept']
                    CovData=['Cov']
                    tmp=(Condition==c).sum(axis=1)==len(c)
                    SubjectTmp=Subject[tmp]
                    ConditionTmp=ConditionNumber[tmp]
                    InterceptData.append(str(n))
                    CovData.append(str(n))
                    n+=1
                    self.CaluclatingIntercept(InterceptData,DataGFP,SubjectTmp,ConditionTmp,ConditionTxt,c,Subject)
                    ####
                    #Covariate
                    ####
                    for j,cov in enumerate(NameCovariate):
                        EphFile=self.file.getNode("/".join(['/Result/IntermediateResult/',"".join(InterceptData),'Name']))
                        EphFile=EphFile.read()
                        EphFile.append(cov)
                        CovData.append(str(j))
                        self.CalculatingSlope(CovData,SubjectTmp,ConditionTmp,j,EphFile,DataGFP,Covariate,tmp)
                        tmp=CovData.pop(-1)
        IntermediateResults=self.file.listNodes('/Result/IntermediateResult/')
        for i in IntermediateResults:
            Name=i.Name.read()
            Name.append('eph')
            Name=".".join(Name)
            IntTest=str(i)
            IntTest=IntTest.find('Intercept')
            if IntTest==-1:# covarience Data
                Slope=i.Slope.read()
                self.WriteEphFile("/".join([IntermediateResultPath,Name.replace('txt','Slope')]),Slope)
                R=i.R.read()
                self.WriteEphFile("/".join([IntermediateResultPath,Name.replace('txt','R')]),R)
            else: # intercept data
                MeanData=i.Mean.read()
                self.WriteEphFile("/".join([IntermediateResultPath,Name.replace('txt','Mean')]),MeanData)
                SE=i.SE.read()
                self.WriteEphFile("/".join([IntermediateResultPath,Name.replace('txt','SE')]),SE)
        # Remove GFP and WaveForm keep only if IS that is long to calculate
        if self.shape[1]<500 or DataGFP:
            try:
                self.file.removeNode('/Result/IntermediateResult/',recursive=True)
                self.file.createGroup('/Result/','IntermediateResult')
            except:
                pass
    def WriteEphFile(self,PathName,Data):
        fichier=open(PathName,"w")
        # on prend le header
        fs=self.file.getNode('/Info/FS')
        fs=fs.read()
        shape=Data.shape
        header=[str(int(shape[1])),'\t',str(int(shape[0])),'\t',str(int(fs)),'\n']
        #ecrtiture du header
        fichier.write("".join(header))
        # boucle sur les time chaque ligne est un temps
        for time in Data:
        #ecriture ligne par ligne
                time.tofile(fichier,sep="\t",format="%s")
                #saut de ligne
                fichier.write("\n")
        fichier.close()
                    
    def ReadingData(self,SubjectTmp,ConditionTmp,t,DataGFP):
        Data=[]
        for i,s in enumerate(SubjectTmp):
            if DataGFP:
                text=['/DataGFP/Subject',str(int(s-1)),'/Condition',str(int(ConditionTmp[i]-1))]
                DataTmp=self.file.getNode("".join(text))
                if self.shape[0]==1:
                    Data.append(DataTmp.read())
                else:
                    Data.append(DataTmp.read()[t])
            else:  
                text=['/Data/Subject',str(int(s-1)),'/Condition',str(int(ConditionTmp[i]-1))]
                DataTmp=self.file.getNode("".join(text))
                if self.shape[0]==1:
                    Data.append(DataTmp.read())
                else:
                    Data.append(DataTmp.read()[t,:])
        self.Data=np.array(Data)

        
    def CaluclatingIntercept(self,GroupName,DataGFP,SubjectTmp,ConditionTmp,ConditionTxt,Combinaison,Subject):
        if DataGFP:
            EphFile=['GFP-Level']
        else:
            if self.shape[1]<500:
                EphFile=['WaveForm-Level']
            else:
                EphFile=['BrainSpace-Level']
        EphFile.append('txt')
        for i,combi in enumerate(Combinaison):
            txt=[ConditionTxt[i],str(int(combi))]
            EphFile.append("-".join(txt))
        InterceptGroup=self.file.createGroup('/Result/IntermediateResult/',"".join(GroupName))
        NameFile=self.file.createArray(InterceptGroup,'Name',EphFile)
        MeanData=self.file.createEArray(InterceptGroup,'Mean',tables.Float64Atom(),(0,self.shape[1]))
        SE=self.file.createEArray(InterceptGroup,'SE',tables.Float64Atom(),(0,self.shape[1]))
        for t in range(self.shape[0]):
            self.ReadingData(SubjectTmp,ConditionTmp,t,DataGFP)
            MeanTmp=self.Data.mean(axis=0)
            # problem due to Gmean GFP have only one value
            if MeanTmp.shape==():
                MeanTmp=np.array([MeanTmp])
                MeanTmp=MeanTmp.reshape((1,len(MeanTmp)))
            if len(MeanTmp.shape)==1:
                MeanTmp=MeanTmp.reshape((1,self.shape[1]))
            MeanData.append(MeanTmp)
            SETmp=self.Data.std(axis=0)/np.sqrt(len(Subject))
            if SETmp.shape==():
               SETmp=np.array([SETmp])
            if len(SETmp.shape)==1:
                SETmp=SETmp.reshape((1,len(SETmp)))
            SE.append(SETmp)

            
    def CalculatingSlope(self,GroupName,SubjectTmp,ConditionTmp,CovLabel,EphFile,DataGFP,Covariate,tmp):
        
        SlopeGroup=self.file.createGroup('/Result/IntermediateResult/',"".join(GroupName))
        NameFile=self.file.createArray(SlopeGroup,'Name',EphFile)
        SlopeData=self.file.createEArray( SlopeGroup,'Slope',tables.Float64Atom(),(0,self.shape[1]))
        R=self.file.createEArray( SlopeGroup,'R',tables.Float64Atom(),(0,self.shape[1]))
        for t in range(self.shape[0]):
            self.ReadingData(SubjectTmp,ConditionTmp,t,DataGFP)
            CovariateTmp=Covariate[tmp,CovLabel]
            CovariateTmp=np.vstack([CovariateTmp.T, np.ones(len(CovariateTmp))]).T
            Shape=list(self.Data.shape)
            Shape=np.array(Shape[1:len(Shape)])
            DataCov=self.Data.reshape((int(self.Data.shape[0]),int(Shape.prod())))
            SlopeTmp,intercept=np.linalg.lstsq(CovariateTmp,DataCov)[0]
            SlopeTmp=SlopeTmp.reshape((1,len(SlopeTmp)))
            RTmp=[]
            for t in DataCov.T:
                RTmp.append(np.corrcoef(CovariateTmp[:,0],t)[0,1])
            RTmp=np.array(RTmp)
            RTmp=RTmp.reshape((1,len(RTmp)))     
            R.append(np.array(RTmp))
            SlopeData.append(SlopeTmp)


            
    def WriteData(self,ResultFolder):
        #Ecrire les resultats en Eph
        """ ecritrue de l'eph : 
        nom de l'eph = name_eph  
        path de l'eph = path_result"""
        OutPutFiles=[]
        pwd.chdir(ResultFolder)
        if self.Anova:
            for i,Terms in enumerate(self.Terms):
                if self.GFP:
                    FileNameP=['GFP-Data']
                    FileNameF=['GFP-Data']
                else:
                    if self.shape[1]<500:
                        FileNameP=['WaveForm-Data']
                        FileNameF=['WaveForm-Data']
                    else:
                        FileNameP=['BrainSpace-Data']
                        FileNameF=['BrainSpace-Data']
                if self.Param:
                    FileNameP.append('Param')
                    FileNameF.append('Param')
                else:
                    FileNameP.append('Non-Param')
                    FileNameF.append('Non-Param')
                    
                if Terms.find(':')!=-1:# term interaction
                    FileNameP.append('Interaction')
                    FileNameP.append(Terms.replace(':','-'))
                    FileNameP.append('P')
                    FileNameP.append('eph')
                    FileNameF.append('Interaction')
                    FileNameF.append(Terms.replace(':','-'))
                    FileNameF.append('F')
                    FileNameF.append('eph')

                else: # main effect
                    FileNameP.append('Main Effect')
                    FileNameP.append(Terms)
                    FileNameP.append('P')
                    FileNameP.append('eph')
                    FileNameF.append('Main Effect')
                    FileNameF.append(Terms)
                    FileNameF.append('F')
                    FileNameF.append('eph')
                #creation du fichier P
                OutPutFiles.append(FileNameP)
                if len(".".join(FileNameP))+len(ResultFolder)>256:
                    txt=" ".join(['Path is too long for',".".join(FileNameP),'File it will be not write'])
                    dlg = wx.MessageDialog(None,txt,"Error",style = wx.OK|wx.ICON_INFORMATION)
                    retour = dlg.ShowModal()
                    dlg.Destroy()
                else:
                    fichier=open(".".join(FileNameP),"w")
                    fs=self.file.getNode('/Info/FS')
                    fs=fs.read()
                    # on prend le header
                    header=[str(int(self.shape[1])),'\t',str(int(self.shape[0])),'\t',str(int(fs)),'\n']
                    #ecrtiture du header
                    fichier.write("".join(header))
                    # boucle sur les time chaque ligne est un temps
                    Raw=np.zeros((self.shape[0],self.shape[1]))
                    Raw=self.P.read()[:,i].reshape((self.shape[0],self.shape[1]))
                    Raw=1-Raw
                    Data=Raw*self.Mask[:,:,i]
                    for time in Data:
                            #ecriture ligne par ligne
                            time.tofile(fichier,sep="\t",format="%s")
                            #saut de ligne
                            fichier.write("\n")
                    fichier.close()

                    #creation du fichier F
                    OutPutFiles.append(FileNameF)
                    fichier=open(".".join(FileNameF),"w")
                    fs=self.file.getNode('/Info/FS')
                    fs=fs.read()
                    # on prend le header
                    header=[str(int(self.shape[1])),'\t',str(int(self.shape[0])),'\t',str(int(fs)),'\n']
                    #ecrtiture du header
                    fichier.write("".join(header))
                    # boucle sur les time chaque ligne est un temps
                    Raw=self.F.read()[:,i].reshape((self.shape[0],self.shape[1]))
                    Data=Raw*self.Mask[:,:,i]
                    for time in Data:
                            #ecriture ligne par ligne
                            time.tofile(fichier,sep="\t",format="%s")
                            #saut de ligne
                            fichier.write("\n")
                    fichier.close()
        else:
            # write Post-Hoc File
            
            for i,Terms in enumerate(self.Terms):
                if self.GFP:
                    FileNameP=['GFP-Data']
                    FileNameT=['GFP-Data']
                else:
                    if self.shape[1]<500:
                        FileNameP=['WaveForm-Data']
                        FileNameT=['WaveForm-Data']
                    else:
                        FileNameP=['BrainSpace-Data']
                        FileNameT=['BrainSpace-Data']
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

                #creation du fichier P
                OutPutFiles.append(FileNameP)
                if len(".".join(FileNameP))+len(ResultFolder)>256:
                    txt=" ".join(['Path is too long for',".".join(FileNameP),'File it will be not write'])
                    dlg = wx.MessageDialog(None,txt,"Error",style = wx.OK|wx.ICON_INFORMATION)
                    retour = dlg.ShowModal()
                    dlg.Destroy() 
                else:
                    fichier=open(".".join(FileNameP),"w")
                    fs=self.file.getNode('/Info/FS')
                    fs=fs.read()
                    # on prend le header
                    header=[str(int(self.shape[1])),'\t',str(int(self.shape[0])),'\t',str(int(fs)),'\n']
                    #ecrtiture du header
                    fichier.write("".join(header))
                    # boucle sur les time chaque ligne est un temps
                    Raw=np.zeros((self.shape[0],self.shape[1]))
                    Raw=self.P.read()[:,i].reshape((self.shape[0],self.shape[1]))
                    Raw=1-Raw
                    Data=Raw*self.Mask[:,:,i]
                    for time in Data:
                            #ecriture ligne par ligne
                            time.tofile(fichier,sep="\t",format="%s")
                            #saut de ligne
                            fichier.write("\n")
                    fichier.close()

                    #creation du fichier F
                    OutPutFiles.append(FileNameT)
                    fichier=open(".".join(FileNameT),"w")
                    fs=self.file.getNode('/Info/FS')
                    fs=fs.read()
                    # on prend le header
                    header=[str(int(self.shape[1])),'\t',str(int(self.shape[0])),'\t',str(int(fs)),'\n']
                    #ecrtiture du header
                    fichier.write("".join(header))
                    # boucle sur les time chaque ligne est un temps
                    Raw=self.F.read()[:,i].reshape((self.shape[0],self.shape[1]))
                    Data=Raw*self.Mask[:,:,i]
                    for time in Data:
                            #ecriture ligne par ligne
                            time.tofile(fichier,sep="\t",format="%s")
                            #saut de ligne
                            fichier.write("\n")
                    fichier.close()
                
        self.OutPutFiles=OutPutFiles
    def MatrixDist(self,file):
        if file.find('.spi')!=-1:
            # un spi file
            tmp=np.loadtxt(file,dtype='string')
            tmp=tmp[:,0:3]
            Coordonnee=np.zeros(tmp.shape)
            for i,row in enumerate(tmp):
                for j,n in enumerate(row):
                    try:
                       Coordonnee[i,j]=float(n)
                    except:
                        pass
        elif file.find('.xyz')!=-1:
            # xyz file
            tmp=np.loadtxt(file,dtype='string', skiprows=1)
            tmp=tmp[:,0:3]
            Coordonnee=np.zeros(tmp.shape)
            for i,row in enumerate(tmp):
                for j,n in enumerate(row):
                    try:
                       Coordonnee[i,j]=float(n)
                    except:
                        pass
        NbPoint=Coordonnee.shape[0]
        MatrixDist=np.zeros((NbPoint,NbPoint))
        for v in range(NbPoint):
            dist=Coordonnee-Coordonnee[v,:]
            dist=dist*dist
            dist=dist.sum(1)
            dist=np.sqrt(dist)
            MatrixDist[v,:]=dist
        self.Distance=MatrixDist
    
