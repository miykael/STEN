import wx
import wx.lib.sheet as sheet
import pickle
import numpy as np
import glob as ls
import os
import tables
import Stat
##tables: /Data/*subject/*condition # array
##        /DataGFP/*subject/*condition # array
##        /Model/Within # array
##        /Model/Between # array
##        /Model/Covariate # array
##        /Model/Subject # array
##        /Names/Within # List
##        /Names/Between
##        /Names/Covariate
##        /Info/Shape
##        /Info/FS # frequncy sampling
##        /Info/level # array
##        /Info/ColFactor
##        /Info/ColWithin
##        /Info/ColBetween
##        /Info/ColCovaraite
##        /Info/Param # info si parametric ou non
##        /Sheet/Value # list
##        /Sheet/NoEmptyCol # array
##        /Sheet/ColName # list
##        /Sheet/Dim # array
##        /Error/EPH
##        /Result/Anova/All/P # P value for All electrodes and IS
##        /Result/Anova/All/F # F value only in parametric
##        /Result/Anova/GFP/P # P value for GFP
##        /Result/Anova/GFP/F # F value 
##        /Result/PostHoc/All/P # P value for All electrodes and IS
##        /Result/PostHoc/All/T # T value 
##        /Result/PostHoc/GFP/P # P value for GFP
##        /Result/PostHoc/GFP/T # T value
##        /Result/IntermediateResult # place for storing intermediate results
class info(wx.Panel):
        """ Panle de gauche de l'application demande les dossier EPH, résultats, les facteurs, ...."""
        def __init__(self,Conteneur,Main):
                #wx.Frame.__init__(self, None, -1, title = "test", size = (500,300))
                wx.Panel.__init__(self,parent = Conteneur)
                FrameSizer=wx.BoxSizer(wx.VERTICAL)
                #definition des OutPut
                self.PathResult = None
                self.NbFactor = 0
                self.Level = {}
                self.Analyse= None
                self.Main=Conteneur
                self.ExportData=Main
                self.ExportData.H5=[]
                # panel 1 = folders
                ##############
                # définition panel 1 
                self.PanelFichier=wx.Panel(self,-1)
                PanelFichierSizer=wx.BoxSizer(wx.VERTICAL)
                PanelFichierSizer.AddSpacer(20)
                
                # selection Load old file
                PanelLoad=wx.Panel(self.PanelFichier,-1)
                PanelLoadSizer=wx.BoxSizer(wx.HORIZONTAL)
                PanelLoadSizer.AddSpacer(5)
                self.DataFile=wx.TextCtrl(PanelLoad,-1,value="",style =wx.TE_READONLY,size=(550,21))
                self.DataFile.SetBackgroundColour(wx.WHITE)
                PanelLoadSizer.Add(self.DataFile,0,wx.EXPAND)
                ButtonDataLoad=wx.Button(PanelLoad,4,label ="Load File",size=(108,23))
                PanelLoadSizer.Add(ButtonDataLoad,0,wx.EXPAND)
                PanelLoad.SetSizer(PanelLoadSizer)
                PanelFichierSizer.Add(PanelLoad,0,wx.EXPAND)
                PanelFichierSizer.AddSpacer(10)
                
                #  selection result folder
                PanelRes=wx.Panel(self.PanelFichier,-1)
                PanelResSizer=wx.BoxSizer(wx.HORIZONTAL)
                PanelResSizer.AddSpacer(5)
                self.TextResult=wx.TextCtrl(PanelRes,-1,value="",style =wx.TE_READONLY,size=(550,21))
                self.TextResult.SetBackgroundColour(wx.WHITE)
                PanelResSizer.Add(self.TextResult,0,wx.EXPAND)
                self.ButtonResult=wx.Button(PanelRes,2,label ="Select result folder", size=(108,23))
                PanelResSizer.Add(self.ButtonResult,0,wx.EXPAND)
                PanelRes.SetSizer(PanelResSizer)
                PanelFichierSizer.Add(PanelRes,0,wx.EXPAND)
                PanelFichierSizer.AddSpacer(10)
                
                # lie les sizer au panel
                self.PanelFichier.SetSizer(PanelFichierSizer)
                # on mets le panel de fichier dans le sizer de la frame
                FrameSizer.Add(self.PanelFichier,0,wx.EXPAND)
                FrameSizer.AddSpacer(10)

                ###############
                # panel 2 = INfo avec creation Data + information sur les datas
                #text data
                PanelInfo=wx.Panel(self,-1)
                InfoSizer=wx.BoxSizer(wx.HORIZONTAL)
                InfoSizer.AddSpacer(5)
                PanelData=wx.Panel(PanelInfo,-1)
                DataSizer=wx.BoxSizer(wx.VERTICAL)
                DataTxt=wx.StaticText(PanelData,-1,label = "Data selection ",style=wx.CENTRE)
                DataSizer.Add(DataTxt,0,wx.EXPAND)
                DataSizer.AddSpacer(5)
                # panel 3 avec les boutton création
                ButtonDataCreate=wx.Button(PanelData,3,label ="Create Data File / Modifiy data")
                DataSizer.Add(ButtonDataCreate,0,wx.EXPAND)
                PanelData.SetSizer(DataSizer)
                InfoSizer.Add(PanelData)
                InfoSizer.AddSpacer(100)
                self.TxtInfo=wx.StaticText(PanelInfo,-1,label="",style=wx.ALIGN_LEFT)
                InfoSizer.Add(self.TxtInfo)
                PanelInfo.SetSizer(InfoSizer)
                # lie les sizer au panel
                FrameSizer.Add(PanelInfo,0,wx.EXPAND)
                FrameSizer.AddStretchSpacer()

                #Panel Progression
                PanelFinal=wx.Panel(self,-1)
                FinalSizer=wx.BoxSizer(wx.HORIZONTAL)
                FinalSizer.AddSpacer(50)
                self.ProgressTxt=wx.StaticText(PanelFinal,-1,label = "",style=wx.ALIGN_LEFT)
                FinalSizer.Add(self.ProgressTxt,0, wx.EXPAND)
                PanelFinal.SetSizer(FinalSizer)
               

                # lie les sizer au panel
                FrameSizer.Add(PanelFinal,0,wx.EXPAND)
                FrameSizer.AddStretchSpacer()
                #on lie le size au frame sizer
                self.SetSizer(FrameSizer)
                #FrameSizer.SetSizeHints(self)
                #self.SetSize((800,200))

                
                
                
                # evenement
                # wx.EVT_BUTTON(self, 1,self.Eph)
                wx.EVT_BUTTON(self, 2,self.Result)
                wx.EVT_BUTTON(self, 3,self.CreateData)
                wx.EVT_BUTTON(self, 4,self.LoadData)
         
        def Result(self, event):
                self.TextResult.SetBackgroundColour(wx.WHITE)
                wx.InitAllImageHandlers()
                dlg = wx.DirDialog(None, "select Result folder",defaultPath = os.getcwd(),style = wx.DD_DEFAULT_STYLE)
                retour = dlg.ShowModal()
                self.PathResult = dlg.GetPath()
                os.chdir(self.PathResult)
                self.TextResult.SetLabel(dlg.GetPath())
                dlg.Show(True)
                dlg.Destroy()
        def LoadData(self, event):
                dlg = wx.FileDialog(None, "Load H5 file",wildcard = "*.h5",style = wx.FD_OPEN)
                text=[]
                retour = dlg.ShowModal()
                if retour==wx.ID_OK:
                        chemin = dlg.GetPath()
                        fichier = dlg.GetFilename()
                        self.DataFile.SetLabel(chemin)
                        self.ExportData.H5=chemin
                        dlg.Destroy()
                        dlg.Show(True)
                        info=ReturnInfomation(chemin)
                        self.TxtInfo.SetLabel("".join(info.text))
                        if info.CovariatePresent:
                                self.ExportData.AnovaWave.PostHocCheckBox.Disable()
                                self.ExportData.AnovaIS.PostHocCheckBox.Disable()
                                self.ExportData.AnovaWave.PostHocCheckBox.SetValue(False)
                                self.ExportData.AnovaIS.PostHocCheckBox.SetValue(False)
                                
                        else:
                                self.ExportData.AnovaWave.PostHocCheckBox.Enable()
                                self.ExportData.AnovaIS.PostHocCheckBox.Enable()
                        
                else:
                        self.ExportData.H5=[]
                        self.DataFile.SetLabel('')
        def CreateData(self, event):
                Data=DataEntry(self)
                Data.Show(True)
                self.ExportData.Show(False)
