import wx
import os
from EntryPanel import DataEntry
from Information import ReturnInfomation

# tables:
# /Data/*subject/*condition # array
# /DataGFP/*subject/*condition # array
# /Model/Within # array
# /Model/Between # array
# /Model/Covariate # array
# /Model/Subject # array
# /Names/Within # List
# /Names/Between
# /Names/Covariate
# /Info/Shape
# /Info/FS # frequncy sampling
# /Info/level # array
# /Info/ColFactor
# /Info/ColWithin
# /Info/ColBetween
# /Info/ColCovaraite
# /Info/Param # info si parametric ou non
# /Sheet/Value # list
# /Sheet/NoEmptyCol # array
# /Sheet/ColName # list
# /Sheet/Dim # array
# /Error/EPH
# /Result/Anova/All/P # P value for All electrodes and IS
# /Result/Anova/All/F # F value only in parametric
# /Result/Anova/GFP/P # P value for GFP
# /Result/Anova/GFP/F # F value
# /Result/PostHoc/All/P # P value for All electrodes and IS
# /Result/PostHoc/All/T # T value
# /Result/PostHoc/GFP/P # P value for GFP
# /Result/PostHoc/GFP/T # T value
# /Result/IntermediateResult # place for storing intermediate results


class info(wx.Panel):

    """ TODO: translate to english
    Panle de gauche de l'application demande les dossier
    EPH, resultats, les facteurs, ...."""

    def __init__(self, Conteneur, Main):
        # wx.Frame.__init__(self, None, -1, title = "test", size = (500,300))
        wx.Panel.__init__(self, parent=Conteneur)
        FrameSizer = wx.BoxSizer(wx.VERTICAL)
        # definition des OutPut
        self.PathResult = None
        self.NbFactor = 0
        self.Level = {}
        self.Analyse = None
        self.Main = Conteneur
        self.ExportData = Main
        self.ExportData.H5 = []
        # panel 1 = folders

        # definition panel 1
        self.PanelFichier = wx.Panel(self, -1)
        PanelFichierSizer = wx.BoxSizer(wx.VERTICAL)
        PanelFichierSizer.AddSpacer(20)

        # selection Load old file
        PanelLoad = wx.Panel(self.PanelFichier, -1)
        PanelLoadSizer = wx.BoxSizer(wx.HORIZONTAL)
        PanelLoadSizer.AddSpacer(5)
        self.DataFile = wx.TextCtrl(
            PanelLoad, -1, value="", style=wx.TE_READONLY, size=(550, 21))
        self.DataFile.SetBackgroundColour(wx.WHITE)
        PanelLoadSizer.Add(self.DataFile, 0, wx.EXPAND)
        ButtonDataLoad = wx.Button(
            PanelLoad, 4, label="Load File", size=(108, 23))
        PanelLoadSizer.Add(ButtonDataLoad, 0, wx.EXPAND)
        PanelLoad.SetSizer(PanelLoadSizer)
        PanelFichierSizer.Add(PanelLoad, 0, wx.EXPAND)
        PanelFichierSizer.AddSpacer(10)

        #  selection result folder
        PanelRes = wx.Panel(self.PanelFichier, -1)
        PanelResSizer = wx.BoxSizer(wx.HORIZONTAL)
        PanelResSizer.AddSpacer(5)
        self.TextResult = wx.TextCtrl(
            PanelRes, -1, value="", style=wx.TE_READONLY, size=(550, 21))
        self.TextResult.SetBackgroundColour(wx.WHITE)
        PanelResSizer.Add(self.TextResult, 0, wx.EXPAND)
        self.ButtonResult = wx.Button(
            PanelRes, 2, label="Select result folder", size=(108, 23))
        PanelResSizer.Add(self.ButtonResult, 0, wx.EXPAND)
        PanelRes.SetSizer(PanelResSizer)
        PanelFichierSizer.Add(PanelRes, 0, wx.EXPAND)
        PanelFichierSizer.AddSpacer(10)

        # lie les sizer au panel
        self.PanelFichier.SetSizer(PanelFichierSizer)
        # on mets le panel de fichier dans le sizer de la frame
        FrameSizer.Add(self.PanelFichier, 0, wx.EXPAND)
        FrameSizer.AddSpacer(10)

        # panel 2 = INfo avec creation Data + information sur les datas
        # text data
        PanelInfo = wx.Panel(self, -1)
        InfoSizer = wx.BoxSizer(wx.HORIZONTAL)
        InfoSizer.AddSpacer(5)
        PanelData = wx.Panel(PanelInfo, -1)
        DataSizer = wx.BoxSizer(wx.VERTICAL)
        DataTxt = wx.StaticText(
            PanelData, -1, label="Data selection ", style=wx.CENTRE)
        DataSizer.Add(DataTxt, 0, wx.EXPAND)
        DataSizer.AddSpacer(5)
        # panel 3 avec les boutton creation
        ButtonDataCreate = wx.Button(
            PanelData, 3, label="Create Data File / Modifiy data")
        DataSizer.Add(ButtonDataCreate, 0, wx.EXPAND)
        PanelData.SetSizer(DataSizer)
        InfoSizer.Add(PanelData)
        InfoSizer.AddSpacer(100)
        self.TxtInfo = wx.StaticText(
            PanelInfo, -1, label="", style=wx.ALIGN_LEFT)
        InfoSizer.Add(self.TxtInfo)
        PanelInfo.SetSizer(InfoSizer)
        # lie les sizer au panel
        FrameSizer.Add(PanelInfo, 0, wx.EXPAND)
        FrameSizer.AddStretchSpacer()

        # Panel Progression
        PanelFinal = wx.Panel(self, -1)
        FinalSizer = wx.BoxSizer(wx.HORIZONTAL)
        FinalSizer.AddSpacer(50)
        self.ProgressTxt = wx.StaticText(
            PanelFinal, -1, label="", style=wx.ALIGN_LEFT)
        FinalSizer.Add(self.ProgressTxt, 0, wx.EXPAND)
        PanelFinal.SetSizer(FinalSizer)

        # lie les sizer au panel
        FrameSizer.Add(PanelFinal, 0, wx.EXPAND)
        FrameSizer.AddStretchSpacer()
        # on lie le size au frame sizer
        self.SetSizer(FrameSizer)
        # FrameSizer.SetSizeHints(self)
        # self.SetSize((800,200))

        # evenement
        # wx.EVT_BUTTON(self, 1,self.Eph)
        wx.EVT_BUTTON(self, 2, self.Result)
        wx.EVT_BUTTON(self, 3, self.CreateData)
        wx.EVT_BUTTON(self, 4, self.LoadData)

    def Result(self, event):
        self.TextResult.SetBackgroundColour(wx.WHITE)
        wx.InitAllImageHandlers()
        dlg = wx.DirDialog(None, "select Result folder",
                           defaultPath=os.getcwd(), style=wx.DD_DEFAULT_STYLE)
        retour = dlg.ShowModal()
        self.PathResult = dlg.GetPath()
        os.chdir(self.PathResult)
        self.TextResult.SetLabel(dlg.GetPath())
        dlg.Show(True)
        dlg.Destroy()

    def LoadData(self, event):
        dlg = wx.FileDialog(
            None, "Load H5 file", wildcard="*.h5", style=wx.FD_OPEN)
        retour = dlg.ShowModal()
        if retour == wx.ID_OK:
            chemin = dlg.GetPath()
            fichier = dlg.GetFilename()
            self.DataFile.SetLabel(chemin)
            self.ExportData.H5 = chemin
            dlg.Destroy()
            dlg.Show(True)
            info = ReturnInfomation(chemin)
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
            self.ExportData.H5 = []
            self.DataFile.SetLabel('')

    def CreateData(self, event):
        Data = DataEntry(self)
        Data.Show(True)
        self.ExportData.Show(False)


class Summary:

    def __init__(self, ColWithin, ColBetween,
                 ColSubject, ColCovariate, PanelTxt):
        txt = ['SUMMARY\n']
        txt.append('SUBJECT FACTOR COL :\n')
        txt.append(ColSubject)
        txt.append('\n')
        tmp = ['Within SUBJECT FACTOR COL :\n']
        for i in ColWithin:
            tmp.append(', ')
            tmp.append(i)
        tmp.remove(', ')
        txt.append("".join(tmp))
        txt.append('\n')
        tmp = ['BETWEEN SUBJECT FACTOR COL :\n']
        for i in ColBetween:
            tmp.append(', ')
            tmp.append(i)
        tmp.remove(', ')
        txt.append("".join(tmp))
        txt.append('\n')
        tmp = ['COVARIATE SUBJECT FACTOR COL :\n']
        for i in ColCovariate:
            tmp.append(', ')
            tmp.append(i)
        tmp.remove(', ')
        txt.append("".join(tmp))
        PanelTxt.SetLabel("".join(txt))
