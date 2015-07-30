import wx
import os
from PanelEntry import DataEntry
from Information import ReturnInfomation


class OnOpen(wx.Panel):

    """
    This panel contains the functions to create a new dataset, to load
    and modify an existing dataset and to specify the result folder.
    """

    def __init__(self, PanelData, MainFrame):

        # Create Data Frame window
        wx.Panel.__init__(self, parent=PanelData, style=wx.SUNKEN_BORDER)

        # Panel: Data Handler
        self.PanelDataHandler = wx.Panel(self, wx.ID_ANY)
        sizerPanelDataHandler = wx.BoxSizer(wx.VERTICAL)

        # Text: Load Dataset
        TxtLoad = wx.StaticText(
            self.PanelDataHandler, wx.ID_ANY, style=wx.CENTRE,
            label="Load existing Dataset")
        sizerPanelDataHandler.Add(TxtLoad, 0, wx.EXPAND)
        sizerPanelDataHandler.AddSpacer(3)

        # Panel: Load Dataset
        PanelLoadFile = wx.Panel(self.PanelDataHandler, wx.ID_ANY)
        sizerPanelLoadFile = wx.BoxSizer(wx.HORIZONTAL)
        self.DataFile = wx.TextCtrl(
            PanelLoadFile, wx.ID_ANY, size=(500, 21), value=os.getcwd())
        self.DataFile.SetBackgroundColour(wx.WHITE)
        sizerPanelLoadFile.Add(self.DataFile, 0, wx.EXPAND)
        ButtonDataLoad = wx.Button(
            PanelLoadFile, wx.ID_ANY, label="Load File", size=(110, 28))
        sizerPanelLoadFile.Add(ButtonDataLoad, 0, wx.EXPAND)
        PanelLoadFile.SetSizer(sizerPanelLoadFile)
        sizerPanelDataHandler.Add(PanelLoadFile, 0, wx.EXPAND)
        sizerPanelDataHandler.AddSpacer(18)

        # Text: Select Result Folder
        TxtSelect = wx.StaticText(
            self.PanelDataHandler, wx.ID_ANY, style=wx.CENTRE,
            label="Select Result Folder")
        sizerPanelDataHandler.Add(TxtSelect, 0, wx.EXPAND)
        sizerPanelDataHandler.AddSpacer(3)

        # Panel: Select Result Folder
        PanelResult = wx.Panel(self.PanelDataHandler, wx.ID_ANY)
        PanelResultSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.TextResult = wx.TextCtrl(
            PanelResult, wx.ID_ANY, size=(500, 21),
            value=os.path.join(os.getcwd(), 'STEN'))
        self.TextResult.SetBackgroundColour(wx.WHITE)
        PanelResultSizer.Add(self.TextResult, 0, wx.EXPAND)
        ButtonResult = wx.Button(
            PanelResult, wx.ID_ANY, label="Select Folder", size=(110, 28))
        PanelResultSizer.Add(ButtonResult, 0, wx.EXPAND)
        PanelResult.SetSizer(PanelResultSizer)
        sizerPanelDataHandler.Add(PanelResult, 0, wx.EXPAND)
        sizerPanelDataHandler.AddSpacer(18)

        # Text: Create or Modify Dataset
        TxtDataset = wx.StaticText(
            self.PanelDataHandler, wx.ID_ANY, style=wx.CENTRE,
            label="Data Selection")
        sizerPanelDataHandler.Add(TxtDataset, 0, wx.EXPAND)
        sizerPanelDataHandler.AddSpacer(3)

        # Panel: Create or Modify Dataset
        PanelDataset = wx.Panel(self.PanelDataHandler, wx.ID_ANY)
        sizerPanelDataset = wx.BoxSizer(wx.HORIZONTAL)
        ButtonDataCreate = wx.Button(
            PanelDataset, wx.ID_ANY, size=(350, 28), style=wx.CENTRE,
            label="Create new Dataset / Modify loaded Dataset")
        sizerPanelDataset.Add(ButtonDataCreate, 0, wx.EXPAND)
        PanelDataset.SetSizer(sizerPanelDataset)
        sizerPanelDataHandler.Add(PanelDataset, 0, wx.EXPAND)
        sizerPanelDataHandler.AddSpacer(18)

        # Create vertical structure of Data Handler Frame
        sizerFrame = wx.BoxSizer(wx.VERTICAL)
        sizerFrame.Add(self.PanelDataHandler, 0, wx.EXPAND)
        self.SetSizer(sizerFrame)
        self.PanelDataHandler.SetSizer(sizerPanelDataHandler)

        # Button Events
        wx.EVT_BUTTON(self, ButtonDataLoad.Id, self.loadData)
        wx.EVT_BUTTON(self, ButtonResult.Id, self.resultAction)
        wx.EVT_BUTTON(self, ButtonDataCreate.Id, self.createData)

        # Specify Outputs
        # TODO: those variables are not needed here
        self.PathResult = None
        self.NbFactor = 0
        self.Level = {}
        self.Analyse = None
        # TODO: unclear why MainFrame is added here? Change name of ExportData?
        self.ExportData = MainFrame
        self.ExportData.H5 = []

    def loadData(self, event):
        """Opens the DataLoad Panel"""
        dlg = wx.FileDialog(
            None, "Load H5 file", wildcard="*.h5", style=wx.FD_OPEN,
            defaultDir=self.DataFile.Value)
        answer = dlg.ShowModal()
        # TODO: Does this code make sense? Can it be cleaned more?
        if answer == wx.ID_OK:
            self.PathFile = dlg.GetPath()
            self.DataFile.SetLabel(self.PathFile)
            self.ExportData.H5 = self.PathFile
            info = ReturnInfomation(self.PathFile)
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

    def resultAction(self, event):
        """Opens the DataResult Panel"""
        dlg = wx.DirDialog(None, "Select Result Folder",
                           defaultPath=self.TextResult.Value,
                           style=wx.DD_DEFAULT_STYLE)
        dlg.ShowModal()
        self.PathResult = dlg.GetPath()
        self.TextResult.SetValue(self.PathResult)

    def createData(self, event):
        """Opens the DataEntry Panel"""
        DataWindow = DataEntry(self)
        DataWindow.Show(True)


# TODO: this class is never used
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
