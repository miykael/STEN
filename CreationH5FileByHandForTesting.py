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


##/Result/GPF/PostHoc
import tables
import CartoolFiles as cf
import glob
import numpy as np
import xlrd

Path='C:\Users\jknebel\Documents\NAC\Article Std Only\Data-GM'
XlsFile='C:\Users\jknebel\Documents\NAC\Article Std Only\Data-GM\\Data.xls'
H5File='C:\Users\jknebel\Documents\python\PyProject\STEN\\TestData\SimulatedData.h5'
EphFile=np.array(glob.glob("\\".join([Path,'*.avg.eph'])))
wb=xlrd.open_workbook(XlsFile)
sh=wb.sheet_by_name('feuille 1')
Ratio=np.float64(sh.col_values(1))
### Creation by hand of the grid Data

# Simulation of reading grid
DataColSubject=np.arange(1,52)
DataColF1=EphFile
np.random.shuffle(EphFile)
DatColF2=EphFile
DataColGroup=np.append(np.ones(30),2*np.ones(21))
DatColRatio=Ratio

# Geneating a Dict containing the grid info with artifical col name coming from grid
InfoDict={'Subject':DataColSubject,'F1':DataColF1,'F2':DataColF1,'Group':DataColGroup,'Ratio':DatColRatio}
NbLine=len(DataColSubject)
# simulation difine factor
Level=np.array([2])
# Creation of Factor Definition for R by hand
AllEph=np.append(DataColF1,DatColF2)
SubjectFactor=np.append(DataColSubject,DataColSubject)
Covariate=np.append(DatColRatio,DatColRatio)
Between=np.append(DataColGroup,DataColGroup)
Within=np.append(np.ones(51),2*np.ones(51))
# factor Name coming from selecting factor
SubjectName={'Subject':SubjectFactor}
BetweeName={'Group':Between}
CovariateName={'Ratio':Covariate}
WithinName={'Cond':Within}
AllFactor={'Subject':SubjectName,'Between':BetweeName,'Covariate':CovariateName,'Within':WithinName}
# Creation H5 File and differnt group
H5=tables.openFile(H5File,'w')
DataGroup=H5.createGroup('/','Data')
ResultGrp=H5.createGroup('/','Result')
AllRes=H5.createGroup(ResultGrp,'All')
GFPRes=H5.createGroup(ResultGrp,'GFP')
# read one file to extract TF and Electrod info
TF=cf.Eph(AllEph[0]).TF
Electrodes=cf.Eph(AllEph[0]).Electrodes
AllData=H5.createEArray(DataGroup,'All',tables.Float64Atom(),(TF*Electrodes,0))
GFPData=H5.createEArray(DataGroup,'GFP',tables.Float64Atom(),(TF,0))
# Reading EphFile dans store into Tables with EArray
for e in AllEph:
    dat=cf.Eph(e)
    AllData.append(dat.Data.reshape(np.array(dat.Data.shape).prod(),1))
    GFPData.append(dat.GFP.reshape(TF,1))
ShapeOriginalData=H5.createArray('/','Shape',np.array(dat.Data.shape))

ModelParticle = {'Name': tables.StringCol(40),'Value': tables.Int32Col(shape=len(SubjectFactor)),'Type':tables.StringCol(40)}
InfoParticle={}
for c in InfoDict:
    InfoParticle[c]=tables.StringCol(256)

AnovaAllParticle={'StatEffect':tables.StringCol(40),'P':tables.Float64Col(shape=(TF,Electrodes)),'F':tables.Float64Col(shape=(TF,Electrodes))}
AnovaGFPParticle={'StatEffect':tables.StringCol(40),'P':tables.Float64Col(shape=(TF,1)),'F':tables.Float64Col(shape=(TF,1))}
PostHocAllParticle={'Name':tables.StringCol(60),'P':tables.Float64Col(shape=(TF,Electrodes)),'T':tables.Float64Col(shape=(TF,Electrodes))}
PostHocGFPParticle={'Name':tables.StringCol(60),'P':tables.Float64Col(shape=(TF,1)),'T':tables.Float64Col(shape=(TF,1))}

IntermediateResultAllParticle={'CondName':tables.StringCol(40),'Type':tables.StringCol(40),'Data':tables.Float64Col(shape=(TF,Electrodes))}
IntermediateResultGFPParticle={'CondName':tables.StringCol(40),'Type':tables.StringCol(40),'Data':tables.Float64Col(shape=(TF,1))}
# crating tables for model
TablesModel=H5.createTable('/','Model',ModelParticle)
# writing Model informations
NewRow=TablesModel.row
for t in AllFactor:
    for n in AllFactor[t]:
        NewRow['Name']=n
        NewRow['Value']=AllFactor[t][n]
        NewRow['Type']=t
        NewRow.append()
TablesModel.flush()

# Creating info Table
TablesInfo=H5.createTable('/','Info',InfoParticle)
# writing Model informations
NewRow=TablesInfo.row
for l in range(NbLine):
    for c in InfoDict:
        NewRow[c]=InfoDict[c][l]
    NewRow.append()
TablesInfo.flush()
# Creating allResultTables
TablesRes=H5.createTable(AllRes,'Anova',AnovaAllParticle)
TablesRes=H5.createTable(AllRes,'IntermediateResult',AnovaGFPParticle)
TablesRes=H5.createTable(AllRes,'PostHoc',PostHocAllParticle)
TablesRes=H5.createTable(GFPRes,'Anova',IntermediateResultAllParticle)
TablesRes=H5.createTable(GFPRes,'IntermediateResult',IntermediateResultGFPParticle)
TablesRes=H5.createTable(GFPRes,'PostHoc',PostHocGFPParticle)
H5.close()
H5=tables.openFile(H5File,'a')
