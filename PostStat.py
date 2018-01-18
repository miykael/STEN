import numpy as np
import tables
import wx
import os
import itertools
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
    def __init__(self, H5, parent,TF=1,Alpha=0.05,SpaceCont=1,SpaceFile=None):
        """ Initialisation for multiple testing correction analysis
            H5 = H5 File
            Parent = Parent windows
        """
        self.parent = parent
        self.file = tables.openFile(H5,'r')
        self.TFDict=TF
        self.SpaceContDict=SpaceCont
        if SpaceFile is not None:
            self.__MatrixDist__(SpaceFile)
        else:
            self.Distance=np.array([[-1]])
        self.AlphaDict=Alpha
    def __MatrixDist__(self,SpaceFile):
        if SpaceFile.split('.')[-1]=='xyz':
            Data=np.loadtxt(SpaceFile,dtype='string',skiprows=1)
        else:
            Data=np.loadtxt(SpaceFile,dtype='string')
        if Data.shape[1]>3:
            Label=Data[:,3]
        else:
            Label=['']
        Coordonee=np.float64(Data[:,0:3])
        NbPoint=Coordonee.shape[0]
        MatrixDist=np.zeros((NbPoint,NbPoint))
        for v in range(NbPoint):
            dist=Coordonee-Coordonee[v,:]
            dist=dist*dist
            dist=dist.sum(1)
            dist=np.sqrt(dist)
            MatrixDist[v,:]=dist
        self.Distance=MatrixDist
    def __MathematicalMorphology__(self,Dilate=True):
        """Calulation of the Mathematical Morphology (Erosion and Dilatation)
            The infromation like BinaryData, Number on Conseq TF , Number of Contigouis points, and the Amtrix Distance are in self
         """
        if self.TF ==1 and self.SpaceCont==1:
            print('1')
            Mask=self.BinaryData
            print(self.BinaryData.sum())
        else:
            # Definition of problematic time point that correspond to time border
            if Dilate:
                print('Dilate')
                print(self.BinaryData.sum())
            else:
                print('Erode')
                print(self.BinaryData.sum())
            TimeStart = (self.TF - 1) / 2
            TimeEnd = self.TF - TimeStart
            # creation of a Mask of 0 and size of the Bianary Data
            Mask = np.zeros(self.BinaryData.shape)
            # Mathematical morphlogy calculation
            if self.BinaryData.sum() != 0:# if their is no significant point we don't need mathematical morphology
                #loop over all time point
                for time in range(self.BinaryData.shape[0]):
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
                        if self.Distance[0,0]==-1: # no correction
                            element = self.BinaryData[BeginTime:EndTime,dim]==1
                        else:
                            space = self.Distance[dim, :]
                            # sort these distance and extract the index from the colser (itself) to the farer
                            space = space.argsort()
                            # keep only the pn poitns correcponding to the criteria choosen by the user
                            space = space[0:self.SpaceCont]
                            # element is a subset of interest containting the time and the sapce of interest
                            # element is a boolean subset where true means significatif points and 0 means no significative points
                            element = self.BinaryData[BeginTime:EndTime, space] ==1
                        if Dilate:# dilatatioon
                            if element.any():
                                # if at least one point in element is significant mask at time =time and space =dim => 1 else leave 0
                                Mask[time,dim]=1
                        else: #Erosion
                            if element.all():
                                # if all poitns of element = 1 mask at time =time and space =dim => 1  else leave a 0
                                Mask[time, dim]=1
                        pourcent = str(100.0 * (self.n) / (self.NbCalcul))
                        
                        pourcent = pourcent[0:pourcent.find('.') + 3]
                        if float(pourcent)>100:
                            pourcent='100'
                            self.n=self.NbCalcul
                        self.dlg.Update(self.n, " ".join(['Progression  :',
                                               pourcent, ' %']))
                        self.n += 1
        self.Mask=Mask

    def Calculation(self):
        """
            Calucualtion of mathematical morpholgy on all results anova and PostHoc
            TF = Number of consecutive Time frame entered by usr
            Alpha = Statistical Thesjold Difine by usr
            SpaceCont = Contigous space point define by usr
            SpaceFiel File with 3d coodonate to determine distance

        """
        ResultType={'Anova.GFP':'/Result/GFP/Anova','Anova.Electrodes':'/Result/All/Anova',
                    'PostHoc.GFP':'/Result/GFP/PostHoc','PostHoc.Electrodes':'/Result/All/PostHoc'}
        self.CorrectedMask={}
        for r in ResultType:
            res=self.file.getNode(ResultType[r])
            if len(res)>0:
                ShapeOriginalData=self.file.getNode('/Shape').read()
                # extrating infromion usefull
                # used for user interface feed back
                # number of terms in Anova or in PostHoc mulipled by the number of TF* number of space point muliply * 2(Erosion/Dilatation)
                self.NbCalcul=2*ShapeOriginalData.prod()
                #Dictionary Correction Anova Contain the mask of All Anova Mask Keys = statistical Condition name
                self.dlg = wx.ProgressDialog(
                                'Multiple Test Correction for '+r,
                                'Calculation in progress : 0 %',
                                self.NbCalcul, parent=self.parent,
                                style=wx.PD_AUTO_HIDE | wx.PD_REMAINING_TIME)
                self.dlg.SetSize((200, 130))
                tmp={}
                print(res)
                for v in res:
                    self.n=0
                    FolderName=r.split('.')[0]
                    try:
                        os.mkdir(self.resultFolder+'\\'+FolderName)
                    except:
                        pass
                    P=v['P']
                    Name=v['StatEffect']
                    CorrectedMask={}
                    # adapt the conseutive number of time frame and the contigous criteria to the length o Data
                    # in case of the user made a mistake.
                    # if their is only one TF we cannot have a TF value !=1
                    # same remark for the contigous criteria
                    if P.shape[0]==1:
                        self.TF=1
                    else:
                        self.TF=self.TFDict[FolderName]
                    
                    if P.shape[1] == 1: 
                        self.SpaceCont = 1
                    else:
                        self.SpaceCont=self.SpaceContDict[FolderName]
                    # we compute an openning more restrictive that means errosion folwed by a dilatation
                    # the BinaryData is all the pvalue lower than Alpha
                    self.BinaryData=np.zeros(P.shape)
                    print('init')
                    print(self.AlphaDict[FolderName])
                    self.BinaryData[P<self.AlphaDict[FolderName]]=1
                    print(self.BinaryData.sum())
                    # Dilatation
                    self.__MathematicalMorphology__(Dilate=False)
                    # the BinaryData is the Mask the come from the errosion
                    self.BinaryData=self.Mask
                    # Erosion
                    self.__MathematicalMorphology__(Dilate=True)
                    tmp[Name]=self.Mask
                # Corrected Mask is a Dicionary tha containe all the binarymask
                self.CorrectedMask[r]=tmp
                self.dlg.Destroy()
        self.file.close()
       
