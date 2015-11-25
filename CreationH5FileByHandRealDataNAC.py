##Tables definition
##
##tables:
##/Data/All #using createEArray('/','AllData',tables.Float64Atom(),(NbPoints,0))
##/Shape # shape of AllData (TF,Electrodes)
##/Data/GFP #using createEArray('/','AllData',tables.Float64Atom(),(NbPoints,0))
##/Model #using a tables with col= {Name of the factor, Value of factor (Vector), type of Factor (Within,between, covariate, subject)
##/Info # using a tables that contain all the information in the "ExcelSheet"
##/Result/All/Anova # Tables with col ={Name of the effect (i.e main effect, interaction, ..),1-p Data(Without any threshold (alpha, consecpoits, ...),F Data}
##/Result/All/IntermediateResult # Tabes with Col = {Condition name, Type (Mean,pearson correaltion,Sandard error,...),Data Corresponding in Type}
##/Result/GFP/Anova # Tables with col ={Name of the effect (i.e main effect, interaction, ..),1-p Data(Without any threshold (alpha, consecpoits, ...),F Data}
##/Result/GFP/IntermediateResult # Tabes with Col = {Condition name, Type (Mean,pearson correaltion,Sandard error,...)}
import tables
import CartoolFiles as cf
import glob
import numpy as np
import xlrd

XlsFile='C:\Users\jknebel\Documents\NAC\Article Std Only\Data-GM\\sten.xls'
H5File='C:\Users\jknebel\Documents\python\PyProject\STEN\\TestData\NACData.h5'
wb=xlrd.open_workbook(XlsFile)
sh=wb.sheet_by_name('STEN')
AllEph=sh.col_values(0)
Ratio=np.float64(sh.col_values(1))
Between=np.int64(np.float64(sh.col_values(2)))
Subject=np.int64(np.float64(sh.col_values(3)))
### Creation by hand of the grid Data
# Geneating a Dict containing the grid info with artifical col name coming from grid
InfoDict={'Subject':Subject,'Group':Between,'Ratio':Ratio}
# factor Name coming from selecting factor
SubjectName={'Subject':Subject}
BetweeName={'Group':Between}
CovariateName={'Ratio':Ratio}
AllFactor={'Subject':SubjectName,'Between':BetweeName,'Covariate':CovariateName}
# Creation H5 File and differnt group
H5=tables.openFile(H5File,'w')
DataGroup=H5.createGroup('/','Data')
ResultGrp=H5.createGroup('/','Result')
AllRes=H5.createGroup(ResultGrp,'All')
GFPRes=H5.createGroup(ResultGrp,'GFP')
# read one file to extract TF and Electrod info
TF=cf.Eph(AllEph[0]).TF
Electrodes=cf.Eph(AllEph[0]).Electrodes
NBpoints=TF*Electrodes
shape=np.array([TF,Electrodes])
Shape=H5.createArray('/','Shape',shape)
AllData=H5.createEArray(DataGroup,'All',tables.Float64Atom(),(NBpoints,0))
GFPData=H5.createEArray(DataGroup,'GFP',tables.Float64Atom(),(TF,0))
## Reading EphFile dans store into Tables with EArray
for e in AllEph:
    dat=cf.Eph(e)
    AllData.append(dat.Data.reshape((dat.TF*dat.Electrodes,1)))
    GFPData.append(dat.GFP.reshape((dat.TF,1)))



ModelParticle = {'Name': tables.StringCol(40),'Value': tables.Int32Col(shape=len(Subject)),'Type':tables.StringCol(40)}
InfoParticle={}
for c in InfoDict:
    InfoParticle[c]=tables.StringCol(256)

AnovaAllParticle={'StatEffect':tables.StringCol(40),'P':tables.Float64Col(shape=(TF,Electrodes)),'F':tables.Float64Col(shape=(TF,Electrodes))}
AnovaGFPParticle={'StatEffect':tables.StringCol(40),'P':tables.Float64Col(shape=(TF,1)),'F':tables.Float64Col(shape=(TF,1))}

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
NbLine=len(Subject)
for l in range(NbLine):
    for c in InfoDict:
        NewRow[c]=InfoDict[c][l]
    NewRow.append()
TablesInfo.flush()
# Creating allResultTables
TablesRes=H5.createTable(AllRes,'Anova',AnovaAllParticle)
TablesRes=H5.createTable(AllRes,'IntermediateResult',AnovaGFPParticle)
TablesRes=H5.createTable(GFPRes,'Anova',IntermediateResultAllParticle)
TablesRes=H5.createTable(GFPRes,'IntermediateResult',IntermediateResultGFPParticle)
H5.close()
H5=tables.openFile(H5File,'a')
