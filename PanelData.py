import wx
import os
import PanelEntry
import H5Tables
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
        self.DataSaveFile = wx.TextCtrl(
            PanelSaveFile, wx.ID_ANY, size=(500, 21),
            value=os.path.join(os.getcwd(), 'dataset.h5'))
        sizerPanelSaveFile.Add(self.DataSaveFile, 0, wx.EXPAND)
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
        self.DataLoadFile = wx.TextCtrl(
            PanelLoadFile, wx.ID_ANY, size=(500, 21),
            value=os.path.join(os.getcwd(), 'dataset.h5'))
        sizerPanelLoadFile.Add(self.DataLoadFile, 0, wx.EXPAND)
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
        # Popup Window to inform that preexisting dataset will be overwritten
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
        fileDirectory = os.path.dirname(self.DataSaveFile.Value)
        filename = os.path.basename(self.DataSaveFile.Value)
        dlg = wx.FileDialog(None, "Save Dataset as H5 File", wildcard="*.h5",
                            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
                            defaultDir=fileDirectory, defaultFile=filename)
        answer = dlg.ShowModal()
        filepath = dlg.GetPath()

        filename, file_extension = os.path.splitext(filepath)
        filename += '.h5'

        dlg.Destroy()
        if answer == wx.ID_OK:
            # TODO: this function doesn't consider additional H5 file content
            #       (e.g. from previous analysis)
            H5Tables.WriteDataset(filename, self.MainFrame.Dataset)
            self.DataSaveFile.SetValue(filename)
            self.MainFrame.saved = True

    def loadData(self, event):
        """Load a dataset from an H5 file"""
        # Popup Window to inform that preexisting dataset will be overwritten
        ok2proceed = False
        if self.MainFrame.Dataset != {}:
            dlg = wx.MessageDialog(
                self, style=wx.OK | wx.CANCEL,
                caption='A Dataset is already loaded',
                message='A dataset is already loaded, are you sure that you ' +
                        'want to load a new dataset?')
            answer = dlg.ShowModal()
            dlg.Destroy()
            if answer == wx.ID_OK:
                ok2proceed = True
        else:
            ok2proceed = True

        # Load the dataset
        if ok2proceed:

            # Get path to H5 file
            fileDirectory = os.path.dirname(self.DataLoadFile.Value)
            filename = os.path.basename(self.DataLoadFile.Value)
            dlg = wx.FileDialog(None, "Load Dataset from a H5 File",
                                defaultDir=fileDirectory, defaultFile=filename,
                                wildcard="*.h5", style=wx.FD_OPEN)
            answer = dlg.ShowModal()
            filepath = dlg.GetPath()
            dlg.Destroy()
            if answer == wx.ID_OK:
                datatable = H5Tables.ReadDataset(filepath)
                self.MainFrame.Dataset = datatable.inputTable
                self.MainFrame.ButtonDataSave.Enable()
                self.MainFrame.ButtonDataModify.Enable()

#                # TODO: Check what panels should be accesable
#                if info.CovariatePresent:
#                    self.MainFrame.AnovaWave.PostHocCheckBox.Disable()
#                    self.MainFrame.AnovaIS.PostHocCheckBox.Disable()
#                    self.MainFrame.AnovaWave.PostHocCheckBox.SetValue(False)
#                    self.MainFrame.AnovaIS.PostHocCheckBox.SetValue(False)
#                else:
#                    self.MainFrame.AnovaWave.PostHocCheckBox.Enable()
#                    self.MainFrame.AnovaIS.PostHocCheckBox.Enable()
#
#            else:
#                self.MainFrame.H5 = []
#                self.DataLoadFile.SetLabel('')

    def resultFolder(self, event):
        """Opens the DataResult Panel"""
        dlg = wx.DirDialog(None, "Select Result Folder",
                           defaultPath=self.TextResult.Value,
                           style=wx.DD_DEFAULT_STYLE)
        answer = dlg.ShowModal()
        resultPath = dlg.GetPath()
        dlg.Destroy()
        if answer == wx.ID_OK:
            self.PathResult = resultPath
            self.TextResult.SetValue(self.PathResult)