class WriteData:
    def __init__(self,ResultFolder,H5,Param,DataGFP=False):
        #Type = Param/Non Param
        self.resultFolder=ResultFolder
        self.file = tables.openFile(H5,'a')
        self.DataGFP=DataGFP
        self.Param=Param
    def StatistcalData(self,CorrectedMask):
        """write Staristicla Data using
            the multiple testing mask
            and raw statistical information in h5"""
        
        # Extract Results check
        ResultType={'Anova.GFP':'/Result/GFP/Anova','Anova.Electrodes':'/Result/All/Anova',
                    'PostHoc.GFP':'/Result/GFP/PostHoc','PostHoc.Electrodes':'/Result/All/PostHoc'}
        for r in ResultType:
            res=self.file.getNode(ResultType[r])
            for v in res:
                FolderName=r.split('.')[0]
                try:
                    os.mkdir(self.resultFolder+'\\'+FolderName)
                except:
                    pass
                Term=v['StatEffect']
                P=1-v['P']
                if r.split('.')[0]=='Anova':#  partial eta square
                    stat=v['F']
                    ext='.F.eph'
                else:# R squared
                    stat=v['T']
                    ext='.t.eph'
                self.TF=P.shape[0]
                self.Electrodes=P.shape[1]
                self.Fs=self.file.getNode('/Data/Header')[2]
                # name based on GFP or Parametric
                Name=[r]
                # name based on GFP or Parametric
                Name.append(Term)
                if self.Param[FolderName]:
                    Name.append('Param')
                else:
                    Name.append('NonParam')
                if self.DataGFP:
                    Name.append('GFP')
                else:
                    if self.Electrodes<500:
                        Name.append('El')
                    else:
                         Name.append('IS')
                Name.append('P.eph')
                Name=".".join(Name)
                self.Data=P*CorrectedMask[r][Term]
                self.__WriteEph__(self.resultFolder+'\\'+FolderName+'\\'+Name)
                self.Data=stat*CorrectedMask[r][Term]
                self.__WriteEph__(self.resultFolder+'\\'+FolderName+'\\'+Name.replace('.P.eph',ext))
     
    def IntermediateResult(self):
        """Write intermediate Result"""
        
        try:
            os.mkdir(self.resultFolder+'\IntermediateResults')
        except:
            pass
        # Extract Effectsize
        self.__EfectSize__('IntermediateResults')
        if self.DataGFP:
            Intermediate=self.file.getNode('/Result/GFP/IntermediateResult')
        else:
            Intermediate=self.file.getNode('/Result/All/IntermediateResult')
        if len(Intermediate)>0:
            for t in Intermediate:
                tmp=t['Data']
                self.TF=tmp.shape[0]
                self.Electrodes=tmp.shape[1]
                self.Data=tmp
                self.__WriteEph__(self.resultFolder+'\IntermediateResults\\'+t['CondName']+'.'+t['Type']+'.eph')
        else:
            newRow = Intermediate.row
            # use PostHoc Function to extract combination
            self.__Combination__()
            if self.DataGFP:
                Data=self.file.getNode('/Data/GFP')
            else:
                Data=self.file.getNode('/Data/All')
            # calculation mean and SE for non covariate Arrangegment
            DataShape=self.file.getNode('/Shape')
            self.Fs=self.file.getNode('/Data/Header')[2]
            # idx to ovoid memory problem and acces only part of the datas
            idx=np.arange(Data.shape[1])
            for ar in self.Arrangement:
                if ar!='Simple Regression':
                    Mean=Data[:,idx[self.Arrangement[ar]]].mean(axis=1)
                    Se=(Data[:,idx[self.Arrangement[ar]]].std(axis=1))/(np.sqrt(self.Arrangement[ar].sum()))
                    if self.DataGFP==False:
                        Mean=Mean.reshape(DataShape)
                        Se=Se.reshape(DataShape)
                    else:
                        Mean=Mean.reshape((Mean.shape[0],1))
                        Se=Se.reshape((Se.shape[0],1))
                    self.TF=Mean.shape[0]
                    self.Electrodes=Mean.shape[1]
                    self.Data=Mean
                    newRow['Data'] = Mean
                    newRow['Type'] = 'mean'
                    newRow['CondName']=ar
                    newRow.append()
                    self.__WriteEph__(self.resultFolder+'\IntermediateResults\\'+ar+'.mean.eph')
                    self.Data=Se
                    newRow['Data'] = Se
                    newRow['Type'] = 'Se'
                    newRow['CondName']=ar
                    newRow.append()
                    self.__WriteEph__(self.resultFolder+'\IntermediateResults\\'+ar+'.Se.eph')
                # calculation R for covariate Arrangegment
            for c in self.Covariate:
                CovData= self.Covariate[c]
                for ar in self.Arrangement:
                    
                    covtmp=CovData[self.Arrangement[ar]]
                    datatmp=Data[:,idx[self.Arrangement[ar]]]
                    R=[]
                    for d in datatmp:
                        R.append(np.corrcoef(d,covtmp)[0,1])
                    R=np.array(R)
                    if self.DataGFP==False:
                        R=R.reshape(DataShape)
                    else:
                        R=R.reshape((R.shape[0],1))
                    self.TF=R.shape[0]
                    self.Electrodes=R.shape[1]
                    self.Data=R
                    newRow['Data'] = R
                    newRow['Type'] = 'R'
                    newRow['CondName']=ar+'_'+c
                    newRow.append()
                    self.__WriteEph__(self.resultFolder+'\IntermediateResults\\'+ar+'_'+c+'.R.eph')
    def __Combination__(self):
        """
        Reading use H5 File to extract all combination
        for intermediate results inspired by Posthoc instat.py
        """
        # Numerical Factor Information from the Datatable
        tableFactor = self.file.getNode('/Model').read()

        # Extraction of relevant factor information from tableFactor
        between = {}
        within = {}
        betweenName = []
        withinName = []
        self.Covariate={}
        CovariateName=[]
        # Generating within and between dictionary with condition name
        for t in tableFactor:
            factorName = t[0]
            factorType = t[1]
            factorData = t[2]
            if factorType == 'Between':
                between[factorName] = factorData
                betweenName.append(factorName)
            elif factorType == 'Within':
                within[factorName] = factorData
                withinName.append(factorName)
            elif factorType == 'Covariate':
                self.Covariate[factorName]=factorData
                CovariateName.append(factorName)
            elif factorType == 'Subject':
                subject = factorData
                self.subject = subject

        # Transform dict into matrix for easy use
        within = np.array(within.values())
        between = np.array(between.values())

        # Extract different levels for each between subject factor
        existingCombi = []
        # Between subject factor Exist
        if between !=[]: 
            levelsBetween = between.max(axis=1).astype('int')
             # Cacluate all possible combinations using the max number of levels
            allCombinationBetween = itertools.product(
                range(1, levelsBetween.max() + 1), repeat=len(levelsBetween))

            # Reduce combination to only existing ones
            
            for c in allCombinationBetween:
                combinations = np.array(c)
                # existing combinations
                if (levelsBetween - combinations < 0).sum() == 0:
                    existingCombi.append(combinations)
        else:
            existingCombi.append(between)
        existingCombi = np.array(existingCombi)
        

       

        # Create all possible combinations and extract the booleans
        # corresponding to it.
        allCombiBool = {}
        condName = []
        for e in existingCombi:
            boolBetween = []
            tmpNameBetween = []
            for c, l in enumerate(e):
                boolBetween.append(between[c, :] == l)
                tmpNameBetween.append("-".join([betweenName[c],
                                      str(int(l))]))
            boolBetween = np.array(boolBetween)
            if within!=[]:
                withinCombi = within[:,subject == 1].T
            else:
                withinCombi=[within]
            for w in withinCombi:
                boolWithin = []
                tmpNameWithin = []
                for c, l in enumerate(w):
                    boolWithin.append(within[c, :] == l)
                    tmpNameWithin.append("-".join([withinName[c],
                                         str(int(l))]))
                boolWithin = np.array(boolWithin)
                # we have betwenn and within subject Factor
                if between!=[] and within !=[]:
                    print('1')
                    bools = np.append(boolBetween, boolWithin, axis=0)
                    # name of the arrangement
                    tmpName = ".".join([".".join(tmpNameBetween),
                                        ".".join(tmpNameWithin)])
                # Only Between subject factor
                elif between!=[]:
                    print('2')
                    bools = boolBetween
                    # name of the arrangement
                    tmpName = ".".join(tmpNameBetween)
                # Only Within subject factor
                elif within !=[]:
                    print('3')
                    bools = boolWithin
                    # name of the arrangement
                    tmpName = ".".join(tmpNameWithin)
                else:
                    bools=subject>-1
                    bools=bools.reshape((1,len(bools)))
                    tmpName='Simple Regression'
                condName.append(tmpName)
                allCombiBool[tmpName] = bools.prod(axis=0) == 1


        # Dictionary of boolean correcponding to all arangements
        self.Arrangement = allCombiBool
    def __WriteEph__(self,FileName):
        """ write Eph File"""
        File=open(FileName,"w")
        # on prend le header
        header=[str(self.Electrodes),'\t',str(self.TF),'\t',str(self.Fs),'\n']
        #ecrtiture du header
        File.write("".join(header))
        # boucle sur les time chaque ligne est un temps
        for time in self.Data:
            #ecriture ligne par ligne
            time.tofile(File,sep='\t',format="%s")
            #saut de ligne
            File.write('\n')
        File.close()
    def __EfectSize__(self,SubFolder):
        """ Calulate partila eta square for anova
            or Rsquare for T-test PostHoc"""
        ResultType={'Anova.GFP':'/Result/GFP/Anova','Anova.Electrodes':'/Result/All/Anova',
                    'PostHoc.GFP':'/Result/GFP/PostHoc','PostHoc.Electrodes':'/Result/All/PostHoc'}
        for r in ResultType:
            res=self.file.getNode(ResultType[r])
            for v in res:
                try:
                    os.mkdir(self.resultFolder+'\\'+SubFolder+'\EffectSize')
                except:
                    pass
                Term=v['StatEffect']
                
                Df=v['Df']
                
                # name based on GFP or Parametric
               
                # name based on GFP or Parametric
                if r.split('.')[0]=='Anova':#  partial eta square
                    Name=['Partial-Eta-Square']
                    F=v['F']
                    EffectSize=(F*Df[0])/((F*Df[0])+Df[1])
                else:# R squared
                    Name=['R-Square']
                    T=v['T']
                    EffectSize=(T*T)/((T*T)+Df[0])
                self.TF=EffectSize.shape[0]
                self.Electrodes=EffectSize.shape[1]
                self.Fs=self.file.getNode('/Data/Header')[2]
                Name.append(Term)
                if self.Param[r.split('.')[0]]:
                    Name.append('Param')
                else:
                    Name.append('NonParam')
                if self.DataGFP:
                    Name.append('GFP')
                else:
                    if self.Electrodes<500:
                        Name.append('El')
                    else:
                         Name.append('IS')
                Name.append('.eph')
                Name=".".join(Name)
                
                self.Data=EffectSize
                self.__WriteEph__(self.resultFolder+'\\'+SubFolder+'\EffectSize\\'+Name)                 
