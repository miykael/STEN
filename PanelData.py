import wx
import os
import PanelEntry
from Information import ReturnInfomation
import wx.lib.sheet


class CreateDataset(wx.Panel):

    """
    This panel contains the functions to create a new dataset, to load
    and modify an existing dataset and to specify the result folder.
    """

    def __init__(self, PanelData, MainFrame):

        # Create Data Frame window
        wx.Panel.__init__(self, parent=PanelData, style=wx.SUNKEN_BORDER)

        # Specify relevant variables
        self.MainFrame = MainFrame
        self.MainFrame.saved = False
        self.MainFrame.Dataset = {}
        # TODO: What about this H5?
        self.MainFrame.H5 = []

        # Panel: Data Handler
        self.PanelDataHandler = wx.Panel(self, wx.ID_ANY)
        sizerPanelDataHandler = wx.BoxSizer(wx.VERTICAL)

        # Text: Create, Modify or Save Dataset
        TxtDataset = wx.StaticText(
            self.PanelDataHandler, wx.ID_ANY, style=wx.CENTRE,
            label="Create or Modify Dataset")
        sizerPanelDataHandler.Add(TxtDataset, 0, wx.EXPAND)
        sizerPanelDataHandler.AddSpacer(3)

        # Panel: Create, Modify or Save Dataset
        PanelDataset = wx.Panel(self.PanelDataHandler, wx.ID_ANY)
        sizerPanelDataset = wx.BoxSizer(wx.HORIZONTAL)
        self.MainFrame.ButtonDataCreate = wx.Button(
            PanelDataset, wx.ID_ANY, size=(175, 28), style=wx.CENTRE,
            label="&Create new Dataset")
        sizerPanelDataset.Add(self.MainFrame.ButtonDataCreate, 0, wx.EXPAND)
        sizerPanelDataset.AddSpacer(5)
        self.MainFrame.ButtonDataModify = wx.Button(
            PanelDataset, wx.ID_ANY, size=(175, 28), style=wx.CENTRE,
            label="&Modify loaded Dataset")
        self.MainFrame.ButtonDataModify.Disable()
        sizerPanelDataset.Add(self.MainFrame.ButtonDataModify, 0, wx.EXPAND)
        PanelDataset.SetSizer(sizerPanelDataset)
        sizerPanelDataHandler.Add(PanelDataset, 0, wx.EXPAND)
        sizerPanelDataHandler.AddSpacer(15)

        # Text: Save Dataset
        TxtSave = wx.StaticText(
            self.PanelDataHandler, wx.ID_ANY, style=wx.CENTRE,
            label="Save Dataset")
        sizerPanelDataHandler.Add(TxtSave, 0, wx.EXPAND)
        sizerPanelDataHandler.AddSpacer(3)

        # Panel: Save Dataset
        PanelSaveFile = wx.Panel(self.PanelDataHandler, wx.ID_ANY)
        sizerPanelSaveFile = wx.BoxSizer(wx.HORIZONTAL)
        self.DataFile = wx.TextCtrl(
            PanelSaveFile, wx.ID_ANY, size=(500, 21),
            value=os.path.join(os.getcwd(), 'dataset.h5'))
        sizerPanelSaveFile.Add(self.DataFile, 0, wx.EXPAND)
        self.MainFrame.ButtonDataSave = wx.Button(
            PanelSaveFile, wx.ID_ANY, label="&Save Dataset", size=(110, 28))
        self.MainFrame.ButtonDataSave.Disable()
        sizerPanelSaveFile.Add(self.MainFrame.ButtonDataSave, 0, wx.EXPAND)
        PanelSaveFile.SetSizer(sizerPanelSaveFile)
        sizerPanelDataHandler.Add(PanelSaveFile, 0, wx.EXPAND)
        sizerPanelDataHandler.AddSpacer(15)

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
            PanelLoadFile, wx.ID_ANY, size=(500, 21),
            value=os.path.join(os.getcwd(), 'dataset.h5'))
        sizerPanelLoadFile.Add(self.DataFile, 0, wx.EXPAND)
        self.MainFrame.ButtonDataLoad = wx.Button(
            PanelLoadFile, wx.ID_ANY, label="&Load Dataset", size=(110, 28))
        sizerPanelLoadFile.Add(self.MainFrame.ButtonDataLoad, 0, wx.EXPAND)
        PanelLoadFile.SetSizer(sizerPanelLoadFile)
        sizerPanelDataHandler.Add(PanelLoadFile, 0, wx.EXPAND)
        sizerPanelDataHandler.AddSpacer(15)

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
        PanelResultSizer.Add(self.TextResult, 0, wx.EXPAND)
        self.MainFrame.ButtonResult = wx.Button(
            PanelResult, wx.ID_ANY, label="&Result Folder", size=(110, 28))
        PanelResultSizer.Add(self.MainFrame.ButtonResult, 0, wx.EXPAND)
        PanelResult.SetSizer(PanelResultSizer)
        sizerPanelDataHandler.Add(PanelResult, 0, wx.EXPAND)
        sizerPanelDataHandler.AddSpacer(15)

        # Create vertical structure of Data Handler Frame
        sizerFrame = wx.BoxSizer(wx.VERTICAL)
        sizerFrame.AddSpacer(3)
        sizerFrame.Add(self.PanelDataHandler, 0, wx.EXPAND)
        self.SetSizer(sizerFrame)
        self.PanelDataHandler.SetSizer(sizerPanelDataHandler)

        # Button Events
        wx.EVT_BUTTON(self, self.MainFrame.ButtonDataCreate.Id,
                      self.createData)
        wx.EVT_BUTTON(self, self.MainFrame.ButtonDataModify.Id,
                      self.modifyData)
        wx.EVT_BUTTON(self, self.MainFrame.ButtonDataSave.Id, self.saveData)
        wx.EVT_BUTTON(self, self.MainFrame.ButtonDataLoad.Id, self.loadData)
        wx.EVT_BUTTON(self, self.MainFrame.ButtonResult.Id, self.resultFolder)

    def createData(self, event):
        """Opens DataEntry Panel with new dataset"""
        # Popup Window that preexisting dataset will be overwritten
        if self.MainFrame.Dataset != {}:
            dlg = wx.MessageDialog(
                self, style=wx.OK | wx.CANCEL,
                caption='A Dataset is already loaded',
                message='A dataset is already loaded, are you sure that you ' +
                        'want to create a new dataset?')
            answer = dlg.ShowModal()
            dlg.Destroy()
            if answer == wx.ID_OK:
                self.MainFrame.Dataset = {}
                self.DataWindow = PanelEntry.DataEntry(self.MainFrame)
                self.DataWindow.Show(True)
                self.MainFrame.Show(False)
                self.MainFrame.ButtonDataModify.Disable()
                self.MainFrame.ButtonDataSave.Disable()
        else:
            self.DataWindow = PanelEntry.DataEntry(self.MainFrame)
            self.DataWindow.Show(True)
            self.MainFrame.Show(False)

    def modifyData(self, event):
        """Opens DataEntry Panel with existing dataset"""
        self.DataWindow = PanelEntry.DataEntry(self.MainFrame)
        self.DataWindow.Show(True)
        self.MainFrame.Show(False)

    def saveData(self, event):
        """Save an already loaded or created dataset as an H5 file"""
        # TODO: how to save dataset with pytables?
        # TODO: how to make sure that not only previous analysis are stored?
        self.MainFrame.saved = True

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
            self.MainFrame.H5 = self.PathFile
            info = ReturnInfomation(self.PathFile)
            self.TxtInfo.SetLabel("".join(info.text))
            if info.CovariatePresent:
                self.MainFrame.AnovaWave.PostHocCheckBox.Disable()
                self.MainFrame.AnovaIS.PostHocCheckBox.Disable()
                self.MainFrame.AnovaWave.PostHocCheckBox.SetValue(False)
                self.MainFrame.AnovaIS.PostHocCheckBox.SetValue(False)
            else:
                self.MainFrame.AnovaWave.PostHocCheckBox.Enable()
                self.MainFrame.AnovaIS.PostHocCheckBox.Enable()

        else:
            self.MainFrame.H5 = []
            self.DataFile.SetLabel('')

    def resultFolder(self, event):
        """Opens the DataResult Panel"""
        dlg = wx.DirDialog(None, "Select Result Folder",
                           defaultPath=self.TextResult.Value,
                           style=wx.DD_DEFAULT_STYLE)
        answer = dlg.ShowModal()
        if answer == wx.ID_OK:
            self.PathResult = dlg.GetPath()
            self.TextResult.SetValue(self.PathResult)
