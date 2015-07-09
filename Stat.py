import rpy2.robjects as robjects
import rpy2.robjects.numpy2ri
import numpy as np
from scipy import stats
import tables
import random
import wx
class Anova:
    """ faire une Anova avec en entree Data, le/les vecteur Between,Covariate, Within et Subject ainsi que leur nom respectif"""
    def __init__(self,H5,parent):
        self.Cancel=False
        self.parent=parent
        self.file=tables.openFile(H5,mode='r+')
        # models
        Between=self.file.getNode('/Model/Between')
        Between=np.array(Between.read())
        Covariate=self.file.getNode('/Model/Covariate')
        Covariate=np.array(Covariate.read())
        Within=self.file.getNode('/Model/Within')
        Within=Within.read()
        Subject=self.file.getNode('/Model/Subject')
        Subject=Subject.read()
        # Names
        NameBetween=self.file.getNode('/Names/Between')
        NameBetween=NameBetween.read()
        NameCovariate=self.file.getNode('/Names/Covariate')
        NameCovariate=NameCovariate.read()
        NameWithin=self.file.getNode('/Names/Within')
        NameWithin=NameWithin.read()
        # les data sont (tf, electrodes, cond, sujet) !!!!!
        self.Formule=["DataR~("]
        SubjectR=robjects.r.factor(Subject)
        robjects.globalEnv["Subject"] = SubjectR
        Error=[" + Error(Subject/("]
        
        # on crée les facteurs Within
        if Within.any():
            for i,NameVariable in enumerate(NameWithin):
                if len(Within.shape)==1:
                    text=[NameVariable,'=Within']
                else:
                    text=[NameVariable,'=Within[:,',str(i),']']
                exec("".join(text))
                text=[NameVariable,'=robjects.r.factor(',NameVariable,')']
                exec("".join(text))
                text=['robjects.globalEnv["',NameVariable,'"] = ',NameVariable]
                exec("".join(text))
                self.Formule.append(NameVariable)
                self.Formule.append('*')
                Error.append(NameVariable)
                Error.append('*')
            
        # on crée les factr Between
        if Between.any(): # Between existe
            for i,NameVariable in enumerate(NameBetween):
                if len(Between.shape)==1:
                    text=[NameVariable,'=Between']
                else:
                    text=[NameVariable,'=Between[:,',str(i),']']
                exec("".join(text))
                text=[NameVariable,'=robjects.r.factor(',NameVariable,')']
                exec("".join(text))
                text=['robjects.globalEnv["',NameVariable,'"] = ',NameVariable]
                exec("".join(text))
                self.Formule.append(NameVariable)
                self.Formule.append('*')
        # on crée les factor covariate
        if Covariate.any():
            for i,NameVariable in enumerate(NameCovariate):
                if len(Covariate.shape)==1:
                    text=[NameVariable,'=Covariate']
                else:
                    text=[NameVariable,'=Covariate[:,',str(i),']']
                exec("".join(text))
                text=[NameVariable,'=robjects.FloatVector(',NameVariable,')']
                exec("".join(text))
                text=['robjects.globalEnv["',NameVariable,'"] = ',NameVariable]
                exec("".join(text))
                self.Formule.append(NameVariable)
                self.Formule.append('*')
        if Within.any():
            Error[len(Error)-1]='))'
        else:
            Error=["+Error(Subject)"]
        del self.Formule[len(self.Formule)-1]
        self.Formule.append(')')
        self.Formule.append("".join(Error))
        self.Formule="".join(self.Formule)
        self.Between=Between
        self.Covariate=Covariate
        self.Within=Within
        self.Subject=Subject
        self.NameBetween=NameBetween
        self.NameCovariate=NameCovariate
        self.NameWithin=NameWithin

    def Param(self,DataGFP=False):
        # mise en forme de Data
        if DataGFP:
            shape=self.file.getNode('/Info/ShapeGFP')
        else:
            shape=self.file.getNode('/Info/Shape')
        shape=shape.read()
        NbSujet=shape[3]
        NbCond=shape[2]
        # GFP bool dit on cacul le GFP dans la stat
        NbAnova=int(shape[0]*shape[1])
        Byte=shape.prod()
        Cycle=int(Byte/10000)
        try:
            NbAnovaCycle=NbAnova/Cycle
        except:
            NbAnovaCycle=NbAnova
        #On fait 1 anova pour les terms
        DataAnova=ExtractData(self.file,0,1,DataGFP)
        DataAnova=DataAnova.extract.reshape((NbSujet*NbCond))
        DataR=robjects.RArray(DataAnova.T)
        robjects.globalEnv["DataR"] = DataR
        TextR=['aov(',self.Formule,')']
        express=rpy2.robjects.r.parse(text = "".join(TextR))
        Fit=rpy2.robjects.r.eval(express)
        robjects.globalEnv["Fit"] = Fit
        # calcul Anova
        Raw=robjects.r.summary(Fit)

        #calcul des Terms
        Terms=[]
        ConfundTerm=False
        index=[]
        for i in range(len(Raw)):
            tmp=Raw[i][0]
            tmp=robjects.r.slot(tmp,"row.names")
            tmp=list(tmp)
            del(tmp[len(tmp)-1])
            if i==0:
                if self.NameWithin!=False:
                    for t in tmp:
                        if t.find(self.NameWithin[0])!=-1:
                            ConfundTerm=True
                            break
          
            if ConfundTerm:
                if i==0:
                    Terms.extend(tmp)
                    TermsSubject=tmp
                    rm=range(len(tmp))
                    index.append(rm)
                else:
                    rm=range(len(tmp))
                    for t in TermsSubject:
                        ind=tmp.index(t)
                        rm.remove(ind)
                    for r in rm:
                        Terms.append(tmp[r])
                    index.append(rm)
            else:     
                Terms.extend(tmp)

        for i,t in enumerate(Terms):
            Terms[i]=t[0:t.find(' ')]
        NbTerms=len(Terms)
        self.Terms=Terms
        
        # terms des estimateurs
        coef=robjects.r.coef(Fit)
        coef=list(coef)
        indexCoefTerms=[]
        CoefTermsTmp=[]
        for n,c in enumerate(coef):
            txt=str(c)
            m=0
            ind=[]
            if txt!='numeric(0)':
                    txt=txt.replace('\r\n','')
                    txt=txt.rsplit(' ')
                    for i in txt:
                        if i !='':
                            try:
                                tmp=float(i)
                            except:
                                if ConfundTerm and n>1:
                                    try:
                                        CoefTermsTmp.index(i)
                                        m+=1
                                    except:
                                        CoefTermsTmp.append(i)
                                        ind.append(m)
                                        m+=1
                                else:
                                    CoefTermsTmp.append(i)
                                    ind.append(m)
                                    m+=1
            indexCoefTerms.append(ind)
        CoefTerms=[]
        for i in CoefTermsTmp:
            if i.find('\n')==-1:
                CoefTerms.append(i)
        
        self.CoefTerms=CoefTerms
        NbCoefTerms=len(CoefTerms)
        
        
        
        
        ###
        if DataGFP: #c'est sur le GFP
            ResultP=self.file.createEArray('/Result/Anova/GFP','P',tables.Float64Atom(),(0,NbTerms))
            ResultF=self.file.createEArray('/Result/Anova/GFP','F',tables.Float64Atom(),(0,NbTerms))
            self.file.createArray('/Result/Anova/GFP','Terms',self.Terms)
            self.file.createArray('/Result/Anova/GFP','CoefTerms',CoefTerms)
            CoefValue=self.file.createEArray('/Result/Anova/GFP','CoefValue',tables.Float64Atom(),(0,NbCoefTerms))
        else: # c'est sur toutes les electrodes
            ResultP=self.file.createEArray('/Result/Anova/All','P',tables.Float64Atom(),(0,NbTerms))
            ResultF=self.file.createEArray('/Result/Anova/All','F',tables.Float64Atom(),(0,NbTerms))
            self.file.createArray('/Result/Anova/All','Terms',self.Terms)
            
            self.file.createArray('/Result/Anova/All','CoefTerms',CoefTerms)
            CoefValue=self.file.createEArray('/Result/Anova/All','CoefValue',tables.Float64Atom(),(0,NbCoefTerms))
            
        Df=[]
        # Anova caculation using R
        Maximum=NbAnova
        dlg=wx.ProgressDialog('Parametric Anova','Calculation in progress : 0 %',maximum= Maximum,parent=self.parent,style=wx.PD_CAN_ABORT|wx.PD_AUTO_HIDE|wx.PD_REMAINING_TIME)
        dlg.SetSize((200,175))
        n=0
        fin1=0
        while fin1 < NbAnova:
            debut1=n*NbAnovaCycle
            fin1=(n+1)*NbAnovaCycle
            n+=1
            if fin1>NbAnova:
                fin1=NbAnova
                Data=ExtractData(self.file,debut1,fin1,DataGFP)
                NbAnovaCycle=Data.extract.shape[0]
                Data=Data.extract.reshape((Data.extract.shape[0],NbSujet*NbCond))
            else:
                Data=ExtractData(self.file,debut1,fin1,DataGFP)
                Data=Data.extract.reshape((NbAnovaCycle,NbSujet*NbCond))
                

            DataSize=Data.shape
            # on transpose pour R
            DataR=robjects.RArray(Data.T)
            robjects.globalEnv["DataR"] = DataR
            TextR=['aov(',self.Formule,')']
            express=rpy2.robjects.r.parse(text = "".join(TextR))
            Fit=rpy2.robjects.r.eval(express)
            robjects.globalEnv["Fit"] = Fit
            # calcul Anova
            Raw=robjects.r.summary(Fit)
            Raw=list(Raw)
            # estimateurs
            coef=robjects.r.coef(Fit)
            coef=list(coef)
            CoefValueTmp=np.zeros((NbAnovaCycle,NbCoefTerms))
            debut=0
            for i,c in enumerate(coef):
                nbterms=len(c)/NbAnovaCycle
                tmp=np.array(c)
                tmp=tmp.reshape((NbAnovaCycle,nbterms))
                if ConfundTerm:
                    tmp=tmp[:,indexCoefTerms[i]]
                    nbterms=len(indexCoefTerms[i])
                fin=debut+nbterms
                CoefValueTmp[:,debut:fin]=tmp  
                debut=fin
                
            # extraction de P,f, DF
            P=np.zeros((DataSize[0],NbTerms))
            F=np.zeros((DataSize[0],NbTerms))
            for i,r in enumerate(Raw):
                tmp=np.array(r)
                p=tmp[:,4,:]
                f=tmp[:,3,:]
                MeanSq=tmp[:,2,:]
                if ConfundTerm:
                    ind=index[i]
                    NaNindex=p.shape[1]-1
                    ind.append(NaNindex)
                    p=p[:,ind]
                    f=f[:,ind]
                    MeanSq=MeanSq[:,ind]
                    ind.remove(NaNindex)
              
                pshape=p.shape
                nterms=pshape[1]-1
                if (np.isnan(p)).sum()==(np.array(pshape)).prod():
                    p=p[np.isnan(p)==False]
                # il y a que de NaN
                elif (np.isnan(p)).sum()!=DataSize[0]:
                    # au moins une des collone est non NAN
                    NbNanByCol=(np.isnan(p)).sum(axis=0)!=DataSize[0]
                    NbNanByCol=NbNanByCol.reshape((1,NbNanByCol.shape[0]))
                    NbNanByCol=NbNanByCol.repeat(DataSize[0],axis=0)
                    p=p[NbNanByCol]
                    p[np.isnan(p)]=1 
                else:
                    p=p[np.isnan(p)==False]
                if p.shape[0]==0 and nterms!=0:
                    p=np.ones((DataSize[0],nterms))
                else:
                    p=p.reshape((DataSize[0],nterms))
                
                
                # il y a que de NaN
                if (np.isnan(f)).sum()==(np.array(pshape)).prod():
                    f=f[np.isnan(f)==False]
                elif (np.isnan(f)).sum()!=DataSize[0]:
                    f=f[NbNanByCol]
                    f[np.isnan(f)]=0
                else:
                    f=f[np.isnan(f)==False]
                if f.shape[0]==0 and nterms!=0:
                    f=np.zeros((DataSize[0],nterms))
                else:
                    f=f.reshape((DataSize[0],nterms))   
                df=tmp[0,0,:].tolist()
                Df.extend(df)
                if i==0:
                    fin=0
                    debut=0
                else:
                    debut=fin
                fin+=(p.shape[1])
                P[:,debut:fin]=p
                F[:,debut:fin]=f
            ResultP.append(P)
            ResultF.append(F)
            CoefValue.append(CoefValueTmp)
            self.Df=np.array(Df)
            pourcent=str(100.0*fin1/(NbAnova))
            pourcent=pourcent[0:pourcent.find('.')+3]
            Cancel = dlg.Update(fin1," ".join(['Progression  :',pourcent,' %']))
            if Cancel[0]== False:
                dlgQuest = wx.MessageDialog(None,"Do you really want to cancel ?","Confirm Cancel", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
                result = dlgQuest.ShowModal()
                dlgQuest.Destroy()
                if result == wx.ID_OK:
                    self.Cancel=True
                    break
                else:
                    self.Cancel=False
                    dlg.Resume()
                    
        dlg.Close()
        dlg.Destroy()

        

        
    def NonParam(self,iter,DataGFP=False):
        iter=int(iter)
        # mise en forme de Data
        if DataGFP:
            shape=self.file.getNode('/Info/ShapeGFP')
        else:
            shape=self.file.getNode('/Info/Shape')
        shape=shape.read()
        NbSujet=shape[3]
        NbCond=shape[2]
        # GFP bool dit on cacul le GFP dans la stat
        NbAnova=int(shape[0]*shape[1])
        Byte=shape.prod()
        Cycle=int(Byte/10000)
        try:
            NbAnovaCycle=NbAnova/Cycle
        except:
            NbAnovaCycle=NbAnova


        #On fait 1 anova pour les terms
        DataAnova=ExtractData(self.file,0,1,DataGFP)
        DataAnova=DataAnova.extract.reshape((NbSujet*NbCond))
        DataR=robjects.RArray(DataAnova.T)
        robjects.globalEnv["DataR"] = DataR
        TextR=['aov(',self.Formule,')']
        express=rpy2.robjects.r.parse(text = "".join(TextR))
        Fit=rpy2.robjects.r.eval(express)
        robjects.globalEnv["Fit"] = Fit
        # calcul Anova
        Raw=robjects.r.summary(Fit)
        
        #calcul des Terms
        Terms=[]
        ConfundTerm=False
        index=[]
        for i in range(len(Raw)):
            tmp=Raw[i][0]
            tmp=robjects.r.slot(tmp,"row.names")
            tmp=list(tmp)
            del(tmp[len(tmp)-1])
            if i==0:
                if self.NameWithin!=False:
                    for t in tmp:
                        if t.find(self.NameWithin[0])!=-1:
                            ConfundTerm=True
                            break
              
            if ConfundTerm:
                if i==0:
                    Terms.extend(tmp)
                    TermsSubject=tmp
                    rm=range(len(tmp))
                    index.append(rm)
                else:
                    rm=range(len(tmp))
                    for t in TermsSubject:
                        ind=tmp.index(t)
                        rm.remove(ind)
                    for r in rm:
                        Terms.append(tmp[r])
                    index.append(rm)
            else:     
                Terms.extend(tmp)
        for i,t in enumerate(Terms):
            Terms[i]=t[0:t.find(' ')]
        NbTerms=len(Terms)
        self.Terms=Terms

        
        # terms des estimateurs
        coef=robjects.r.coef(Fit)
        coef=list(coef)
        indexCoefTerms=[]
        CoefTermsTmp=[]
        for n,c in enumerate(coef):
            txt=str(c)
            m=0
            ind=[]
            if txt!='numeric(0)':
                    txt=txt.replace('\r\n','')
                    txt=txt.rsplit(' ')
                    for i in txt:
                        if i !='':
                            try:
                                tmp=float(i)
                            except:
                                if ConfundTerm and n>1:
                                    try:
                                        CoefTermsTmp.index(i)
                                        m+=1
                                    except:
                                        CoefTermsTmp.append(i)
                                        ind.append(m)
                                        m+=1
                                else:
                                    CoefTermsTmp.append(i)
                                    ind.append(m)
                                    m+=1
            indexCoefTerms.append(ind)
        CoefTerms=[]
        for i in CoefTermsTmp:
            if i.find('\n')==-1:
                CoefTerms.append(i)
        
        self.CoefTerms=CoefTerms
        NbCoefTerms=len(CoefTerms)
        
        if DataGFP: #c'est sur le GFP
            ResultP=self.file.createEArray('/Result/Anova/GFP','P',tables.Float64Atom(),(0,NbTerms))
            ResultF=self.file.createEArray('/Result/Anova/GFP','F',tables.Float64Atom(),(0,NbTerms))
            self.file.createArray('/Result/Anova/GFP','Terms',self.Terms)
            self.file.createArray('/Result/Anova/GFP','CoefTerms',CoefTerms)
            CoefValue=self.file.createEArray('/Result/Anova/GFP','CoefValue',tables.Float64Atom(),(0,NbCoefTerms))
        else: # c'est sur toutes les electrodes
            ResultP=self.file.createEArray('/Result/Anova/All','P',tables.Float64Atom(),(0,NbTerms))
            ResultF=self.file.createEArray('/Result/Anova/All','F',tables.Float64Atom(),(0,NbTerms))
            self.file.createArray('/Result/Anova/All','Terms',self.Terms)
            self.file.createArray('/Result/Anova/All','CoefTerms',CoefTerms)
            
            CoefValue=self.file.createEArray('/Result/Anova/All','CoefValue',tables.Float64Atom(),(0,NbCoefTerms))
        Df=[]
        # fiting
        if NbAnova%NbAnovaCycle==0:
            Maximum=((NbAnova/NbAnovaCycle))*iter
        else:
            Maximum=((NbAnova/NbAnovaCycle)+1)*iter
        dlg=wx.ProgressDialog('Non Parametric Anova','Progression : 0 %',Maximum,parent=self.parent,style=wx.PD_CAN_ABORT|wx.PD_AUTO_HIDE|wx.PD_REMAINING_TIME)
        dlg.SetSize((200,175))
        n=0
        fin1=0
        step=0
        self.OrderSubject=[]
        self.OrderCond=[]
        while fin1 < NbAnova:
            debut1=n*NbAnovaCycle
            fin1=(n+1)*NbAnovaCycle
            n+=1
            if fin1>NbAnova:
                fin1=NbAnova
                Data=ExtractData(self.file,debut1,fin1,DataGFP)
                NbAnovaCycle=Data.extract.shape[0]
                Data=Data.extract.reshape((Data.extract.shape[0],NbSujet*NbCond))
            else:
                Data=ExtractData(self.file,debut1,fin1,DataGFP)
                Data=Data.extract.reshape((NbAnovaCycle,NbSujet*NbCond))


            DataSize=Data.shape
            # on transpose pour R
            DataR=robjects.RArray(Data.T)
            robjects.globalEnv["DataR"] = DataR
            TextR=['aov(',self.Formule,')']
            express=rpy2.robjects.r.parse(text = "".join(TextR))
            Fit=rpy2.robjects.r.eval(express)
            robjects.globalEnv["Fit"] = Fit
            # calcul Anova
            Raw=robjects.r.summary(Fit)
            Raw=list(Raw)
            # estimateurs
            coef=robjects.r.coef(Fit)
            coef=list(coef)
            CoefValueTmp=np.zeros((NbAnovaCycle,NbCoefTerms))
            debut=0
            for i,c in enumerate(coef):
                nbterms=len(c)/NbAnovaCycle
                tmp=np.array(c)
                tmp=tmp.reshape((NbAnovaCycle,nbterms))
                if ConfundTerm:
                    tmp=tmp[:,indexCoefTerms[i]]
                    nbterms=len(indexCoefTerms[i])
                fin=debut+nbterms
                CoefValueTmp[:,debut:fin]=tmp  
                debut=fin
            # extraction de P,f, DF
            FReal=np.zeros((DataSize[0],NbTerms))
            for i,r in enumerate(Raw):
                tmp=np.array(r)
                p=tmp[:,4,:]
                f=tmp[:,3,:]
                MeanSq=tmp[:,2,:]
                if ConfundTerm:
                    ind=index[i]
                    NaNindex=p.shape[1]-1
                    ind.append(NaNindex)
                    p=p[:,ind]
                    f=f[:,ind]
                    MeanSq=MeanSq[:,ind]
                    ind.remove(NaNindex)
              
                
                pshape=p.shape
                nterms=pshape[1]-1
                p=p[np.isnan(p)==False]
                p=p.reshape((DataSize[0],nterms))
                f=f[np.isnan(f)==False]
                f=f.reshape((DataSize[0],nterms))
                if i==0:
                    fin=0
                    debut=0
                else:
                    debut=fin
                fin+=(f.shape[1])
                FReal[:,debut:fin]=f
            CoefValue.append(CoefValueTmp)
            Count=np.zeros(FReal.shape)
            ResultF.append(FReal)
            for i in range(iter):
                # on fait les randomisations 
                if debut1==0:
                    NbSujet=int(shape[len(shape)-1])
                    NbCond=int(shape[len(shape)-2])
                    OrderSubject=[]
                    OrderCond=[]
                    for s in range(NbSujet):
                        OrderSubject.append(random.randint(0,NbSujet-1))
                        Cond=range(NbCond)
                        random.shuffle(Cond)
                        OrderCond.append(Cond)
                    self.OrderSubject.append(OrderSubject)
                    self.OrderCond.append(OrderCond)
                # donee bootstrap
                if fin1>NbAnova:
                    fin1=NbAnova
                    NbAnovaCycle=Data.extract.shape[0]
                    Data=ExtractDataNonParam(self.file,debut1,fin1,DataGFP,self.OrderSubject[i],self.OrderCond[i])
                    Data=Data.extract.reshape((NbAnovaCycle,NbSujet*NbCond))
                else:
                    Data=ExtractDataNonParam(self.file,debut1,fin1,DataGFP,self.OrderSubject[i],self.OrderCond[i])
                    Data=Data.extract.reshape((Data.extract.shape[0],NbSujet*NbCond))
                DataSize=Data.shape
                # on transpose pour R
                DataR=robjects.RArray(Data.T)
                robjects.globalEnv["DataR"] = DataR
                TextR=['aov(',self.Formule,')']
                express=rpy2.robjects.r.parse(text = "".join(TextR))
                Fit=rpy2.robjects.r.eval(express)
                robjects.globalEnv["Fit"] = Fit
                # calcul Anova
                Raw=robjects.r.summary(Fit)
                Raw=list(Raw)
                # extraction de P,f, DF
                FBoot=np.zeros((DataSize[0],NbTerms))
                for i,r in enumerate(Raw):
                    tmp=np.array(r)
                    p=tmp[:,4,:]
                    f=tmp[:,3,:]
                    MeanSq=tmp[:,2,:]
                    if ConfundTerm:
                        ind=index[i]
                        NaNindex=p.shape[1]-1
                        ind.append(NaNindex)
                        p=p[:,ind]
                        f=f[:,ind]
                        MeanSq=MeanSq[:,ind]
                        ind.remove(NaNindex)
              
                
                    pshape=p.shape
                    nterms=pshape[1]-1
                    p=p[np.isnan(p)==False]
                    p=p.reshape((DataSize[0],nterms))
                    f=f[np.isnan(f)==False]
                    f=f.reshape((DataSize[0],nterms))
                    if i==0:
                        fin=0
                        debut=0
                    else:
                        debut=fin
                    fin+=(f.shape[1])
                    FBoot[:,debut:fin]=f
                diff=FBoot-FReal
                CountTmp=np.zeros(diff.shape)
                CountTmp[diff>0]=1
                Count+=CountTmp
                pourcent=str(100.0*step/(Maximum))
                pourcent=pourcent[0:pourcent.find('.')+3]
                Cancel = dlg.Update(step," ".join(['Progression  :',pourcent,' %']))
                if Cancel[0]== False:
                    dlgQuest = wx.MessageDialog(None,"Do you really want to cancel ?","Confirm Cancel", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
                    result = dlgQuest.ShowModal()
                    dlgQuest.Destroy()
                    if result == wx.ID_OK:
                        self.Cancel=True
                        break
                        
                    else:
                        self.Cancel=False
                        dlg.Resume()    
                step+=1
            P=Count/iter
            ResultP.append(P)
            if self.Cancel:
                break
        dlg.Close()
        dlg.Destroy()
            
class ExtractData:
    def __init__(self,file,debut,fin,GFP):
        if GFP:
            shape=file.getNode('/Info/ShapeGFP')
        else:
            shape=file.getNode('/Info/Shape')
        shape=shape.read()
        NbSujet=int(shape[len(shape)-1])
        NbCond=int(shape[len(shape)-2])
        NbAnovaCycle=fin-debut
        DataTmp=np.zeros((NbAnovaCycle,NbCond,NbSujet))
        for s in range(NbSujet):
            for c in range(NbCond):
                if GFP:
                    location=['/DataGFP/Subject',str(s),'/Condition',str(c)]
                else:
                    location=['/Data/Subject',str(s),'/Condition',str(c)]
                
                tmp=file.getNode("".join(location))
                tmp=tmp.read()
                NbAnova=tmp.shape
                NbAnova=np.array(NbAnova)
                tmp=tmp.reshape(NbAnova.prod())
                DataTmp[:,c,s]=tmp[debut:fin]
        #DataTmp=DataTmp.reshape((NbAnovaCycle,NbCond*NbSujet))
        self.extract=DataTmp
        del(DataTmp)
        
class ExtractDataNonParam:
    def __init__(self,file,debut,fin,GFP,OrderSubject,OrderCond):
        if GFP:
            shape=file.getNode('/Info/ShapeGFP')
        else:
            shape=file.getNode('/Info/Shape')
        shape=shape.read()
        NbSujet=int(shape[len(shape)-1])
        NbCond=int(shape[len(shape)-2])
        NbAnovaCycle=fin-debut
        DataTmp=np.zeros((NbAnovaCycle,NbCond,NbSujet))
        for i,s in enumerate(OrderSubject):
            for c in OrderCond[i]:
                if GFP:
                    location=['/DataGFP/Subject',str(s),'/Condition',str(c)]
                else:
                    location=['/Data/Subject',str(s),'/Condition',str(c)]
                tmp=file.getNode("".join(location))
                tmp=tmp.read()
                NbAnova=tmp.shape
                NbAnova=np.array(NbAnova)
                tmp=tmp.reshape(NbAnova.prod())
                DataTmp[:,c,s]=tmp[debut:fin]
        #DataTmp=DataTmp.reshape((NbAnovaCycle,NbCond*NbSujet))
        self.extract=DataTmp
        del(DataTmp)
            
class PostHoc:
    def __init__(self,H5,Parent):
        self.Parent=Parent
        self.file=tables.openFile(H5,mode='r+')
        # models
        Between=self.file.getNode('/Model/Between')
        self.Between=np.array(Between.read())
        Within=self.file.getNode('/Model/Within')
        self.Within=np.array(Within.read())
        Subject=self.file.getNode('/Model/Subject')
        self.Subject=Subject.read()
        # Names
        NameBetween=self.file.getNode('/Names/Between')
        self.NameBetween=NameBetween.read()
        NameWithin=self.file.getNode('/Names/Within')
        self.NameWithin=NameWithin.read()
        self.Cancel=False

        
    def Param(self,DataGFP=False):
        if DataGFP:
            shape=self.file.getNode('/Info/ShapeGFP')
        else:
            shape=self.file.getNode('/Info/Shape')
        shape=shape.read()
        # Mettre le veteur sujet en 2 dimentions, afin d'etre sur que la deuxième dimention existe
        if len(self.Subject.shape)==1:
            self.Subject=self.Subject.reshape((self.Subject.shape[0],1))
        NbSubject=self.Subject.max()
        LevelWithin=self.file.getNode('/Info/Level')
        LevelWithin=LevelWithin.read()
        NbConditionWithin=LevelWithin.prod()
        # test il y a un facteur Within
        if self.Within.any():
            ConditionNumber=np.array([])
            for i in range(NbConditionWithin):
                tmp=np.ones((NbSubject))
                tmp=tmp*(i+1)
                ConditionNumber=np.concatenate((ConditionNumber,tmp))
            ConditionNumber=ConditionNumber.reshape((ConditionNumber.shape[0],1))
        else:
            # il n'y a pas de facteur Within
            ConditionNumber=np.ones((NbSubject))
         # Mettre le veteur Between en 2 dimentions, afin d'etre sur que la deuxième dimention existe
        if self.Between.any():
            if len(self.Between.shape)==1:
                self.Between=self.Between.reshape((self.Between.shape[0],1))

        fs=self.file.getNode('/Info/FS')
        fs=fs.read()

        # crée la list CondionTxt, contenant le nom des facteurs within puis between pour les noms en sortie
        # création de la liste level contenant le niveau de chaque facteur d'abord within puis between
        ConditionTxt=[]
        Level=[]
        if self.Within.any():
            for i,w in enumerate(self.NameWithin):
                try:
                    NbLevel=int(self.Within[:,i].max())
                except:
                    NbLevel=int(self.Within.max())
                Level.append(NbLevel)
                for j in range(NbLevel):
                    text=[w,str(j+1),'=0']
                    exec("".join(text))
                ConditionTxt.append(w)
        if self.Between.any():
            for i,w in enumerate(self.NameBetween):
                try:
                    NbLevel=int(self.Between[:,i].max())
                except:
                    NbLevel=int(self.Between.max())
                Cond=[]
                Level.append(NbLevel)
                for j in range(NbLevel):
                    text=[w,str(j+1),'=0']
                    exec("".join(text))
                ConditionTxt.append(w)


        Level=np.array(Level)
        NbCondition=Level.prod()
        # creation de la list combinaison regroupant toute les combinaison possible aves les facteurs within et between
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
        # creation de la matrice condition avec les veteurs/matrice within et/ou between.
        # Ces matrice sont composer de valeur 1,2, nb niveau par niveau matrice utiliser pour le model dans R
        #facteur within et Between
        if self.Within.any() and self.Between.any():
            Condition=np.concatenate((self.Within,self.Between),axis=1)
        #Pas de facteur Between
        elif self.Within.any():
            Condition=self.Within
        #Pas de facteur within que Between
        elif self.Between.any():
            Condition=self.Between
            
        NbTest=np.array(range(len(Combinaison))).sum()
        dlg=wx.ProgressDialog('Parametric T-test',"/".join(['PostHoc T-Test : 0',str(NbTest)]),NbTest,parent=self.Parent,style=wx.PD_CAN_ABORT|wx.PD_AUTO_HIDE|wx.PD_REMAINING_TIME)
        dlg.SetSize((200,175))
        # lecture des données dans le H5 pour crée les matrices permettant le calcul des t-test
        NbFactorWithin=self.Within.shape[1]
        Name=[]
        n=0
        if DataGFP: #c'est sur le GFP
            ResultP=self.file.createEArray('/Result/PostHoc/GFP','P',tables.Float64Atom(),(shape[0]*shape[1],0))
            ResultT=self.file.createEArray('/Result/PostHoc/GFP','T',tables.Float64Atom(),(shape[0]*shape[1],0))
        else: # c'est sur toutes les electrodes
            ResultP=self.file.createEArray('/Result/PostHoc/All','P',tables.Float64Atom(),(shape[0]*shape[1],0))
            ResultT=self.file.createEArray('/Result/PostHoc/All','T',tables.Float64Atom(),(shape[0]*shape[1],0))
        for Nbc,c1 in enumerate(Combinaison):
            tmp=(Condition==c1).sum(axis=1)==len(c1)
            SubjectTmp=self.Subject[tmp]
            ConditionTmp=ConditionNumber[tmp]
            Data1=[]
            for i,s in enumerate(SubjectTmp):
                if DataGFP:
                    text=['/DataGFP/Subject',str(int(s-1)),'/Condition',str(int(ConditionTmp[i]-1))]
                    DataTmp=self.file.getNode("".join(text))
                    DataTmp=DataTmp.read()
                    Data1.append(DataTmp)
                else:
                    text=['/Data/Subject',str(int(s-1)),'/Condition',str(int(ConditionTmp[i]-1))]
                    DataTmp=self.file.getNode("".join(text))
                    DataTmp=DataTmp.read()
                    Data1.append(DataTmp)
            Data1=np.array(Data1)
            EphFile=[]
            for i,combi in enumerate(c1):
                txt=[ConditionTxt[i],str(int(combi))]
                EphFile.append("-".join(txt))
            EphFile.append('vs')
            for c in range(Nbc+1,len(Combinaison)):
                c2=Combinaison[c]
                tmp=(Condition==c2).sum(axis=1)==len(c2)
                SubjectTmp=self.Subject[tmp]
                ConditionTmp=ConditionNumber[tmp]
                Data2=[]
                for i,s in enumerate(SubjectTmp):
                    if DataGFP:
                        text=['/DataGFP/Subject',str(int(s-1)),'/Condition',str(int(ConditionTmp[i]-1))]
                        DataTmp=self.file.getNode("".join(text))
                        DataTmp=DataTmp.read()
                        Data2.append(DataTmp)  
                    else:
                        text=['/Data/Subject',str(int(s-1)),'/Condition',str(int(ConditionTmp[i]-1))]
                        DataTmp=self.file.getNode("".join(text))
                        DataTmp=DataTmp.read()
                        Data2.append(DataTmp)
                Data2=np.array(Data2)
                for i,combi in enumerate(c2):
                    txt=[ConditionTxt[i],str(int(combi))]
                    EphFile.append("-".join(txt))
                
                
                #que des paired T-test car pas de facteur Bewtween
                if self.NameBetween==[]:
                    EphFile.insert(0,'Paired-Ttest')
                    res=stats.ttest_rel(Data1,Data2,axis=0)
                    Name.append("".join(EphFile))
                    EphFile.remove('Paired-Ttest')
                #que des unpaired T-test car pas de facteur Within
                elif self.NameWithin==[]:
                    EphFile.insert(0,'UnPaired-Ttest')
                    res=stats.ttest_ind(Data1,Data2,axis=0)
                    Name.append(".".join(EphFile))
                    EphFile.remove('UnPaired-Ttest')
                #parend et un paired dépendant du facteur between
                else:
                    # on test que tout les niveau des facteurs between soit les meme si c'est le cas on a du paired sinon unpaired
                    # on compare si les conditions between on les même niveau, on somme pui si cette somme est strictement egale
                    # au nombre total de condtions - nb de facteur within (nombre de facteur between) alos paired
                    if (c2[NbFactorWithin:len(c2)]==c1[NbFactorWithin:len(c2)]).sum()==len(c1)-NbFactorWithin: # if true = paired
                        EphFile.insert(0,'Paired-Ttest')
                        res=stats.ttest_rel(Data1,Data2,axis=0)
                        Name.append(".".join(EphFile))
                        EphFile.remove('Paired-Ttest')
                    else:
                        EphFile.insert(0,'UnPaired-Ttest')
                        res=stats.ttest_ind(Data1,Data2,axis=0)
                        Name.append(".".join(EphFile))
                        EphFile.remove('UnPaired-Ttest')
                if len(res[1].shape)==1:
                    taille=res[1].shape[0]
                    P=res[1].reshape((taille,1))
                    T=res[0].reshape((taille,1))
                else:
                    P=res[1]
                    T=res[0]


                    
                ShapeData=P.shape
                ShapeData=np.array(ShapeData)
                P=P.reshape((ShapeData.prod(),1))
                T=T.reshape((ShapeData.prod(),1))
                ResultP.append(P)
                ResultT.append(T)
                n+=1
                EphFile=EphFile[0:EphFile.index('vs')]
                EphFile.append('vs')
                prog="".join(['PostHoc T-Test : ',str(n),'/',str(NbTest)])
                Cancel = dlg.Update(n,prog)
                if Cancel[0]== False:
                    dlgQuest = wx.MessageDialog(None,"Do you really want to cancel ?","Confirm Cancel", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
                    result = dlgQuest.ShowModal()
                    dlgQuest.Destroy()
                    if result == wx.ID_OK:
                        self.Cancel=True
                        break
                        
                    else:
                        self.Cancel=False
                        dlg.Resume()
        
        if DataGFP:
            self.file.createArray('/Result/PostHoc/GFP','Terms',Name)
        else:
            self.file.createArray('/Result/PostHoc/All','Terms',Name)



                
            
    def NonParam(self,iter,DataGFP=False):
        if DataGFP:
            shape=self.file.getNode('/Info/ShapeGFP')
        else:
            shape=self.file.getNode('/Info/Shape')
        shape=shape.read()
        # Mettre le veteur sujet en 2 dimentions, afin d'etre sur que la deuxième dimention existe
        if len(self.Subject.shape)==1:
            self.Subject=self.Subject.reshape((self.Subject.shape[0],1))
        NbSubject=self.Subject.max()
        LevelWithin=self.file.getNode('/Info/Level')
        LevelWithin=LevelWithin.read()
        NbConditionWithin=LevelWithin.prod()
        # test il y a un facteur Within
        if self.Within.any():
            ConditionNumber=np.array([])
            for i in range(NbConditionWithin):
                tmp=np.ones((NbSubject))
                tmp=tmp*(i+1)
                ConditionNumber=np.concatenate((ConditionNumber,tmp))
            ConditionNumber=ConditionNumber.reshape((ConditionNumber.shape[0],1))
        else:
            # il n'y a pas de facteur Within
            ConditionNumber=np.ones((NbSubject))
         # Mettre le veteur Between en 2 dimentions, afin d'etre sur que la deuxième dimention existe
        if self.Between.any():
            if len(self.Between.shape)==1:
                self.Between=self.Between.reshape((self.Between.shape[0],1))

        fs=self.file.getNode('/Info/FS')
        fs=fs.read()

        # crée la list CondionTxt, contenant le nom des facteurs within puis between pour les noms en sortie
        # création de la liste level contenant le niveau de chaque facteur d'abord within puis between
        ConditionTxt=[]
        Level=[]
        if self.Within.any():
            for i,w in enumerate(self.NameWithin):
                try:
                    NbLevel=int(self.Within[:,i].max())
                except:
                    NbLevel=int(self.Within.max())
                Level.append(NbLevel)
                for j in range(NbLevel):
                    text=[w,str(j+1),'=0']
                    exec("".join(text))
                ConditionTxt.append(w)
        if self.Between.any():
            for i,w in enumerate(self.NameBetween):
                try:
                    NbLevel=int(self.Between[:,i].max())
                except:
                    NbLevel=int(self.Between.max())
                Cond=[]
                Level.append(NbLevel)
                for j in range(NbLevel):
                    text=[w,str(j+1),'=0']
                    exec("".join(text))
                ConditionTxt.append(w)


        Level=np.array(Level)
        NbCondition=Level.prod()
        # creation de la list combinaison regroupant toute les combinaison possible aves les facteurs within et between
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
        # creation de la matrice condition avec les veteurs/matrice within et/ou between.
        # Ces matrice sont composer de valeur 1,2, nb niveau par niveau matrice utiliser pour le model dans R
        #facteur within et Between
        if self.Within.any() and self.Between.any():
            Condition=np.concatenate((self.Within,self.Between),axis=1)
        #Pas de facteur Between
        elif self.Within.any():
            Condition=self.Within
        #Pas de facteur within que Between
        elif self.Between.any():
            Condition=self.Between
            
        NbTest=np.array(range(len(Combinaison))).sum()
        dlg=wx.ProgressDialog('Non-Parametric T-test',"/".join(['PostHoc T-Test : 0',str(NbTest)]),NbTest,parent=self.Parent,style=wx.PD_CAN_ABORT|wx.PD_AUTO_HIDE|wx.PD_REMAINING_TIME)
        dlg.SetSize((200,175))
        # lecture des données dans le H5 pour crée les matrices permettant le calcul des t-test
        NbFactorWithin=self.Within.shape[1]
        Name=[]
        n=0
        if DataGFP: #c'est sur le GFP
            ResultP=self.file.createEArray('/Result/PostHoc/GFP','P',tables.Float64Atom(),(shape[0]*shape[1],0))
            ResultT=self.file.createEArray('/Result/PostHoc/GFP','T',tables.Float64Atom(),(shape[0]*shape[1],0))
        else: # c'est sur toutes les electrodes
            ResultP=self.file.createEArray('/Result/PostHoc/All','P',tables.Float64Atom(),(shape[0]*shape[1],0))
            ResultT=self.file.createEArray('/Result/PostHoc/All','T',tables.Float64Atom(),(shape[0]*shape[1],0))
        for Nbc,c1 in enumerate(Combinaison):
            tmp=(Condition==c1).sum(axis=1)==len(c1)
            SubjectTmp=self.Subject[tmp]
            ConditionTmp=ConditionNumber[tmp]
            Data1=[]
            text1=[]
            for i,s in enumerate(SubjectTmp):
                if DataGFP:
                    text=['/DataGFP/Subject',str(int(s-1)),'/Condition',str(int(ConditionTmp[i]-1))]
                    DataTmp=self.file.getNode("".join(text))
                    DataTmp=DataTmp.read()
                    Data1.append(DataTmp)
                else:
                    text=['/Data/Subject',str(int(s-1)),'/Condition',str(int(ConditionTmp[i]-1))]
                    DataTmp=self.file.getNode("".join(text))
                    DataTmp=DataTmp.read()
                    Data1.append(DataTmp)
                text1.append(text)
            Data1=np.array(Data1)
            EphFile=[]
            for i,combi in enumerate(c1):
                txt=[ConditionTxt[i],str(int(combi))]
                EphFile.append("-".join(txt))
            EphFile.append('vs')
            for c in range(Nbc+1,len(Combinaison)):
                c2=Combinaison[c]
                tmp=(Condition==c2).sum(axis=1)==len(c2)
                SubjectTmp=self.Subject[tmp]
                ConditionTmp=ConditionNumber[tmp]
                text2=[]
                Data2=[]
                for i,s in enumerate(SubjectTmp):
                    if DataGFP:
                        text=['/DataGFP/Subject',str(int(s-1)),'/Condition',str(int(ConditionTmp[i]-1))]
                        DataTmp=self.file.getNode("".join(text))
                        DataTmp=DataTmp.read()
                        Data2.append(DataTmp)  
                    else:
                        text=['/Data/Subject',str(int(s-1)),'/Condition',str(int(ConditionTmp[i]-1))]
                        DataTmp=self.file.getNode("".join(text))
                        DataTmp=DataTmp.read()
                        Data2.append(DataTmp)
                    text2.append(text)    
                Data2=np.array(Data2)
                
                for i,combi in enumerate(c2):
                    txt=[ConditionTxt[i],str(int(combi))]
                    EphFile.append("-".join(txt))
                
                
                #que des paired T-test car pas de facteur Bewtween
                if self.NameBetween==[]:
                    EphFile.insert(0,'Paired-Ttest')
                    res=stats.ttest_rel(Data1,Data2,axis=0)
                    Name.append("".join(EphFile))
                    EphFile.remove('Paired-Ttest')
                #que des unpaired T-test car pas de facteur Within
                elif self.NameWithin==[]:
                    EphFile.insert(0,'UnPaired-Ttest')
                    res=stats.ttest_ind(Data1,Data2,axis=0)
                    Name.append(".".join(EphFile))
                    EphFile.remove('UnPaired-Ttest')
                #parend et un paired dépendant du facteur between
                else:
                    # on test que tout les niveau des facteurs between soit les meme si c'est le cas on a du paired sinon unpaired
                    # on compare si les conditions between on les même niveau, on somme pui si cette somme est strictement egale
                    # au nombre total de condtions - nb de facteur within (nombre de facteur between) alos paired
                    if (c2[NbFactorWithin:len(c2)]==c1[NbFactorWithin:len(c2)]).sum()==len(c1)-NbFactorWithin: # if true = paired
                        EphFile.insert(0,'Paired-Ttest')
                        res=stats.ttest_rel(Data1,Data2,axis=0)
                        Name.append(".".join(EphFile))
                        EphFile.remove('Paired-Ttest')
                    else:
                        EphFile.insert(0,'UnPaired-Ttest')
                        res=stats.ttest_ind(Data1,Data2,axis=0)
                        Name.append(".".join(EphFile))
                        EphFile.remove('UnPaired-Ttest')
                EphFile=EphFile[0:EphFile.index('vs')]
                EphFile.append('vs')
                TReal=res[0]
                Count=np.zeros(TReal.shape)
                iter=int(iter)
                for i in range(iter):
                    Data1=[]
                    Data2=[]
                    if self.NameBetween==[]:
                        for s in range(len(text1)):
                            Subject=[random.randint(0,(len(text1))-1)]
                            if random.randint(0,1)==0:
                                    DataTmp=self.file.getNode("".join(text1[Subject[0]]))
                                    DataTmp=DataTmp.read()
                                    Data1.append(DataTmp)
                                    DataTmp=self.file.getNode("".join(text2[Subject[0]]))
                                    DataTmp=DataTmp.read()
                                    Data2.append(DataTmp)
                            else:
                                    DataTmp=self.file.getNode("".join(text2[Subject[0]]))
                                    DataTmp=DataTmp.read()
                                    Data1.append(DataTmp)
                                    DataTmp=self.file.getNode("".join(text1[Subject[0]]))
                                    DataTmp=DataTmp.read()
                                    Data2.append(DataTmp)
                        Data1=np.array(Data1)
                        Data2=np.array(Data2)
                        res=stats.ttest_rel(Data1,Data2,axis=0)
                    #que des unpaired T-test car pas de facteur Within
                    elif self.NameWithin==[]:
                        text=[]
                        text.extend(text1)
                        text.extend(text2)
                        for s in range(len(text1)):
                                Subject=[random.randint(0,(len(text))-1)]
                                DataTmp=self.file.getNode("".join(text[Subject[0]]))
                                DataTmp=DataTmp.read()
                                Data1.append(DataTmp)
                        for s in range(len(text2)):
                                Subject=[random.randint(0,(len(text))-1)]
                                DataTmp=self.file.getNode("".join(text[Subject[0]]))
                                DataTmp=DataTmp.read()
                                Data2.append(DataTmp)
                        Data1=np.array(Data1)
                        Data2=np.array(Data2)
                        res=stats.ttest_ind(Data1,Data2,axis=0)
                    #paired and un paired dépendant du facteur between
                    else:
                        # on test que tout les niveau des facteurs between soit les meme si c'est le cas on a du paired sinon unpaired
                        # on compare si les conditions between on les même niveau, on somme pui si cette somme est strictement egale
                        # au nombre total de condtions - nb de facteur within (nombre de facteur between) alos paired
                        if (c2[NbFactorWithin:len(c2)]==c1[NbFactorWithin:len(c2)]).sum()==len(c1)-NbFactorWithin: # if true = paired
                            for s in range(len(text1)):
                                Subject=[random.randint(0,(len(text1))-1)]
                                if random.randint(0,1)==0:
                                    DataTmp=self.file.getNode("".join(text1[Subject[0]]))
                                    DataTmp=DataTmp.read()
                                    Data1.append(DataTmp)
                                    DataTmp=self.file.getNode("".join(text2[Subject[0]]))
                                    DataTmp=DataTmp.read()
                                    Data2.append(DataTmp)
                                else:
                                    DataTmp=self.file.getNode("".join(text2[Subject[0]]))
                                    DataTmp=DataTmp.read()
                                    Data1.append(DataTmp)
                                    DataTmp=self.file.getNode("".join(text1[Subject[0]]))
                                    DataTmp=DataTmp.read()
                                    Data2.append(DataTmp)
                            Data1=np.array(Data1)
                            Data2=np.array(Data2)
                            res=stats.ttest_rel(Data1,Data2,axis=0)
                        else:
                            text=[]
                            text.extend(text1)
                            text.extend(text2)
                            for s in range(len(text1)):
                                Subject=[random.randint(0,(len(text))-1)]
                                DataTmp=self.file.getNode("".join(text[Subject[0]]))
                                DataTmp=DataTmp.read()
                                Data1.append(DataTmp)
                            for s in range(len(text2)):
                                Subject=[random.randint(0,(len(text))-1)]
                                DataTmp=self.file.getNode("".join(text[Subject[0]]))
                                DataTmp=DataTmp.read()
                                Data2.append(DataTmp)
                            Data1=np.array(Data1)
                            Data2=np.array(Data2)
                            res=stats.ttest_ind(Data1,Data2,axis=0)
                    TBoot=res[0]
                    diff=TBoot-TReal
                    CountTmp=np.zeros(diff.shape)
                    CountTmp[diff>0]=1
                    Count+=CountTmp
                P=Count/iter


                if len(res[1].shape)==1:
                    taille=res[1].shape[0]
                    P=res[1].reshape((taille,1))
                    T=res[0].reshape((taille,1))
                else:
                    P=res[1]
                    T=res[0]
                ShapeData=P.shape
                ShapeData=np.array(ShapeData)
                P=P.reshape((ShapeData.prod(),1))
                T=T.reshape((ShapeData.prod(),1))
                ResultP.append(P)
                ResultT.append(T)
                n+=1
                prog="".join(['PostHoc T-Test : ',str(n),'/',str(NbTest)])
                Cancel = dlg.Update(n,prog)
                if Cancel[0]== False:
                    dlgQuest = wx.MessageDialog(None,"Do you really want to cancel ?","Confirm Cancel", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
                    result = dlgQuest.ShowModal()
                    dlgQuest.Destroy()
                    if result == wx.ID_OK:
                        self.Cancel=True
                        break
                        
                    else:
                        self.Cancel=False
                        dlg.Resume() 
                   
        if DataGFP:
            self.file.createArray('/Result/PostHoc/GFP','Terms',Name)
        else:
            self.file.createArray('/Result/PostHoc/All','Terms',Name)
        