class DataEntry(wx.Frame):
        """ feuille de clacul sytle SPSS"""
        def __init__(self,Parent):
                wx.Frame.__init__(self, None,1,title = "DATA ENTRY",style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
                FrameSizer=wx.BoxSizer(wx.VERTICAL)
                self.save=False
                self.info=Parent
                self.ExportData=Parent.ExportData
                #feuille de clacul style XLS)
                PanelData=wx.Panel(self,-1)
                DataSizer=wx.BoxSizer(wx.HORIZONTAL)
                PanelSheet=wx.Panel(PanelData,-1)
                SheetSizer=wx.BoxSizer(wx.VERTICAL)
                SheetSizer.AddSpacer(10)
                PanelCellContent=wx.Panel(PanelSheet,-1)
                CellContentSizer=wx.BoxSizer(wx.HORIZONTAL)
                CellContentSizer.AddSpacer(10)
                CellTxt=wx.StaticText( PanelCellContent,-1,label='Cell Content : ',style=wx.ALIGN_LEFT)
                CellContentSizer.Add(CellTxt,0,wx.EXPAND)
                CellContentSizer.AddSpacer(5)
                self.CellContentTxt=wx.TextCtrl( PanelCellContent,-1,value="",style =wx.TE_READONLY,size=(600,21))
                self.CellContentTxt.SetBackgroundColour(wx.WHITE)
                CellContentSizer.Add(self.CellContentTxt,0,wx.EXPAND)
                PanelCellContent.SetSizer(CellContentSizer)
                SheetSizer.Add(PanelCellContent)
                SheetSizer.AddSpacer(10)
                self.Sheet=CalculSheet(PanelSheet)
                SheetSizer.Add(self.Sheet)
                PanelSheet.SetSizer(SheetSizer)
                DataSizer.Add(PanelSheet,0,wx.EXPAND)
                DataSizer.AddSpacer(10)



                # Panel pour le Drop des fichier
                PanelDrop=wx.Panel(PanelData,-1)
                DropSizer=wx.BoxSizer(wx.HORIZONTAL)
                PanelCol=wx.Panel(PanelDrop,-1)
                ColSizer=wx.BoxSizer(wx.VERTICAL)
                ColSizer.AddSpacer(5)
                # liste des Valeur d'une colone
                self.ColName=wx.StaticText(PanelCol,-1,label='Select One Colon',style=wx.ALIGN_CENTRE)
                ColSizer.Add(self.ColName,0,wx.ALIGN_CENTRE)
                ColSizer.AddSpacer(5)
                self.ColData=wx.ListBox(PanelCol,1,choices="",style=wx.LB_EXTENDED|wx.LB_HSCROLL,size=(190,400))
                ColSizer.Add(self.ColData,0,wx.EXPAND)
                ColSize=self.ColData.GetSize()
                ColSizer.AddSpacer(10)
                self.SortButton=wx.Button(PanelCol,14,label='sort')
                ColSizer.Add(self.SortButton,0,wx.EXPAND)
                ColSize=self.ColData.GetSize()
                ColSizer.AddSpacer(10)
                PanelMove=wx.Panel(PanelCol,-1)
                MoveSizer=wx.BoxSizer(wx.HORIZONTAL)
                self.MoveUpButton=wx.Button(PanelMove,9,label='Move Up')
                MoveSizer.Add(self.MoveUpButton,0,wx.EXPAND)
                MoveSizer.AddSpacer(5)
                self.MoveDownButton=wx.Button(PanelMove,10,label='Move Down')
                MoveSizer.Add(self.MoveDownButton,0,wx.EXPAND)
                PanelMove.SetSizer(MoveSizer)
                ColSizer.Add(PanelMove,0,wx.EXPAND)
                ColSizer.AddSpacer(10)
                self.OKButton=wx.Button(PanelCol,11,label='Add')
                ColSizer.Add(self.OKButton,0,wx.EXPAND)
                PanelCol.SetSizer(ColSizer)
                
                PanelButton=wx.Panel(PanelDrop,-1)
                ButtonSizer=wx.BoxSizer(wx.VERTICAL)
                self.AddButton=wx.Button(PanelButton,12,label='<')
                ButtonSizer.Add(self.AddButton,0,wx.EXPAND)
                ButtonSizer.AddSpacer(10)
                self.RmButton=wx.Button(PanelButton,13,label='>')
                ButtonSizer.Add(self.RmButton,0,wx.EXPAND)
                ButtonSizer.AddSpacer(10)
                self.PanelMove=wx.Panel(PanelButton,-1)
                PanelButton.SetSizer(ButtonSizer)
                # List Conteant tous les eph de PathEpSh
                PanelEph=wx.Panel(PanelDrop,-1)
                EphSizer=wx.BoxSizer(wx.VERTICAL)
                EphSizer.AddSpacer(5)
                txteph=wx.StaticText(PanelEph,-1,label='EPH Files',style=wx.ALIGN_CENTRE)
                EphSizer.Add(txteph,0,wx.EXPAND)
                EphSizer.AddSpacer(5)
                self.DragEph=wx.ListBox(PanelEph,2,choices='',style=wx.LB_EXTENDED|wx.LB_HSCROLL,size=ColSize)
                EphSizer.Add(self.DragEph,0,wx.EXPAND)
                EphSizer.AddSpacer(5)
                # selection Eph folder
                self.ButtonEph=wx.Button(PanelEph,15,label ="Select Folder",size=(190,23))
                EphSizer.Add(self.ButtonEph,0,wx.EXPAND)
                EphSizer.AddSpacer(5)
                FolderTxT=wx.StaticText(PanelEph,-1,label='Current Folder :',style=wx.ALIGN_LEFT,size=(190,21))
                EphSizer.Add(FolderTxT,0,wx.EXPAND)
                EphSizer.AddSpacer(5)
                self.TextEph=wx.TextCtrl(PanelEph,-1,value="",style =wx.TE_READONLY, size=(190,21))
                self.TextEph.SetBackgroundColour(wx.WHITE)
                EphSizer.Add(self.TextEph,0,wx.EXPAND)
                EphSizer.AddSpacer(5)
                FilterTxT=wx.StaticText(PanelEph,-1,label='Filter :',style=wx.ALIGN_LEFT,size=(190,21))
                EphSizer.Add(FilterTxT,0,wx.EXPAND)
                EphSizer.AddSpacer(5)
                self.TextFilter=wx.TextCtrl(PanelEph,3,value="",style=wx.TE_PROCESS_ENTER,size=(190,21))
                self.TextFilter.SetBackgroundColour(wx.WHITE)
                self.TextFilter.Disable()
                EphSizer.Add(self.TextFilter,0,wx.EXPAND)
                PanelEph.SetSizer(EphSizer)
                DropSizer.Add(PanelCol,0,wx.EXPAND)
                DropSizer.AddSpacer(5)
                DropSizer.Add(PanelButton,0,wx.CENTER)
                DropSizer.AddSpacer(5)
                DropSizer.Add(PanelEph,0,wx.EXPAND)
                DropSizer.AddSpacer(10)
                PanelDrop.SetSizer(DropSizer)
                DataSizer.Add(PanelDrop,0,wx.EXPAND)
                PanelData.SetSizer(DataSizer)
                FrameSizer.Add(PanelData,0,wx.EXPAND)
                # on met tous les bouton disable
                self.MoveUpButton.Disable()
                self.MoveDownButton.Disable()
                self.AddButton.Disable()
                self.RmButton.Disable()
                self.OKButton.Disable()
                self.SortButton.Disable()
                # Panel Buttons

                
                PanelButton = wx.Panel(self,-1)
                ButtonSizer = wx.BoxSizer(wx.HORIZONTAL)
                ButtonSizer.AddSpacer(10)
                #sous panel avec le bouton des data
                PanelButtonData = wx.Panel(PanelButton,-1)
                ButtonDataSizer =wx.BoxSizer(wx.HORIZONTAL)
                ButtonDefFactor=wx.Button(PanelButtonData,1,label ="Define Factor")
                ButtonDataSizer.Add(ButtonDefFactor,0,wx.EXPAND)
                ButtonDataSizer.AddSpacer(5)
                
                self.Buttonsave=wx.Button(PanelButtonData,4,label ="Save Data and continue")
                ButtonDataSizer.Add(self.Buttonsave,0,wx.EXPAND)
                ButtonDataSizer.AddSpacer(5)
                PanelButtonData.SetSizer(ButtonDataSizer)
                ButtonSizer.Add(PanelButtonData,0,wx.EXPAND)
                ButtonSizer.AddSpacer(20)
                #Panel changement nom des colons
                PanelChangeCol=wx.Panel(PanelButton,-1)
                ChangeColSizer =wx.BoxSizer(wx.HORIZONTAL)
                ChangeColSizer.AddSpacer(5)
                NbCol=self.Sheet.GetNumberCols()
                self.text=[""]
                for i in range(NbCol):
                        self.text.append(self.Sheet.GetColLabelValue(i))
                TextChangeCol1=wx.StaticText(PanelChangeCol,-1,label ="Name Colon : ")
                ChangeColSizer.Add(TextChangeCol1,0,wx.ALIGN_CENTRE)
                ChangeColSizer.AddSpacer(5)
                
                self.BoxFactor=wx.ComboBox(PanelChangeCol, 1, choices=self.text,style=wx.CB_READONLY)
                ChangeColSizer.Add(self.BoxFactor,0,wx.EXPAND)
                ChangeColSizer.AddSpacer(5)
                
                TextChangeCol2=wx.StaticText(PanelChangeCol,-1,label = "into")
                ChangeColSizer.Add(TextChangeCol2,0,wx.ALIGN_CENTRE)
                ChangeColSizer.AddSpacer(5)
                
                self.NewName=wx.TextCtrl(PanelChangeCol,1,value="")
                ChangeColSizer.Add(self.NewName,0,wx.EXPAND)
                ChangeColSizer.AddSpacer(5)
                
                ButtonChange=wx.Button(PanelChangeCol,5,label ="rename process")
                ChangeColSizer.Add(ButtonChange,0,wx.EXPAND)
                PanelChangeCol.SetSizer(ChangeColSizer)
                ButtonSizer.Add(PanelChangeCol,0,wx.EXPAND)

                
                # Panel insert rows colums
                PanelButton2 = wx.Panel(self,-1)
                ButtonSizer2 = wx.BoxSizer(wx.HORIZONTAL)
                ButtonSizer2.AddSpacer(10)
                PanelInsert=wx.Panel(PanelButton2,-1)
                InsertSizer=wx.BoxSizer(wx.HORIZONTAL)
                TextInserRow=wx.StaticText(PanelInsert,-1,label = "Number of Rows :")
                InsertSizer.Add(TextInserRow,0,wx.ALIGN_CENTRE)
                InsertSizer.AddSpacer(5)
                self.NbRow=self.Sheet.GetNumberRows()
                self.Row=wx.SpinCtrl(PanelInsert, 1, str(self.NbRow), min=1, max=1000,style=wx.SP_ARROW_KEYS)
                InsertSizer.Add(self.Row,0,wx.EXPAND)
                InsertSizer.AddSpacer(20)
                TextInserCol=wx.StaticText(PanelInsert,-1,label = "Number of Cols :")
                InsertSizer.Add(TextInserCol,0,wx.ALIGN_CENTRE)
                InsertSizer.AddSpacer(5)
                self.NbCol=self.Sheet.GetNumberCols()
                self.Col=wx.SpinCtrl(PanelInsert, 2, str(self.NbCol), min=1, max=100,style=wx.SP_ARROW_KEYS)
                InsertSizer.Add(self.Col,0,wx.EXPAND)
                InsertSizer.AddSpacer(5)
                PanelInsert.SetSizerAndFit(InsertSizer)
                ButtonSizer2.Add(PanelInsert,0,wx.EXPAND)
                ButtonSizer2.AddSpacer(10)
                
                #Panel clear + copy + paste + export
                PanelClear=wx.Panel(PanelButton2,-1)
                ClearSizer=wx.BoxSizer(wx.HORIZONTAL)
                ClearSizer.AddSpacer(5)
                ButtonPaste=wx.Button(PanelClear,8,label ="Paste Clipboard into selected Cell")
                ClearSizer.Add(ButtonPaste,0,wx.EXPAND)
                ClearSizer.AddSpacer(5)
                ButtonClear=wx.Button(PanelClear,6,label ="clear selceted cells")
                ClearSizer.Add(ButtonClear,0,wx.EXPAND)
                ClearSizer.AddSpacer(5)
                ButtonClearAll=wx.Button(PanelClear,7,label ="clear All")
                ClearSizer.Add(ButtonClearAll,0,wx.EXPAND)
                ButtonCopy=wx.Button(PanelClear,16,label ="Copy selceted cells to the Clipboard")
                ClearSizer.Add(ButtonCopy,0,wx.EXPAND)
                ClearSizer.AddSpacer(5)
                ButtonExport=wx.Button(PanelClear,17,label ="Export Table to CSV file")
                ClearSizer.Add(ButtonExport,0,wx.EXPAND)
                ClearSizer.AddSpacer(5)

                
                PanelClear.SetSizerAndFit(ClearSizer)
                ClearSizer.AddSpacer(5)


                
                ButtonSizer2.Add(PanelClear,0,wx.EXPAND)
                
                PanelButton.SetSizerAndFit(ButtonSizer)
                PanelButton2.SetSizerAndFit(ButtonSizer2)
                FrameSizer.Add(PanelButton,0,wx.EXPAND)
                FrameSizer.Add(PanelButton2,0,wx.EXPAND)
                # lié tout au sizer
                self.SetSizerAndFit(FrameSizer)
 

                
                
                # evemement
                wx.EVT_BUTTON(self, 1,self.DefFactor)
                wx.EVT_BUTTON(self, 4,self.SaveData)
                wx.EVT_BUTTON(self, 5,self.RenameCol)
                wx.EVT_BUTTON(self, 6,self.ClearSheet)
                wx.EVT_BUTTON(self, 7,self.ClearAllSheet)
                wx.EVT_BUTTON(self, 8,self.PasteClip)
                wx.EVT_BUTTON(self, 11,self.Drag)
                wx.EVT_BUTTON(self, 9,self.MoveUp)
                wx.EVT_BUTTON(self, 10,self.MoveDown)
                wx.EVT_BUTTON(self, 12,self.AddCol)
                wx.EVT_BUTTON(self, 13,self.RmCol)
                wx.EVT_BUTTON(self, 14,self.Sort)
                wx.EVT_BUTTON(self, 15,self.SelectEphFolder)
                wx.EVT_BUTTON(self,16,self.CopySelection)
                wx.EVT_BUTTON(self,17,self.ExportToXls)
                wx.EVT_TEXT_ENTER(self,3,self.Filter)
                ######################
                ################### SORT BUTTON !!!!!
                ######################
                ###self.ListCol.GetSelections()
                wx.EVT_LISTBOX(self,1,self.ColSelected)
                wx.EVT_LISTBOX(self,2,self.EphSelected)
                wx.EVT_SPINCTRL(self,1,self.ModifRow)
                wx.EVT_SPINCTRL(self,2,self.ModifCol)
                self.Bind(wx.EVT_CLOSE,self.OnClose)
                self.Bind(wx.grid.EVT_GRID_RANGE_SELECT,self.OnColSelected)
                self.Bind(wx.grid.EVT_GRID_SELECT_CELL,self.OnCellSelected)
                self.Sheet.Bind(wx.EVT_CHAR,self.OnKeyPress)

                if self.ExportData.H5==[]:
                        self.Buttonsave.Disable()
                        self.Show(True)
                        self.Sheet.SetNumberRows(30)
                else:
                        self.ReadH5()
        
        def Filter(self,txt):
                Filtre=self.TextFilter.GetValue()
                eph=self.DragEph.GetItems()
                os.chdir(self.info.PathEph)
                eph=ls.glob("".join(['*',Filtre,'*.eph']))
                eph.sort()
                self.DragEph.SetItems(eph)
                
        def ReadH5(self):
                self.Show(True)
                self.Buttonsave.Disable()
                file=tables.openFile(self.ExportData.H5,mode='r')
                FactorName=file.getNode('/Names/Within')
                self.FactorName=FactorName.read()
                Level=file.getNode('/Info/Level')
                self.Level=Level.read() 
                NoEpmtyCol=file.getNode('/Sheet/NoEmptyCol')
                NoEpmtyCol=NoEpmtyCol.read()
                SheetColName=file.getNode('/Sheet/ColName')
                SheetColName=SheetColName.read()
                SheetValue=file.getNode('/Sheet/Value')
                SheetValue=SheetValue.read()
                MaxColNumber=np.array(NoEpmtyCol).max()+1
                if MaxColNumber>9:
                        self.Sheet.SetNumberCols(MaxColNumber)
                        self.NbCol=MaxColNumber
                else:
                       self.NbCol=9 
                self.Col.SetValue(self.NbCol)
                self.text=['']
                for i,col in enumerate(NoEpmtyCol):
                        
                        ColName=SheetColName[i]
                        self.Sheet.SetColLabelValue(col,ColName)
                        self.text.append(ColName)
                        self.BoxFactor.SetItems(self.text)
                        ColValue=SheetValue[i]
                        if len(ColValue)>35:
                                self.Sheet.SetNumberRows(len(ColValue))
                                self.NbRow=len(ColValue)
                        else:
                                self.NbRow=30
                        self.Row.SetValue(self.NbRow)
                        for row,value in enumerate(ColValue):
                                self.Sheet.SetCellValue(row,col,value)
                        file.close()
        def OnKeyPress(self,event):
                if event.GetKeyCode()==3:
                        self.Sheet.Copy()
                elif event.GetKeyCode()==22:
                        self.Sheet.Paste()
                else:
                        
                        event.Skip()  
        def CopySelection(self,event):
               self.Sheet.Copy()
        def ExportToXls(self,event):
                wx.InitAllImageHandlers()
                dlg = wx.FileDialog(None, "Save Table to",wildcard = "*.csv",style = wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
                retour = dlg.ShowModal()
                chemin = dlg.GetPath()
                fichier = dlg.GetFilename()
                dlg.Destroy()
                dlg.Show(True)
                CsvFile = open(chemin, "w")
                Data=ReadSheet(self.Sheet,self.NbRow,self.NbCol)
                row=np.array(Data.NoEmptyRow).max()+1
                col=np.array(Data.NoEmptyCol).max()+1
                for r in range(row):
                        tmp=[]
                        for c in range(col):
                                cell=self.Sheet.GetCellValue(r,c)
                                tmp.append(';')
                                tmp.append(cell)
                        tmp.remove(';')
                        CsvFile.write("".join(tmp))
                        CsvFile.write('\n')
                        
                        
        def SelectEphFolder(self,event):
                self.TextFilter.Enable()
                wx.InitAllImageHandlers()
                dlg = wx.DirDialog(None, "select Folder",defaultPath=os.getcwd(),style = wx.DD_DEFAULT_STYLE|wx.DD_CHANGE_DIR)
                retour = dlg.ShowModal()
                self.info.PathEph = dlg.GetPath()
                dlg.Show(True)
                dlg.Destroy()
                os.chdir(self.info.PathEph)
                eph=ls.glob('*.eph')
                eph.sort()
                self.DragEph.SetItems(eph)
                if retour ==wx.ID_OK:
                        self.TextEph.SetLabel(self.info.PathEph)
                
        def OnCellSelected(self,event):
                row=event.GetRow()
                col=event.GetCol()
                CellValue=self.Sheet.GetCellValue(row,col)
                self.CellContentTxt.SetLabel(CellValue)
                self.Bind(wx.EVT_KEY_DOWN,self.OnKeyPress)
                event.Skip()
                
        def Sort(self,event):
                ColItems=self.ColData.GetItems()
                ColItems.sort()
                self.ColData.SetItems(ColItems)
        def Drag(self,event):
                #  dplacement des eph mis dans la list vers la colone selectinee. De plus le nombrre de ligne est teste et augmente si il le faut.
                ColItems=self.ColData.GetItems()
                Col=self.Sheet.GetSelectedCols()
                self.Sheet.Clear()
                ActualRow=self.Row.GetValue()
                # test du nombres de lignes
                if len(ColItems)>ActualRow:
                        NewRowNeeded=len(ColItems)-ActualRow
                        for i in range(NewRowNeeded):
                                self.Sheet.AppendRows()
                        self.Row.SetValue(len(ColItems))
                        self.NbRow=self.Row.GetValue()
                for row,it in enumerate(ColItems):
                        self.Sheet.SetCellValue(row,Col[0],it)
                # desactivation des boutons
                self.MoveUpButton.Disable()
                self.MoveDownButton.Disable()
                self.AddButton.Disable()
                self.RmButton.Disable()
                self.OKButton.Disable()
                self.Sheet.Enable()
                self.SortButton.Disable()
                self.Sheet.DeselectCol(Col[0])
                self.ColName.SetLabel('Select One Colon')
                self.ColData.SetItems('')
                
        def AddCol(self,event):
                ColItems=self.ColData.GetItems()
                EphItems=self.DragEph.GetItems()
                EphSelected=self.DragEph.GetSelections()
                for i in EphSelected:
                        EphFile=[self.info.PathEph]
                        EphFile.append('\\')
                        EphFile.append(EphItems[i])
                        ColItems.append("".join(EphFile))
                                        
                self.ColData.SetItems(ColItems)
                self.DragEph.SetItems(EphItems)
                self.TextFilter.SetValue('')
                os.chdir(self.info.PathEph)
                eph=ls.glob('*.eph')
                eph.sort()
                self.DragEph.SetItems(eph)
        def RmCol(self,event):
                ColItems=self.ColData.GetItems()
                EphItems=self.DragEph.GetItems()
                EphSelected=self.ColData.GetSelections()
                for i in EphSelected:
                        EphItems.append(ColItems[i])
                        ColItems[i]='rm'
                mark=1
                while mark==1:
                        try:
                                ColItems.remove('rm')
                        except:
                                mark=2
                EphItems.sort()
                self.ColData.SetItems(ColItems)
                #self.DragEph.SetItems(EphItems)
        def MoveUp(self,event):
                Items=self.ColData.GetItems()
                ItemsSelected=self.ColData.GetSelections()
                if ItemsSelected[0]!=0:
                        for i in ItemsSelected:
                                Tmp=Items[i]
                                TmpPrev=Items[i-1]
                                Items[i]=TmpPrev
                                Items[i-1]=Tmp
                else:
                        dlg = wx.MessageDialog(None,'You cannot move Up with the first line', style = wx.OK)
                        retour = dlg.ShowModal()
                        dlg.Destroy()
                self.ColData.SetItems(Items)
        def MoveDown(self,event):
                Items=self.ColData.GetItems()
                ItemsSelected=self.ColData.GetSelections()
                if ItemsSelected[0]!=len(Items)-1:
                        for i in ItemsSelected:
                                Tmp=Items[i]
                                TmpPrev=Items[i+1]
                                Items[i]=TmpPrev
                                Items[i+1]=Tmp
                else:
                        dlg = wx.MessageDialog(None,'You cannot move Down with the last line', style = wx.OK)
                        retour = dlg.ShowModal()
                        dlg.Destroy()
                self.ColData.SetItems(Items)
        def EphSelected(self,event):
                self.MoveUpButton.Disable()
                self.MoveDownButton.Disable()
                self.AddButton.Enable()
                self.RmButton.Disable()
                Col=self.Sheet.GetSelectedCols()
                if Col ==[]:
                        self.OKButton.Disable()
                        self.AddButton.Disable()
                else:
                        self.AddButton.Enable()
                        self.OKButton.Enable()
                        self.Sheet.Disable()
        def ColSelected(self,event):
                self.MoveUpButton.Enable()
                self.MoveDownButton.Enable()
                self.AddButton.Disable()
                self.RmButton.Enable()
                self.OKButton.Enable()
                self.Sheet.Disable()
                self.SortButton.Enable()
        
        def OnColSelected(self,event): 
                Col=self.Sheet.GetSelectedCols()
                name=['Colon Name : ']
                if Col !=[]:
                        if len(Col)==1:
                                name.append(self.Sheet.GetColLabelValue(Col[0]))
                                self.ColName.SetLabel("".join(name))
                                self.ColName.SetExtraStyle(wx.ALIGN_CENTRE)
                                rows=self.Sheet.GetNumberRows()
                                CellValue=[]
                                for r in range(rows):
                                        value=self.Sheet.GetCellValue(r,Col[0])
                                        if value!='':
                                                CellValue.append(value)
                                self.ColData.SetItems(CellValue)
                                if self.DragEph.GetSelections()!=[]:
                                        self.AddButton.Enable()
                                        self.OKButton.Enable()
                                else:
                                        self.AddButton.Disable()
                                self.Sheet.Disable()
                        else:
                                self.ColName.SetLabel('SELECT ONE COLON !!!')
                                
        def OnClose(self,event):
                if self.save:
                        self.Destroy()
                        self.ExportData.Show(True)
                else:
                        dlg = wx.MessageDialog(self,"Do you really want to close this application?","Confirm Exit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
                        result = dlg.ShowModal()
                        dlg.Destroy()
                        if result == wx.ID_OK:
                                self.Destroy()
                                self.ExportData.Show(True)
                                
        def PasteClip(self,event):
                self.Sheet.Paste()
        def DefFactor(self,event):
                self.Data=ReadSheet(self.Sheet,self.NbRow,self.NbCol)
                self.ModelDef=FactorWithin(self.Data.NoEmptyCol,self.Sheet,self,Level=[],Factor=[])
                self.ModelDef.Show(True)
        def SaveData(self,event):
                self.Show(False)
                wx.InitAllImageHandlers()
                dlg = wx.FileDialog(None, "Save Model to",wildcard = "*.h5",style = wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
                retour = dlg.ShowModal()
                chemin = dlg.GetPath()
                fichier = dlg.GetFilename()
                dlg.Destroy()
                dlg.Show(True)
                
                try:
                        self.ModelDef.Close()
                        self.ModelDef.ModelFull.Close()
                except:
                        pass
                self.info.DataFile.SetLabel(chemin)
                # création du fichier H5 pour les donée importante
                self.file=tables.openFile(chemin,mode='w')
                self.DataGroup=self.file.createGroup('/','Data')
                self.DataGFPGroup=self.file.createGroup('/','DataGFP')
                self.ModelGroup=self.file.createGroup('/','Model')
                self.InfoGroup=self.file.createGroup('/','Info')
                self.SheetGroup=self.file.createGroup('/','Sheet')
                self.NamesGroup=self.file.createGroup('/','Names')
                self.ErrorGroup=self.file.createGroup('/','Error')
                ResultGroup=self.file.createGroup('/','Result')
                IntermediateResults=self.file.createGroup(ResultGroup,'IntermediateResult')
                Aov=self.file.createGroup(ResultGroup,'Anova')
                PH=self.file.createGroup(ResultGroup,'PostHoc')
                self.file.createGroup(Aov,'All')
                self.file.createGroup(Aov,'GFP')
                self.file.createGroup(PH,'All')
                self.file.createGroup(PH,'GFP')
                SavingObj=DataProcessing(self)
                self.file.close()
                
                # export fichier H5
                self.ExportData.H5=chemin
                info=ReturnInfomation(chemin)
                self.info.TxtInfo.SetLabel("".join(info.text))
                if info.CovariatePresent:
                        self.info.ExportData.AnovaWave.PostHocCheckBox.Disable()
                        self.info.ExportData.AnovaIS.PostHocCheckBox.Disable()
                        self.info.ExportData.AnovaWave.PostHocCheckBox.SetValue(False)
                        self.info.ExportData.AnovaIS.PostHocCheckBox.SetValue(False)
                else:
                        self.info.ExportData.AnovaWave.PostHocCheckBox.Enable()
                        self.info.ExportData.AnovaIS.PostHocCheckBox.Enable()
                self.save=True
                self.Close()

        def RenameCol(self,event):
                NewName=self.NewName.GetLabel()
                # -1 car il y a un espace vide au début
                col=self.BoxFactor.GetCurrentSelection()-1
                self.Sheet.SetColLabelValue(col,NewName)
                self.text[col+1]=NewName
                self.BoxFactor.SetItems(self.text)
                self.NewName.SetLabel("")
                
        def ClearSheet(self,event):
                self.Sheet.Clear()
        def ClearAllSheet(self,event):
                self.Sheet.SelectAll()
                self.Sheet.Clear()
        def ModifRow(self,event):
                ActualRow=self.Row.GetValue()
                SheetRow=self.Sheet.GetNumberRows()
                while SheetRow!=ActualRow:
                        if SheetRow<ActualRow:
                                self.Sheet.AppendRows()
                                # Add Row
                        elif SheetRow>ActualRow:
                                self.Sheet.DeleteRows(ActualRow)
                        SheetRow=self.Sheet.GetNumberRows()
                self.NbRow=self.Row.GetValue()
        def ModifCol(self,event):
                ActualCol=self.Col.GetValue()
                SheetCol=self.Sheet.GetNumberCols()
                while SheetCol!=ActualCol:
                        # Add Row
                        if SheetCol<ActualCol:
                                self.Sheet.AppendCols()
                                txt=[]
                                for c in range(ActualCol):
                                        txt.append(self.Sheet.GetColLabelValue(c))
                                self.text=txt
                                
                        elif SheetCol>ActualCol:
                                self.Sheet.DeleteCols(ActualCol)
                                txt=[]
                                for c in range(ActualCol):
                                        txt.append(self.Sheet.GetColLabelValue(c))
                                self.text=txt
                        SheetCol=self.Sheet.GetNumberCols()
                self.text.insert(0,'')
                self.BoxFactor.SetItems(self.text)
                self.NbCol=self.Col.GetValue()
class DataProcessing:
        def __init__(self,info):
                ColName=[]
                for i in info.Data.NoEmptyCol:
                        ColName.append(str(info.Sheet.GetColLabelValue(i)))
                Level=info.Level
                Within=info.Within
                Between=info.Between
                Subject=info.Subject
                Covariate=info.Covariate
                FactorName=info.FactorName
                
                Nbsujet=len(Subject)
                NbCombi=Level.prod()
                if  Between.any():
                        NameBetween=[]
                        for i in info.BetweenIndex:
                                NameBetween.append(ColName[i])
                else:
                        NameBetween=False
                                
                if Covariate.any():
                        NameCovariate=[]    
                        for i in info.CovariateIndex:
                                NameCovariate.append(ColName[i])
                        
                else:
                        NameCovariate=False

                # demande si le Covariate est différentes pour les facteur within
                Model=DefineModel(Level.tolist(),Subject.tolist(),Between.tolist(),Covariate.tolist())

                # ecriture dans la table des donnée lié aux stat et autres info utilse nom, ...
                info.FactorName=[str(f) for f in info.FactorName]
               
                for i,col in enumerate(info.Data.Value):
                        if type(col)==list:
                                col=[str(n) for n in col]
                                info.Data.Value[i]=col
                        else:
                                info.Data.Value[i]=str(col)
                info.ColFactor=[str(n) for n in info.ColFactor]
                Dim=[]            
                Dim.append(info.Sheet.GetNumberRows())
                Dim.append(info.Sheet.GetNumberCols())
                
                # les vecteur/array des model pWithin, between, covariate et sujet
                WithinH5=info.file.createArray(info.ModelGroup,'Within',Model.Within)
                BetweenH5=info.file.createArray(info.ModelGroup,'Between',Model.Groupe)
                SubjectH5=info.file.createArray(info.ModelGroup,'Subject',Model.Subject)

                # info sur les colone Within
                ColFactor=info.file.createArray(info.InfoGroup,'ColFactor',info.ColFactor)
                ColWithin=info.file.createArray(info.InfoGroup,'ColWithin',info.ModelDef.ModelFull.WithinIndex)
                if info.ModelDef.ModelFull.BetweenIndex==[]:
                        info.ModelDef.ModelFull.BetweenIndex=-1
                ColBetween=info.file.createArray(info.InfoGroup,'ColBetween',info.ModelDef.ModelFull.BetweenIndex)
                if info.ModelDef.ModelFull.CovariateIndex==[]:
                        info.ModelDef.ModelFull.CovariateIndex=-1
                ColCovariate=info.file.createArray(info.InfoGroup,'ColCovariate',info.ModelDef.ModelFull.CovariateIndex)
                # info général, les niveau des facteur Within (pour modification des entrées)
                if Level.any()==False:
                        Level=False
                Level=info.file.createArray(info.InfoGroup,'Level',Level)
                # info les valeur des cellule
                SheetValue=info.file.createArray(info.SheetGroup,'Value',info.Data.Value)
                # les colone non vide
                SheetNoEmptyCol=info.file.createArray(info.SheetGroup,'NoEmptyCol',info.Data.NoEmptyCol)
                # le nom des colone
                ColName=info.file.createArray(info.SheetGroup,'ColName',ColName)
                # dimenssion du tableur 
                Dim=info.file.createArray(info.SheetGroup,'Dim',Dim)
                # nom des fateur Within
                if info.FactorName==[]:
                        info.FactorName=False
                FactorName=info.file.createArray(info.NamesGroup,'Within',info.FactorName)
                # nom de between
                BetweenName=info.file.createArray(info.NamesGroup,'Between',NameBetween)
                # nom des covariate
                CovName=info.file.createArray(info.NamesGroup,'Covariate',NameCovariate)

                if Covariate.any():
                        # demander si il y a des valeurs différentes de covariate pour les différents niveau des facteurs within
                        dlg = wx.MessageDialog(None,'Do you have different Covariate Value for each Within Subject Factor?',"Covariate Data", wx.YES_NO|wx.YES_DEFAULT|wx.ICON_QUESTION)
                        dlg.SetSize((800,800))
                        response = dlg.ShowModal()
                        if response==wx.ID_YES:
                                ModelModif=CovariateDefinition(Model.Within,Model.Groupe,Model.Subject,Model.Covariate,FactorName,NameBetween,NameCovariate)
                                if ModelModif.Correction:
                                        Covariate=info.file.createArray(info.ModelGroup,'Covariate',ModelModif.Covariate)
                                elif ModelModif.Correction == False:
                                        Covariate=info.file.createArray(info.ModelGroup,'Covariate',Model.Covariate)
                        else:
                                Covariate=info.file.createArray(info.ModelGroup,'Covariate',Model.Covariate)
                                dlg.Destroy()
                        dlg.Destroy()
                else:
                        Covariate=info.file.createArray(info.ModelGroup,'Covariate',Model.Covariate)
                
                #Lecture de Eph  et mise dans la table  puis faire les claluls dessus (GFP, ST, ..:)
                SubjectGroup=[]
                SubjectGroupGFP=[]
                dlg=wx.ProgressDialog('File extraction','Files extraction : 0 %',(Nbsujet*NbCombi+1),None,wx.PD_REMAINING_TIME)
                dlg.SetSize((200,130))
                n=0
                ErrorEph=[]
                for cond,i in enumerate(Within):
                        if type(i)==list:
                                for sujet,e in enumerate(i):
                                        try:
                                                Name=['Subject',str(sujet)]
                                                SubjectGroup.append(info.file.createGroup(info.DataGroup,"".join(Name)))
                                                SubjectGroupGFP.append(info.file.createGroup(info.DataGFPGroup,"".join(Name)))
                                        except:
                                                pass
                                        NameEph=e
                                        try:
                                                EphData=Eph(NameEph)
                                                CondName=['Condition',str(cond)]
                                                if EphData.tf==1:
                                                        Data=info.file.createArray(SubjectGroup[sujet],"".join(CondName),EphData.data.reshape((1,EphData.data.shape[0])))
                                                        Data=info.file.createArray(SubjectGroupGFP[sujet],"".join(CondName),EphData.data.std(0))
                                                elif EphData.electrodes==1:
                                                        Data=info.file.createArray(SubjectGroupGFP[sujet],"".join(CondName),EphData.data)
                                                        Data=info.file.createArray(SubjectGroup[sujet],"".join(CondName),EphData.data.reshape((EphData.data.shape[0],1)))
                                                else:
                                                        Data=info.file.createArray(SubjectGroupGFP[sujet],"".join(CondName),EphData.data.std(1))
                                                        Data=info.file.createArray(SubjectGroup[sujet],"".join(CondName),EphData.data)
                                        except:
                                                ErrorEph.append(NameEph)



                                        n+=1
                                        pourcent=str(100.0*n/(Nbsujet*NbCombi))
                                        pourcent=pourcent[0:pourcent.find('.')+3]
                                        dlg.Update(n," ".join(['Files extraction  :',pourcent,'%']))
                                        
                        else:
                                Name=['Subject',str(cond)]
                                SubjectGroup.append(info.file.createGroup(info.DataGroup,"".join(Name)))
                                NameEph=i
                                try:
                                        EphData=Eph(NameEph)
                                        Data=info.file.createArray(SubjectGroup[cond],'Condition',EphData.data)
                                        if EphData.tf==1:
                                                Data=info.file.createArray(SubjectGroupGFP[sujet],"".join(CondName),EphData.data.std(0))
                                        elif EphData.electrodes==1:
                                                Data=info.file.createArray(SubjectGroupGFP[sujet],"".join(CondName),EphData.data)
                                        else:
                                                Data=info.file.createArray(SubjectGroupGFP[sujet],"".join(CondName),EphData.data.std(1))
                                except:
                                        ErrorEph.append(NameEph)

                                n+=1
                                pourcent=str(100.0*n/(Nbsujet*NbCombi))
                                pourcent=pourcent[0:pourcent.find('.')+3]
                                dlg.Update(n," ".join(['Files extraction  :',pourcent,'%']))
                
                dlg.Destroy()
                # Erreur dans la lecture des EPHs
                if ErrorEph==[]:
                        ErrorEph=False
                        ErrorEph=info.file.createArray(info.ErrorGroup,'Eph',ErrorEph)
                        Shape=info.file.createArray(info.InfoGroup,'ShapeGFP',np.array([int(EphData.tf),1,int(NbCombi),int(Nbsujet)]))
                        Shape=info.file.createArray(info.InfoGroup,'Shape',np.array([int(EphData.tf),int(EphData.electrodes),int(NbCombi),int(Nbsujet)]))
                        Fs=info.file.createArray(info.InfoGroup,'FS',np.array(EphData.fs))
                else:
                        ErrorEph=info.file.createArray(info.ErrorGroup,'Eph',ErrorEph)

                try:
                        ModelModif.Destroy()
                except:
                        pass
                
"""lecture: path eph/eph name""" 
class Eph: #lire les Eph, puis faire les claluls dessus (GFP, ST, ..:)
	"""lecture: path eph/eph name""" 
	def __init__(self,PathEph):
		""" on initialise l'objet eph
		soit on lis des EPH 2 parametres 
		1) PathEph = lieu de l'eph
		2) NameEph = nom de l'eph
		"""
                header = open(PathEph).readline()
                header=header.split('\t')
                if len(header)==1:
                        header = open(PathEph).readline()
                        header=header.split(' ')
                self.electrodes =int(header[0])
                self.tf=int(header[1])
                try:
                        self.fs=int(header[2])
                except:
                        self.fs=float(header[2])
                self.data=np.loadtxt(PathEph,skiprows=1)
        
               
                
class CalculSheet(sheet.CSheet):
        def __init__(self, parent,size=(2,2)):
                sheet.CSheet.__init__(self, parent)
                self.SetNumberRows(30)
                self.SetNumberCols(9)
                self.SetColLabelValue(0,'subject')

                
class ReadSheet:
        def __init__(self,Sheet,NbRow,NbCol):
                self.Value=[]
                self.NoEmptyCol=[]
                self.NoEpmptyRow=[]
                NoEmptyRow=[]
                for c in range(NbCol):
                        Col=[]
                        for r in range(NbRow):
                                Col.append(Sheet.GetCellValue(r,c))
                        # Non empty Colon    
                        if Col.count('')!=len(Col):
                                self.NoEmptyCol.append(c)

                                
                for r in range(NbRow):
                        Row=[]
                        for c in range(NbCol):
                                Row.append(Sheet.GetCellValue(r,c))
                        
                         # Non empty Colon    
                        if Row.count('')!=len(Row):
                                NoEmptyRow.append(r)
                for c in self.NoEmptyCol:
                        Col=[]
                        for r in NoEmptyRow:
                                cell=Sheet.GetCellValue(r,c)     
                                Col.append(cell)
                        self.Value.append(Col)
                self.NoEmptyRow=NoEmptyRow
                

class FactorWithin(wx.Frame):
        """définition des facteur Within stype SPSS"""
        def __init__(self,NoEmptyCol,Sheet,Parent,Level,Factor):
                wx.Frame.__init__(self, None, -1, title = "Within subject definition", size = (200,250))
                FrameSizer=wx.BoxSizer(wx.VERTICAL)
                self.Level=Level
                self.Factor=Factor
                self.NoEmptyCol=NoEmptyCol
                self.Sheet=Sheet
                self.ColWithin=[]
                self.ColBetween=[]
                self.ColSubject=[]
                self.ColCovariate=[]
                self.TabValue=Parent.Data.Value
                self.DataEntry=Parent
                
                
                #panel Factor
                PanelFactor=wx.Panel(self,-1)
                FactorSizer=wx.BoxSizer(wx.VERTICAL)
                TextNameFactor=wx.StaticText(PanelFactor,-1,label = "   Within Subject Factor Name : ")
                FactorSizer.Add(TextNameFactor,0,wx.ALIGN_LEFT)
                self.FactorName=wx.TextCtrl(PanelFactor,1,value="")
                FactorSizer.Add(self.FactorName,0,wx.ALIGN_RIGHT)
                
                TextNbLevel=wx.StaticText(PanelFactor,-1,label = "   Number of Levels : ")
                FactorSizer.Add(TextNbLevel,0,wx.ALIGN_LEFT)
                self.LevelNb=wx.TextCtrl(PanelFactor,1,value="")
                FactorSizer.Add(self.LevelNb,0,wx.ALIGN_RIGHT)
                PanelFactor.SetSizerAndFit(FactorSizer)
                FrameSizer.Add(PanelFactor,0,wx.EXPAND)
                FrameSizer.AddStretchSpacer()

                #Panel button et def
                PanelDef=wx.Panel(self,-1)
                DefSizer=wx.BoxSizer(wx.HORIZONTAL)

                #Panel avec les button
                PanelButton=wx.Panel(PanelDef,-1)
                ButtonSizer=wx.BoxSizer(wx.VERTICAL)
                self.ButtonAdd=wx.Button(PanelButton,1,label ="Add")
                ButtonSizer.Add(self.ButtonAdd,0,wx.EXPAND)
                self.ButtonClear=wx.Button(PanelButton,2,label ="Clear")
                self.ButtonClear.Disable()
                ButtonSizer.Add(self.ButtonClear,0,wx.EXPAND)
                self.ButtonChange=wx.Button(PanelButton,3,label ="Change")
                self.ButtonChange.Disable()
                ButtonSizer.Add(self.ButtonChange,0,wx.EXPAND)
                PanelButton.SetSizerAndFit(ButtonSizer)
                DefSizer.Add(PanelButton,0,wx.EXPAND)
                #panel avec la liste non modifiable
                PanelList=wx.Panel(PanelDef,-1)
                self.ListFactor=wx.ListBox(PanelList,1,size=(100,100),style=wx.LB_SINGLE)
                DefSizer.Add(PanelList,wx.EXPAND)
                PanelDef.SetSizerAndFit(DefSizer)
                FrameSizer.Add(PanelDef,0,wx.EXPAND)
                FrameSizer.AddStretchSpacer()

                # Panel Continue
                PanelContinue=wx.Panel(self,-1)
                ContinueSizer=wx.BoxSizer(wx.VERTICAL)
                ContinueButton=wx.Button(PanelContinue,4,label ="Continue")
                ContinueSizer.Add(ContinueButton,0,wx.ALIGN_RIGHT)
                PanelContinue.SetSizer(ContinueSizer)
                FrameSizer.Add(PanelContinue,0,wx.EXPAND)
                self.SetSizer(FrameSizer)
                Factor=[]
                for i in range(len(self.Factor)):
                        name=[]
                        name.append(self.Factor[i])
                        name.append('(')
                        name.append(str(self.Level[i]))
                        name.append(')')
                        Factor.append("".join(name))
                self.ListFactor.SetItems(Factor)
                        
                ###### les evenements !!!!
                wx.EVT_BUTTON(self, 1,self.Add)
                wx.EVT_BUTTON(self, 2,self.Clear)
                wx.EVT_BUTTON(self, 3,self.Change)
                wx.EVT_BUTTON(self, 4,self.Continue)
                wx.EVT_LISTBOX(self,1,self.ItemSelected)
                
        def ItemSelected(self,event):
                self.ButtonChange.Enable()
                self.ButtonClear.Enable()
                self.ButtonAdd.Disable()
                idx=self.ListFactor.GetSelections()
                self.FactorName.SetValue(self.Factor[idx[0]])
                self.LevelNb.SetValue(str(self.Level[idx[0]]))
        def Add(self,event):
                
                name=[]
                name.append(self.FactorName.GetValue())
                name.append('(')
                name.append(self.LevelNb.GetValue())
                name.append(')')
                Factor=self.ListFactor.GetItems()
                try:
                        level=int(self.LevelNb.GetValue())
                        if level ==1:
                                dlg = wx.MessageDialog('Level must be bigger than 1', style = wx.OK)
                                retour = dlg.ShowModal()
                                dlg.Destroy()
                                self.FactorName.SetValue('')
                                self.LevelNb.SetValue('')
                        else:
                                self.Level.append(level)
                                self.Factor.append(self.FactorName.GetValue())
                                Factor.append("".join(name))
                                self.ListFactor.DeselectAll()
                                self.ListFactor.SetItems(Factor)
                                self.FactorName.SetValue('')
                                self.LevelNb.SetValue('')
                                

                except:
                        dlg = wx.MessageDialog(self,'Numbers of level must be integer', style = wx.OK)
                        retour = dlg.ShowModal()
                        dlg.Destroy()
                        self.FactorName.SetValue('')
                        self.LevelNb.SetValue('')
                
        def  Clear(self,event):
                idx=self.ListFactor.GetSelections()
                idx=idx[0]
                self.ListFactor.Delete(idx)
                self.ButtonChange.Disable()
                self.ButtonAdd.Enable()
                self.ButtonClear.Disable()
                self.FactorName.SetValue('')
                self.LevelNb.SetValue('')
        def Change(self,event):
                self.ButtonChange.Disable()
                self.ButtonAdd.Enable()
                self.ButtonClear.Disable()
                idx=self.ListFactor.GetSelections()
                idx=idx[0]
                Factor=self.ListFactor.GetItems()
                name=[]
                name.append(self.FactorName.GetValue())
                name.append('(')
                name.append(self.LevelNb.GetValue())
                name.append(')')
                try:
                        level=int(self.LevelNb.GetValue())
                        if level ==1:
                                dlg = wx.MessageDialog('Level must be bigger than 1', style = wx.OK)
                                retour = dlg.ShowModal()
                                dlg.Destroy()
                                self.FactorName.SetValue(self.Factor[idx])
                                self.LevelNb.SetValue(str(self.Level[idx]))
                        else:
                                self.Level[idx]=level
                                self.Factor[idx]=self.FactorName.GetValue()
                                Factor[idx]="".join(name)
                                self.ListFactor.SetItems(Factor)
                                self.ListFactor.DeselectAll()
                                self.FactorName.SetValue('')
                                self.LevelNb.SetValue('')
                except:
                        dlg = wx.MessageDialog(self,'Numbers of level must be integer', style = wx.OK)
                        retour = dlg.ShowModal()
                        dlg.Destroy()
                        self.FactorName.SetValue(self.Factor[idx])
                        self.LevelNb.SetValue(str(self.Level[idx]))

                
                
        def Continue(self,event):
                self.ModelFull=FactorDef(self.NoEmptyCol,self.Sheet,self)
                self.ModelFull.Show(True)
                self.Show(False)
                self.DataEntry.FactorName=self.Factor
                

                
class FactorDef(wx.Frame):
        """attribution des facteurs style SPSS"""
        def __init__(self,NoEmptyCol,Sheet,Parent):
                wx.Frame.__init__(self, None, -1, title = "Factor deficnition", size = (200,250))
                FrameSizer=wx.BoxSizer(wx.VERTICAL)
                # Panel des definition
                PanelInit=wx.Panel(self,-1)
                SizerInit=wx.BoxSizer(wx.HORIZONTAL)
                self.Subject= []
                self.Within=[]
                self.WithinIndex=[]
                self.Between=[]
                self.BetweenIndex=[]
                self.Covariate=[]
                self.CovariateIndex=[]
                self.Level=Parent.Level
                self.Sheet=Sheet
                self.TabValue=Parent.TabValue
                self.DataEntry=Parent.DataEntry
                self.DataEntry.ColFactor=[]
                self.FactorWithin=Parent
                #List des colones
                self.ColName=[]
                for i in NoEmptyCol:
                        self.ColName.append(Sheet.GetColLabelValue(i))
                self.ListCol=wx.ListBox(PanelInit,1,choices=self.ColName,style=wx.LB_EXTENDED)
                SizerInit.Add(self.ListCol,0,wx.EXPAND)

                #panels des case pour la définition
                PanelDef=wx.Panel(PanelInit,-1)
                SizerDef=wx.BoxSizer(wx.VERTICAL)

                #Panel Subject
                PanelSubject=wx.Panel(PanelDef,-1,size=(200,200))
                SizerSubject=wx.BoxSizer(wx.HORIZONTAL)
                
                PanelSubjectButton=wx.Panel(PanelSubject,-1)
                SizerSubjectButton=wx.BoxSizer(wx.VERTICAL)
                self.SubjectAdd=wx.Button(PanelSubjectButton,1,label='>')
                SizerSubjectButton.Add(self.SubjectAdd,0,wx.EXPAND)
                self.SubjectAdd.Disable()
                self.SubjectRm=wx.Button(PanelSubjectButton,2,label='<')
                SizerSubjectButton.Add(self.SubjectRm,0,wx.EXPAND)
                self.SubjectRm.Disable()
                PanelSubjectButton.SetSizer(SizerSubjectButton)
                
                PanelSubjectVariable=wx.Panel(PanelSubject,-1)
                SizerSubjectVariable=wx.BoxSizer(wx.VERTICAL)
                SubjectText=wx.StaticText(PanelSubjectVariable,-1,label ="Subject Variable",style=wx.ALIGN_CENTER)
                SizerSubjectVariable.Add(SubjectText,0,wx.EXPAND)
                self.SubjectVariable=wx.TextCtrl(PanelSubjectVariable,1,value="",style =wx.TE_READONLY)
                SizerSubjectVariable.Add(self.SubjectVariable,0,wx.EXPAND)
                PanelSubjectVariable.SetSizer(SizerSubjectVariable)

                SizerSubject.Add(PanelSubjectButton,0,wx.ALIGN_CENTRE)
                SizerSubject.Add(PanelSubjectVariable,0,wx.ALIGN_RIGHT)
                PanelSubject.SetSizer(SizerSubject)

                SizerDef.Add(PanelSubject,0,wx.EXPAND)

                #Panel Within
                PanelWithin=wx.Panel(PanelDef,-1)
                SizerWithin=wx.BoxSizer(wx.HORIZONTAL)
                
                PanelWithinButton=wx.Panel(PanelWithin,-1)
                SizerWithinButton=wx.BoxSizer(wx.VERTICAL)
                self.WithinAdd=wx.Button(PanelWithinButton,3,label='>')
                SizerWithinButton.Add(self.WithinAdd,0,wx.EXPAND)
                self.WithinAdd.Disable()
                self.WithinRm=wx.Button(PanelWithinButton,4,label='<')
                SizerWithinButton.Add(self.WithinRm,0,wx.EXPAND)
                self.WithinRm.Disable()
                PanelWithinButton.SetSizer(SizerWithinButton)
                
                PanelWithinVariable=wx.Panel(PanelWithin,-1)
                SizerWithinVariable=wx.BoxSizer(wx.VERTICAL)
                WithinText=wx.StaticText(PanelWithinVariable,-1,label ="Within Subject Variable(s)",style=wx.ALIGN_CENTER)
                SizerWithinVariable.Add(WithinText,0,wx.EXPAND)
                Model=DefineModel(Parent.Level,[1],[1],[1])
                if Model.Within.any():
                        ListFactorWithin=Model.Within.tolist()
                else:
                        ListFactorWithin=[[]]
                        
                        
                
##                ListFactorWithin=Model.Within.tolist()
                Fact=[]
               
                if ListFactorWithin ==[[]]:
                        WithinText.SetLabel('Data')
                        Fact=['_?_']
                else:
                        for i in ListFactorWithin:
                                tmp=[]
                                for j in i:
                                        number=int(j)
                                        tmp.append(str(number))
                                FactNumber=",".join(tmp)
                                tmp=['_?_(']
                                tmp.append(FactNumber)
                                tmp.append(')')
                                Fact.append("".join(tmp)) 
                self.WithinVariable=wx.ListBox(PanelWithinVariable,2,choices=Fact,size=(100,100),style=wx.LB_EXTENDED)
                SizerWithinVariable.Add(self.WithinVariable,0,wx.EXPAND)
                PanelWithinVariable.SetSizer(SizerWithinVariable)

                SizerWithin.Add(PanelWithinButton,0,wx.wx.ALIGN_CENTRE)
                SizerWithin.Add(PanelWithinVariable,0,wx.wx.ALIGN_RIGHT)
                PanelWithin.SetSizer(SizerWithin)

                SizerDef.Add(PanelWithin,0,wx.EXPAND)

                #Panel Between
                PanelBetween=wx.Panel(PanelDef,-1)
                SizerBetween=wx.BoxSizer(wx.HORIZONTAL)
                
                PanelBetweenButton=wx.Panel(PanelBetween,-1)
                SizerBetweenButton=wx.BoxSizer(wx.VERTICAL)
                self.BetweenAdd=wx.Button(PanelBetweenButton,5,label='>')
                SizerBetweenButton.Add(self.BetweenAdd,0,wx.EXPAND)
                self.BetweenAdd.Disable()
                self.BetweenRm=wx.Button(PanelBetweenButton,6,label='<')
                SizerBetweenButton.Add(self.BetweenRm,0,wx.EXPAND)
                self.BetweenRm.Disable()
                PanelBetweenButton.SetSizer(SizerBetweenButton)
                
                PanelBetweenVariable=wx.Panel(PanelBetween,-1)
                SizerBetweenVariable=wx.BoxSizer(wx.VERTICAL)
                BetweenText=wx.StaticText(PanelBetweenVariable,-1,label ="Between Subject Variable(s)",style=wx.ALIGN_CENTER)
                SizerBetweenVariable.Add(BetweenText,0,wx.EXPAND)
                self.BetweenVariable=wx.ListBox(PanelBetweenVariable,3,size=(100,100),style=wx.LB_EXTENDED)
                SizerBetweenVariable.Add(self.BetweenVariable,0,wx.EXPAND)
                PanelBetweenVariable.SetSizer(SizerBetweenVariable)

                SizerBetween.Add(PanelBetweenButton,0,wx.ALIGN_CENTRE)
                SizerBetween.Add(PanelBetweenVariable,0,wx.ALIGN_RIGHT)
                PanelBetween.SetSizer(SizerBetween)

                SizerDef.Add(PanelBetween,0,wx.EXPAND)

                #Panel Covariate
                PanelCovariate=wx.Panel(PanelDef,-1)
                SizerCovariate=wx.BoxSizer(wx.HORIZONTAL)
                
                PanelCovariateButton=wx.Panel(PanelCovariate,-1)
                SizerCovariateButton=wx.BoxSizer(wx.VERTICAL)
                self.CovariateAdd=wx.Button(PanelCovariateButton,7,label='>')
                SizerCovariateButton.Add(self.CovariateAdd,0,wx.EXPAND)
                self.CovariateAdd.Disable()
                self.CovariateRm=wx.Button(PanelCovariateButton,8,label='<')
                SizerCovariateButton.Add(self.CovariateRm,0,wx.EXPAND)
                self.CovariateRm.Disable()
                PanelCovariateButton.SetSizer(SizerCovariateButton)
                
                PanelCovariateVariable=wx.Panel(PanelCovariate,-1)
                SizerCovariateVariable=wx.BoxSizer(wx.VERTICAL)
                CovariateText=wx.StaticText(PanelCovariateVariable,-1,label ="Covariate(s)",style=wx.ALIGN_CENTER)
                SizerCovariateVariable.Add(CovariateText,0,wx.EXPAND)
                self.CovariateVariable=wx.ListBox(PanelCovariateVariable,4,size=(100,100),style=wx.LB_EXTENDED)
                SizerCovariateVariable.Add(self.CovariateVariable,0,wx.EXPAND)
                PanelCovariateVariable.SetSizer(SizerCovariateVariable)

                SizerCovariate.Add(PanelCovariateButton,0,wx.ALIGN_CENTRE)
                SizerCovariate.Add(PanelCovariateVariable,0,wx.ALIGN_RIGHT)
                PanelCovariate.SetSizer(SizerCovariate)

                SizerDef.Add(PanelCovariate,0,wx.EXPAND)
                
                PanelDef.SetSizer(SizerDef)
                SizerInit.Add(PanelDef,0,wx.EXPAND)
                PanelInit.SetSizer(SizerInit)
                FrameSizer.Add(PanelInit,0,wx.EXPAND)                                
                # Panel Button OK
                PanelOK=wx.Panel(self,-1)
                SizerOK=wx.BoxSizer(wx.HORIZONTAL)
                ButtonPrevious=wx.Button(PanelOK,9,label='return to Within Subject factor definition')
                SizerOK.Add(ButtonPrevious,0,wx.ALIGN_LEFT)
                ButtonOK=wx.Button(PanelOK,10,label='OK')
                SizerOK.Add(ButtonOK,0,wx.ALIGN_RIGHT)
                PanelOK.SetSizer(SizerOK)
                FrameSizer.Add(PanelOK,0,wx.ALIGN_RIGHT)
                self.SetSizerAndFit(FrameSizer)

                # evenement 
                 ###### les evenements !!!!
                wx.EVT_BUTTON(self, 1,self.AddSubject)
                wx.EVT_BUTTON(self, 2,self.RmSubject)
                wx.EVT_BUTTON(self, 3,self.AddWithin)
                wx.EVT_BUTTON(self, 4,self.RmWithin)
                wx.EVT_BUTTON(self, 5,self.AddBetween)
                wx.EVT_BUTTON(self, 6,self.RmBetween)
                wx.EVT_BUTTON(self, 7,self.AddCovariate)
                wx.EVT_BUTTON(self, 8,self.RmCovariate)
                # 1: colone 2: facteur 3: between 4: covariate
                wx.EVT_LISTBOX(self,1,self.ColSelected)
                wx.EVT_LISTBOX(self,2,self.WithinSelected)
                wx.EVT_LISTBOX(self,3,self.BetweenSelected)
                wx.EVT_LISTBOX(self,4,self.CovariateSelected)
                wx.EVT_BUTTON(self,10,self.Ok)
                wx.EVT_BUTTON(self,9,self.Previous)

                ### bouton OK avec les facteur sous forme de vecteur
        def Previous(self,event):
                self.FactorWithin.Show(True)
                self.Close()
        def Ok(self,event):
                self.DataEntry.ColFactor=self.WithinVariable.GetItems()
                level=np.array(self.Level)
                self.DataEntry.Level=level
                NbLevel=level.prod()
                error=[]
                subject=[]
                errortmp=[]
                if self.Subject==[]:
                        error.append('Subject colone not define')
                for i in self.Subject:
                        if type(i)==list:
                                for s in i:
                                        try:
                                                subject.append(int(s))
                                        except:
                                                errortmp=1
                        else:
                                try:
                                        subject.append(int(s))
                                except:
                                        errortmp=1
                                
                                                
                

                if errortmp==1:
                        error.append('Subject colone must be an integer')
                else:
                        subject=np.array(subject)
                        if subject.max()>len(subject):
                                error.append('Subject number bigger than length')
                        else:
                                self.Subject=subject.squeeze()
                                self.DataEntry.Subject=subject.squeeze()
                        

                Within=[]
                errortmp=[]
                for f in self.Within:
                        if type(f)==list:
                                tmp=[]
                                for e in f:
                                        if e[len(e)-4:len(e)]=='.eph':
                                                
                                                tmp.append(os.path.abspath(str(e)))
                                        else:
                                                errortmp=1
                                Within.append(tmp)
                        else:
                                if f[len(f)-4:len(f)]=='.eph':
                                        Within.append(str(f))
                                else:
                                        errortmp=2
                                        
                
                if errortmp==1:
                        error.append('Within colones must contain *.eph file')
                elif errortmp==2:
                        error.append('Within colone must contain *.eph file')
                else:
                        self.DataEntry.Within=Within
                if NbLevel !=len(self.Within):
                        error.append('Fill all Within subject factor')
                        
                errortmp=[]
                between=[]
                for f in self.Between:
                        if type(f)==list:
                                tmp=[]
                                for e in f:
                                        try:
                                                tmp.append(int(e))
                                        except:
                                                errortmp=1
                                between.append(tmp)
                        else:
                                try:
                                        between.append(int(e))
                                except:
                                       errortmp=2
                if errortmp==1:
                        error.append('Between colones must be an integer')
                elif errortmp==2:
                         error.append('Between colone must be an integer')
                else:
                        between=np.array(between)
                        self.DataEntry.Between=between.squeeze()
                        self.DataEntry.BetweenIndex=self.BetweenIndex
                        

                covariate=[]
                errortmp=[]
                for f in self.Covariate:
                        if type(f)==list:
                                tmp=[]
                                for e in f:
                                        try:
                                                tmp.append(float(e))
                                        except:
                                                errortmp=1
                                covariate.append(tmp)
                        else:
                                try:
                                        covariate.append(float(e))
                                except:
                                        errortmp=2
                if errortmp==1:
                        error.append('Covariate colones must be a float')
                elif errortmp==2:
                        error.append('Covariate colone must be a float')
                else:
                        covariate=np.array(covariate)
                        self.DataEntry.Covariate=covariate.squeeze()
                        self.DataEntry.CovariateIndex=self.CovariateIndex


                
                

                if error!=[]:
                        self.Show(False)
                        self.DataEntry.Buttonsave.Disable()
##                        self.DataEntry.ButtonModify.Disable()
                        dlg = wx.MessageDialog(self," \n ".join(error), style = wx.OK)
                        retour = dlg.ShowModal()
                        dlg.Destroy()
                        
                else:
                        self.DataEntry.Buttonsave.Enable()
##                        self.DataEntry.ButtonModify.Enable()
                        self.Show(False)
              
                
                        
                        


                # Summary(self.WithinVariable.GetItems(),self.BetweenVariable.GetItems(),self.SubjectVariable.GetLabel(),self.CovariateVariable.GetItems(),self.DataEntry.SummaryTxT)       
        def AddSubject(self,event):
                self.SubjectAdd.Disable()
                self.SubjectRm.Enable()
                ColNumber=self.ListCol.GetSelections()
                ColName=self.ListCol.GetItems()
                if len(ColNumber)==1:
                        name=ColName[ColNumber[0]]
                        self.SubjectVariable.SetLabel(name)
                        ColName.pop(ColNumber[0])
                        #ColName.append('')
                        self.ListCol.SetItems(ColName)
                        ColNumber=self.ColName.index(name)
                        self.ColNumberSubject=ColNumber
                        self.Subject.append(self.TabValue[ColNumber])
                else:
                        dlg = wx.MessageDialog(self,'Select only one variables for Subject', style = wx.OK)
                        retour = dlg.ShowModal()
                        dlg.Destroy()
                
        def RmSubject(self,event):
                self.SubjectRm.Disable()
                self.SubjectAdd.Enable()
                ColName=self.ListCol.GetItems()
                VariableSubject=self.SubjectVariable.GetLabel()
                ColName.insert(self.ColNumberSubject,VariableSubject)
                self.Subject=[]
                self.SubjectVariable.SetLabel("")
                self.ListCol.SetItems(ColName)   
                  
        def AddWithin(self,event):
                ColNumber=self.ListCol.GetSelections()
                ColName=self.ListCol.GetItems()
                Factor=self.WithinVariable.GetItems()
                NbFactor=len(Factor)
                if len(self.Within)+len(ColNumber)>NbFactor:
                        dlg = wx.MessageDialog(self,'Within subject factor is full', style = wx.OK)
                        retour = dlg.ShowModal()
                        dlg.Destroy()
                else:            
                        if len(ColNumber)>NbFactor:
                                dlg = wx.MessageDialog(self,'Number of selected Variable exceed number of Factor', style = wx.OK)
                                retour = dlg.ShowModal()
                                dlg.Destroy()
                        else:
                                Selections=ColNumber[0:NbFactor]
                                for i in Selections:
                                        # i is a integer
                                        nametmp=[]
                                        nametmp.append(ColName[i])
                                        n=-1
                                        mark=-1
                                        while mark==-1:
                                                n+=1
                                                mark=Factor[n].find('?')
                                        tmpfact=Factor[n]
                                        debut=tmpfact.find('(')
                                        if debut!=-1:
                                                nametmp.append(tmpfact[debut:len(tmpfact)])
                                        Factor[n]="".join(nametmp)
                                        
                                        index=self.ColName.index(ColName[i])
                                        self.WithinIndex.append(index)
                                        self.Within.append(self.TabValue[index])
                                        ColName[i]=''
                                ColNameNew=[]
                                for i in ColName:
                                        if i !='':
                                                ColNameNew.append(i)

                                self.ListCol.SetItems(ColNameNew)
                                self.WithinVariable.SetItems(Factor)
  
        def RmWithin(self,event):
                FactorSelections=self.WithinVariable.GetSelections()
                Factor=self.WithinVariable.GetItems()
                ColName=self.ListCol.GetItems()
                for i in FactorSelections:
                        name=Factor[i]
                        fin=name.find('(')
                        facttmp=['_?_']
                        if fin !=-1:
                                facttmp.append(name[fin:len(name)])
                                name=name[0:fin]
                        Factor[i]="".join(facttmp)
                        ColName.insert(self.WithinIndex[i],name)
                        self.WithinIndex[i]=''
                        self.Within[i]=[]

                tmp=[]
                for i in self.WithinIndex:
                        if i !='':
                                tmp.append(i)
                self.WithinIndex=tmp
                tmpvalue=[]
                for i in self.Within:
                        if i!=[]:
                                tmpvalue.append(i)
                ColNameNew=[]
                for i in ColName:
                        if i!='':
                                ColNameNew.append(i)
                for i in ColName:
                        if i=='':
                                ColNameNew.append('')
                self.Within=tmpvalue
                self.ListCol.SetItems(ColNameNew)
                self.WithinVariable.SetItems(Factor)
        def AddBetween(self,event):
                ColNumber=self.ListCol.GetSelections()
                ColName=self.ListCol.GetItems()
                name=self.BetweenVariable.GetItems()
                for i in ColNumber:
                        name.append(ColName[i])
                        index=self.ColName.index(ColName[i])
                        self.BetweenIndex.append(index)
                        self.Between.append(self.TabValue[index])
                        ColName[i]=''
                ColNameNew=[]
                for i in ColName:
                        if i !='':
                                ColNameNew.append(i)
                self.ListCol.SetItems(ColNameNew)
                self.BetweenVariable.SetItems(name)
        def RmBetween(self,event):
                Selections=self.BetweenVariable.GetSelections()
                name=self.BetweenVariable.GetItems()
                ColName=self.ListCol.GetItems()
                for i in Selections:
                        ColName.insert(self.BetweenIndex[i],name[i])
                        self.Between[i]=[]
                        self.BetweenIndex=''
                        name[i]=''

                tmp=[]
                
                for i in self.BetweenIndex:
                        if i !='':
                                tmp.append(i)
                NameNew=[]
                for i in name:
                        if i !='':
                                NameNew.append(i)
                self.BetweenIndex=tmp
                tmpvalue=[]
                for i in self.Between:
                        if i !=[]:
                                tmpvalue.append(i)
                ColNameNew=[]
                for i in ColName:
                        if i!='':
                                ColNameNew.append(i)
                for i in ColName:
                        if i=='':
                                ColNameNew.append('')
                self.Between=tmpvalue
                self.ListCol.SetItems(ColNameNew)
                self.BetweenVariable.SetItems(NameNew)
        def AddCovariate(self,event):
                ColNumber=self.ListCol.GetSelections()
                ColName=self.ListCol.GetItems()
                name=self.CovariateVariable.GetItems()
                for i in ColNumber:
                        name.append(ColName[i])
                        index=self.ColName.index(ColName[i])
                        self.CovariateIndex.append(index)
                        self.Covariate.append(self.TabValue[index])
                        ColName[i]=''
                ColNameNew=[]
                for i in ColName:
                        if i !='':
                                ColNameNew.append(i)

                self.ListCol.SetItems(ColNameNew)
                self.CovariateVariable.SetItems(name)
        def RmCovariate(self,event):
                Selections=self.CovariateVariable.GetSelections()
                name=self.CovariateVariable.GetItems()
                ColName=self.ListCol.GetItems()
                for i in Selections:
                        ColName.insert(self.CovariateIndex[i],name[i])
                        self.CovariateIndex[i]=''
                        self.Covariate[i]=[]
                        name[i]=''

                tmp=[]
                nametmp=[]
                for i in self.CovariateIndex:
                        if i !='':
                                tmp.append(i)
                NameNew=[]
                for i in name:
                        if i !='':
                                NameNew.append(i)
                tmpvalue=[]
                for i in self.Covariate:
                        if i !=[]:
                                tmpvalue.append(i)
                ColNameNew=[]
                for i in ColName:
                        if i!='':
                                ColNameNew.append(i)
                for i in ColName:
                        if i=='':
                                ColNameNew.append('')
                self.Covariate=tmpvalue
                self.CovariateIndex=tmp
                self.ListCol.SetItems(ColNameNew)
                self.CovariateVariable.SetItems(NameNew)
        def ColSelected(self,event):
                self.WithinAdd.Enable()
                self.BetweenAdd.Enable()
                self.CovariateAdd.Enable()
                self.WithinRm.Disable()
                self.BetweenRm.Disable()
                self.CovariateRm.Disable()
                if self.SubjectVariable.GetLabel()=="":
                        self.SubjectRm.Disable()
                        self.SubjectAdd.Enable()
                else:
                        self.SubjectRm.Enable()
                        self.SubjectAdd.Disable()
        def WithinSelected(self,event):
                self.SubjectAdd.Disable()
                self.WithinAdd.Disable()
                self.BetweenAdd.Disable()
                self.CovariateAdd.Disable()
                self.SubjectRm.Disable()
                self.WithinRm.Enable()
                self.BetweenRm.Disable()
                self.CovariateRm.Disable()
        def BetweenSelected(self,event):
                self.SubjectAdd.Disable()
                self.WithinAdd.Disable()
                self.BetweenAdd.Disable()
                self.CovariateAdd.Disable()
                self.SubjectRm.Disable()
                self.WithinRm.Disable()
                self.BetweenRm.Enable()
                self.CovariateRm.Disable()
        def CovariateSelected(self,event):
                self.SubjectAdd.Disable()
                self.WithinAdd.Disable()
                self.BetweenAdd.Disable()
                self.CovariateAdd.Disable()
                self.SubjectRm.Disable()
                self.WithinRm.Disable()
                self.BetweenRm.Disable()
                self.CovariateRm.Enable()
### Class definition du Model
class DefineModel:
        def __init__(self,level,sujet,groupe,covariate):
                # level,groupe, sujet , covariate are list
                if groupe==[]:
                        groupevide=True
                else:
                        groupevide=False
                if covariate==[]:
                        covvide=True
                else:
                        covvide=False
                
                groupe= np.array(groupe)
                groupe=groupe.T
                sujet= np.array(sujet)
                covariate= np.array(covariate)
                covariate=covariate.T
                levelArray=np.array(level)
                combi=levelArray.prod()
                condition=combi*len(sujet)
                conditiontmp=condition
                ModelWithin=np.zeros((int(condition),int(len(level))))
                if level!=[]:
                        for k,i in enumerate(level):
                                repet=conditiontmp/i
                                conditiontmp=repet
                                for j in range(i):
                                        fact=np.ones((repet,1))*j+1
                                        debut=j*repet
                                        fin=(j+1)*repet
                                        ModelWithin[debut:fin,k]=fact[:,0]
                                n=j
                                while ModelWithin[condition-1,k]==0:
                                        for j in range(i):
                                            n+=1
                                            fact=np.ones((repet,1))*j+1
                                            debut=n*repet
                                            fin=(n+1)*repet
                                            ModelWithin[debut:fin,k]=fact[:,0]
                        
                else:
                        ModelWithin=np.array(False)       
                self.Within=ModelWithin

                
                ModelSujet=np.zeros(int((condition)))
                MarkGroup=0
                MarkCov=0
                try:
                        ModelGroupe=np.zeros((condition,groupe.shape[1]))
                        MarkGroup=1
                except:
                        ModelGroupe=np.zeros(int((condition)))
                try:
                        ModelCovariate=np.zeros((condition,covariate.shape[1]))
                        MarkCov=1
                except:
                        ModelCovariate=np.zeros(int((condition)))
                combi=int(combi)
                for i in range(combi):
                        debut=i*len(sujet)
                        fin=(i+1)*len(sujet)
                        ModelSujet[debut:fin]=sujet
                        if groupevide:
                               #ModelGroupe=np.array([])
                                ModelGroupe=False
                        else:
                                if MarkGroup==1:
                                        ModelGroupe[debut:fin,:]=groupe
                                else:
                                        ModelGroupe[debut:fin]=groupe
                        if covvide:
                                #ModelCovariate=np.array([])
                                ModelCovariate=False
                        else:
                                if MarkCov==1:
                                        ModelCovariate[debut:fin,:]=covariate
                                else:
                                        ModelCovariate[debut:fin]=covariate
                self.Subject=ModelSujet
                self.Groupe=ModelGroupe
                self.Covariate=ModelCovariate

                
      
class Summary:
        def __init__(self,ColWithin,ColBetween,ColSubject,ColCovariate,PanelTxt):
                txt=['SUMMARY\n']
                txt.append('SUBJECT FACTOR COL :\n')
                txt.append(ColSubject)
                txt.append('\n')
                tmp=['Within SUBJECT FACTOR COL :\n']
                for i in ColWithin:
                        tmp.append(', ')
                        tmp.append(i)
                tmp.remove(', ')
                txt.append("".join(tmp))
                txt.append('\n')
                tmp=['BETWEEN SUBJECT FACTOR COL :\n']     
                for i in ColBetween:
                        tmp.append(', ')
                        tmp.append(i)
                tmp.remove(', ')
                txt.append("".join(tmp))
                txt.append('\n')
                tmp=['COVARIATE SUBJECT FACTOR COL :\n'] 
                for i in ColCovariate:
                        tmp.append(', ')
                        tmp.append(i)
                tmp.remove(', ')
                txt.append("".join(tmp))
                PanelTxt.SetLabel("".join(txt))
                 
class ReturnInfomation:
        def __init__(self,chemin):
                text=[]
                info=Stat.Anova(chemin,self)
                info.file.close()
                file=tables.openFile(chemin,mode='r')
                formule=['R-FORMULA : aov(']
                formule.append(info.Formule)
                formule.append(')\n\n')
                text.append("".join(formule))
                Within=['Within FACTOR(S) NAME(S)[LEVELS] : ']
                Factor=file.getNode('/Names/Within')
                Factor=Factor.read()
                Level=file.getNode('/Info/Level')
                Level=Level.read()
                if Factor != False:
                        for i,f in enumerate(Factor):
                                Within.append(', ')
                                Within.append(f)
                                Within.append(' [')
                                Within.append(str(Level[i]))
                                Within.append(']')
                        Within.remove(', ')
                        Within.append('\n\n')
                        text.append("".join(Within))
                
                NameBetween=file.getNode('/Names/Between')
                BetweenFactor=file.getNode('/Model/Between')
                BetweenFactor=BetweenFactor.read()
                NameBetween=NameBetween.read()
                if NameBetween != False:
                        between=['BETWEEN FACTOR(S) NAME(S): ']
                        for i,f in enumerate(NameBetween):
                                between.append(', ')
                                tmp=[]
                                try:
                                        BetweenLevel=str(int(BetweenFactor[:,i].max()))
                                except:
                                        BetweenLevel=str(int(BetweenFactor.max()))
                                tmp.append(f)
                                tmp.append('[')
                                tmp.append(BetweenLevel)
                                tmp.append(']')
                                between.append("".join(tmp))
                        between.remove(', ')
                        between.append('\n\n')
                        text.append("".join(between))
                Namecov=file.getNode('/Names/Covariate')
                Namecov=Namecov.read()
                if Namecov != False:
                        cov=['COVARIATE NAME(S): ']
                        for f in Namecov:
                                cov.append(', ')
                                cov.append(f)
                        cov.remove(', ')
                        cov.append('\n\n')
                        text.append("".join(cov))
                        self.CovariatePresent=True
                else:
                        self.CovariatePresent=False
                ErrorEph=file.getNode('/Error/Eph')
                ErrorEph=ErrorEph.read()
                if ErrorEph==False:
                        error='ALL EPH FILES ARE READED !!!'
                else:
                        error=['This Eph Files have a problem : \n']
                        n=0
                        for i,e in enumerate(ErrorEph):
                                if n == 10:
                                       n=0
                                       error.append(', ')
                                       error.append(e)
                                       error.append('\n')
                                else:
                                       error.append(', ')
                                       error.append(e)
                        error.remove(', ')
                        txt="".join(error)
                        txt=txt.replace(',','\n')
                        dlg = wx.MessageDialog(None,txt,"Error Eph Files", wx.OK|wx.ICON_ERROR)
                        result = dlg.ShowModal()
                        dlg.Destroy()          
                self.text=text
                file.close()


class CovariateDefinition(wx.Dialog):
        def __init__(self,Within,Between,Subject,Covariate,NameWithin,NameBetween,NameCovariate):
                wx.Dialog.__init__(self,None, -1, title = "Covariate Definition", size = (1000,500))
                self.MakeModal(True)
                FrameSizer=wx.BoxSizer(wx.VERTICAL)
                # load panel
                self.Correction=[]
                PanelSheet=wx.Panel(self,-1)
                SheetSizer=wx.BoxSizer(wx.VERTICAL)
                self.Sheet=CalculSheetCov(PanelSheet)
                SheetSizer.Add(self.Sheet,0,wx.EXPAND)
                PanelSheet.SetSizer(SheetSizer)
                FrameSizer.Add(PanelSheet,0,wx.EXPAND)
                FrameSizer.AddSpacer(10)
                
                ModifPanel=wx.Panel(self,-1)
                ModifiySizer=wx.BoxSizer(wx.HORIZONTAL)
                ButtonCancel=wx.Button(ModifPanel,1,label ="Cancel",size=(108,23))
                ModifiySizer.Add(ButtonCancel,0,wx.EXPAND)
                Buttonok=wx.Button(ModifPanel,2,label ="OK",size=(108,23))
                ModifiySizer.Add(Buttonok,0,wx.EXPAND)
                ModifPanel.SetSizerAndFit(ModifiySizer)
                FrameSizer.Add(ModifPanel,0,wx.EXPAND)
                self.SetSizerAndFit(FrameSizer)

                wx.EVT_BUTTON(self, 1,self.Cancel)
                wx.EVT_BUTTON(self, 2,self.OK)
                self.Show(True)
                # subject
                row=0
                NbRow=len(Subject)
                NbCol=1
                
                if len(Within.shape)!=1:
                        NbCol+=Within.shape[1]
                else:
                        NbCol+=1

                if len(Covariate.shape)!=1:
                        NbCol+=Covariate.shape[1]
                else:
                        NbCol+=1
                        
                try:
                        if len(Between.shape)!=1:
                                NbCol+=Between.shape[1]
                        else:
                                NbCol+=1
                except:
                       pass
                
                 
                self.Sheet.SetNumberRows(NbRow)
                self.Sheet.SetNumberCols(NbCol)
                for s in Subject:
                        value=str(int(s))
                        self.Sheet.SetCellValue(row,0,value)
                        row+=1
                col=1
                ColDisable=[0]
                # Within
                if NameWithin!=False:
                        for i,n in enumerate(NameWithin):
                                self.Sheet.SetColLabelValue(col,n)
                                if len(Within.shape)!=1:
                                        ColValues=Within[:,i]
                                else:
                                        ColValues=Within
                                row=0
                                for v in ColValues:
                                        value=str(int(v))
                                        self.Sheet.SetCellValue(row,col,value)
                                        row+=1
                                ColDisable.append(col)
                                col+=1
                                
                        
                # Between
                if NameBetween!=False:
                        for i,n in enumerate(NameBetween):
                                self.Sheet.SetColLabelValue(col,n)
                                if len(Between.shape)!=1:
                                        ColValues=Between[:,i]
                                else:
                                        ColValues=Between
                                row=0
                                for v in ColValues:
                                        value=str(int(v))
                                        self.Sheet.SetCellValue(row,col,value)
                                        row+=1
                                ColDisable.append(col)
                                col+=1
                self.ColCov=[]
                #Covariate
                if NameCovariate!=False:
                        for i,n in enumerate(NameCovariate):
                                self.Sheet.SetColLabelValue(col,n)
                                if len(Covariate.shape)!=1:
                                        ColValues=Covariate[:,i]
                                else:
                                        ColValues=Covariate
                                row=0
                                for v in ColValues:
                                        value=str(float(v))
                                        self.Sheet.SetCellValue(row,col,value)
                                        row+=1
                                self.ColCov.append(col)
                                col+=1
                self.NbRow=NbRow
                self.Sheet.Bind(wx.EVT_CHAR,self.OnKeyPress)
                self.Sheet.DisableCellEditControl
                self.ShowModal()
                
        def OK(self,event):
                NewModelCov=np.zeros((self.NbRow,len(self.ColCov)))
                for i,c in enumerate(self.ColCov):
                     for r in range(self.NbRow):
                             cell=self.Sheet.GetCellValue(r,c)
                             NewModelCov[r,i]=float(cell)
                self.Covariate=NewModelCov
                self.Correction=True
                self.MakeModal(False)
                self.Close()
        def Cancel(self,event):
                self.Correction=False
                self.MakeModal(False)
                self.Close()
        def OnKeyPress(self,event):
                if event.GetKeyCode()==3:
                        self.Sheet.Copy()
                elif event.GetKeyCode()==22:
                        self.Sheet.Paste()
                else:
                        
                        event.Skip()
               
                             
                        
                
class CalculSheetCov(sheet.CSheet):
        def __init__(self, parent):
                sheet.CSheet.__init__(self, parent)
                self.SetNumberRows(40)
                self.SetNumberCols(9)
                self.SetColLabelValue(0,'subject')
                                       
                
                
                
                        
                                         

