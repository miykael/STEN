import wx
from os.path import dirname


class AnovaWave(wx.Panel):

    """TODO: EXPLANATION TEXT"""

    def __init__(self, notebook, Mainframe):
        wx.Panel.__init__(self, parent=notebook)

        # Specify relevant variables
        self.Mainframe = Mainframe
        self.AnovaCheck = True
        self.PostHocCheck = False
        self.Param = True
        self.ParamPostHoc = True
        self.nIteration = 1000
        self.nIterationPostHoc = 1000
        self.Alpha = 0.05
        self.AlphaPostHoc = 0.05
        self.PtsConseq = 1
        self.PtsConseqPostHoc = 1
        self.Clust = 1
        self.ClustPostHoc = 1
        self.AnalyseType = 'GFP Only'
        self.SPIFile = ''
        self.SPIPath = ''

        # Panel: Perform ANOVA
        self.PanelAnova = wx.Panel(self, wx.ID_ANY)
        sizerAnova = wx.BoxSizer(wx.VERTICAL)

        # Add "Perform ANOVA" checkbox
        self.AnovaCheckBox = wx.CheckBox(self, wx.ID_ANY, "Perform ANOVA")
        self.AnovaCheckBox.SetValue(self.AnovaCheck)

        # Parametric / Non-Parametric Test Section
        PanelParam = wx.Panel(self.PanelAnova, wx.ID_ANY)
        PanelNonParam = wx.Panel(PanelParam, wx.ID_ANY)

        self.RadioParam = wx.RadioButton(
            PanelNonParam, wx.ID_ANY, 'Parametric Test', style=wx.RB_GROUP)
        self.RadioNonParam = wx.RadioButton(
            PanelNonParam, self.RadioParam.Id,
            'Non-Parametric Test (Bootstrapping)')

        # Iteration Section
        self.PanelIter = wx.Panel(PanelParam, wx.ID_ANY)
        TxtIter = wx.StaticText(self.PanelIter, wx.ID_ANY, label=" Iteration",
                                style=wx.ALIGN_CENTER)
        self.IterInput = wx.TextCtrl(
            self.PanelIter, wx.ID_ANY, value=str(self.nIteration),
            style=wx.TE_CENTRE)

        # Statistic (alpha, conseq pts, cluster size) Section
        PanelStats = wx.Panel(self.PanelAnova, wx.ID_ANY)
        PanelAlpha = wx.Panel(PanelStats, wx.ID_ANY)
        TxtAlpha = wx.StaticText(PanelAlpha, wx.ID_ANY, label=" Alpha Value",
                                 style=wx.ALIGN_CENTER)
        self.AlphaInput = wx.TextCtrl(
            PanelAlpha, wx.ID_ANY, value=str(self.Alpha), style=wx.TE_CENTRE)

        PanelPtsConseq = wx.Panel(PanelStats, wx.ID_ANY)
        PtsConseqText = wx.StaticText(
            PanelPtsConseq, wx.ID_ANY, label="Consecutive Time Frames",
            style=wx.ALIGN_CENTER)
        self.PtsConseqInput = wx.TextCtrl(
            PanelPtsConseq, wx.ID_ANY, value=str(self.PtsConseq),
            style=wx.TE_CENTRE)

        self.PanelClust = wx.Panel(PanelStats, wx.ID_ANY)
        TxtClust = wx.StaticText(
            self.PanelClust, wx.ID_ANY, label="Cluster Size (Electrodes)",
            style=wx.ALIGN_CENTER)
        self.ClustInput = wx.TextCtrl(
            self.PanelClust, wx.ID_ANY, value=str(self.Clust),
            style=wx.TE_CENTRE)

        # Create Structure of "Perform ANOVA"
        sizerNonParam = wx.BoxSizer(wx.VERTICAL)
        sizerNonParam.Add(self.RadioParam, 0, wx.TOP)
        sizerNonParam.AddSpacer(2)
        sizerNonParam.Add(self.RadioNonParam, 0, wx.TOP)
        PanelNonParam.SetSizer(sizerNonParam)

        sizerIter = wx.BoxSizer(wx.VERTICAL)
        sizerIter.Add(TxtIter, 0, wx.EXPAND)
        sizerIter.AddSpacer(2)
        sizerIter.Add(self.IterInput, 0, wx.EXPAND)
        self.PanelIter.SetSizer(sizerIter)

        sizerParam = wx.BoxSizer(wx.HORIZONTAL)
        sizerParam.Add(PanelNonParam, 0, wx.EXPAND)
        sizerParam.AddSpacer(10)
        sizerParam.Add(self.PanelIter, 0, wx.EXPAND)
        PanelParam.SetSizer(sizerParam)

        sizerAlpha = wx.BoxSizer(wx.VERTICAL)
        sizerAlpha.Add(TxtAlpha, 0, wx.EXPAND)
        sizerAlpha.Add(self.AlphaInput, 0, wx.EXPAND)
        PanelAlpha.SetSizer(sizerAlpha)

        sizerPtsConseq = wx.BoxSizer(wx.VERTICAL)
        sizerPtsConseq.Add(PtsConseqText, 0, wx.EXPAND)
        sizerPtsConseq.Add(self.PtsConseqInput, 0, wx.EXPAND)
        PanelPtsConseq.SetSizer(sizerPtsConseq)

        SizerPtsClust = wx.BoxSizer(wx.VERTICAL)
        SizerPtsClust.Add(TxtClust, 0, wx.EXPAND)
        SizerPtsClust.Add(self.ClustInput, 0, wx.EXPAND)
        self.PanelClust.SetSizer(SizerPtsClust)

        sizerStats = wx.BoxSizer(wx.HORIZONTAL)
        sizerStats.Add(PanelAlpha)
        sizerStats.AddSpacer(10)
        sizerStats.Add(PanelPtsConseq)
        sizerStats.AddSpacer(10)
        sizerStats.Add(self.PanelClust)
        sizerStats.AddSpacer(10)
        PanelStats.SetSizer(sizerStats)

        sizerAnova.Add(PanelParam, 0, wx.EXPAND)
        sizerAnova.AddSpacer(10)
        sizerAnova.Add(PanelStats, 0, wx.EXPAND)
        sizerAnova.AddSpacer(10)
        self.PanelAnova.SetSizer(sizerAnova)

        # Panel: Perform Post hoc Analysis
        self.PanelPostHoc = wx.Panel(self, wx.ID_ANY)
        sizerPostHoc = wx.BoxSizer(wx.VERTICAL)

        # Add "Post hoc Analysis" checkbox
        titlePostHocText = "Post hoc Analysis (all possible t-test)"
        titlePostHocText += " - only on ANOVA, not on ANCOVA"
        # TODO: check that field is disabled if there is a covariate
        self.PostHocCheckBox = wx.CheckBox(self, wx.ID_ANY, titlePostHocText)
        self.PostHocCheckBox.SetValue(self.PostHocCheck)

        # Parametric / Non-Parametric Test Section
        PanelParam = wx.Panel(self.PanelPostHoc, wx.ID_ANY)
        PanelNonParam = wx.Panel(PanelParam, wx.ID_ANY)

        self.RadioParamPostHoc = wx.RadioButton(
            PanelNonParam, wx.ID_ANY, 'Parametric Test', style=wx.RB_GROUP)
        self.RadioNonParamPostHoc = wx.RadioButton(
            PanelNonParam, self.RadioParamPostHoc.Id,
            'Non-Parametric Test (Bootstrapping)')

        # IterPostHocation Section
        self.PanelIterPostHoc = wx.Panel(PanelParam, wx.ID_ANY)
        TxtIterPostHoc = wx.StaticText(
            self.PanelIterPostHoc, wx.ID_ANY, label=" Iteration",
            style=wx.ALIGN_CENTER)
        self.IterInputPostHoc = wx.TextCtrl(
            self.PanelIterPostHoc, wx.ID_ANY, style=wx.TE_CENTRE,
            value=str(self.nIterationPostHoc))

        # Statistic (alpha, conseq pts, cluster size) Section
        PanelStatsPostHoc = wx.Panel(self.PanelPostHoc, wx.ID_ANY)
        PanelAlphaPostHoc = wx.Panel(PanelStatsPostHoc, wx.ID_ANY)
        TxtAlphaPostHoc = wx.StaticText(
            PanelAlphaPostHoc, wx.ID_ANY, label=" Alpha Value",
            style=wx.ALIGN_CENTER)
        self.AlphaInputPostHoc = wx.TextCtrl(
            PanelAlphaPostHoc, wx.ID_ANY, value=str(self.Alpha),
            style=wx.TE_CENTRE)

        PanelPtsConseqPostHoc = wx.Panel(PanelStatsPostHoc, wx.ID_ANY)
        PtsConseqTextPostHoc = wx.StaticText(
            PanelPtsConseqPostHoc, wx.ID_ANY, label="Consecutive Time Frames",
            style=wx.ALIGN_CENTER)
        self.PtsConseqInputPostHoc = wx.TextCtrl(
            PanelPtsConseqPostHoc, wx.ID_ANY, value=str(self.PtsConseqPostHoc),
            style=wx.TE_CENTRE)

        self.PanelClustPostHoc = wx.Panel(PanelStatsPostHoc, wx.ID_ANY)
        TxtClustPostHoc = wx.StaticText(
            self.PanelClustPostHoc, wx.ID_ANY,
            label="Cluster Size (Electrodes)", style=wx.ALIGN_CENTER)
        self.ClustInputPostHoc = wx.TextCtrl(
            self.PanelClustPostHoc, wx.ID_ANY, value=str(self.ClustPostHoc),
            style=wx.TE_CENTRE)

        # Create Structure of "Perform Post hoc Analysis"
        sizerNonParam = wx.BoxSizer(wx.VERTICAL)
        sizerNonParam.Add(self.RadioParamPostHoc, 0, wx.TOP)
        sizerNonParam.AddSpacer(2)
        sizerNonParam.Add(self.RadioNonParamPostHoc, 0, wx.TOP)
        PanelNonParam.SetSizer(sizerNonParam)

        sizerIterPostHoc = wx.BoxSizer(wx.VERTICAL)
        sizerIterPostHoc.Add(TxtIterPostHoc, 0, wx.EXPAND)
        sizerIterPostHoc.AddSpacer(2)
        sizerIterPostHoc.Add(self.IterInputPostHoc, 0, wx.EXPAND)
        self.PanelIterPostHoc.SetSizer(sizerIterPostHoc)

        sizerParam = wx.BoxSizer(wx.HORIZONTAL)
        sizerParam.Add(PanelNonParam, 0, wx.EXPAND)
        sizerParam.AddSpacer(10)
        sizerParam.Add(self.PanelIterPostHoc, 0, wx.EXPAND)
        PanelParam.SetSizer(sizerParam)

        sizerAlphaPostHoc = wx.BoxSizer(wx.VERTICAL)
        sizerAlphaPostHoc.Add(TxtAlphaPostHoc, 0, wx.EXPAND)
        sizerAlphaPostHoc.Add(self.AlphaInputPostHoc, 0, wx.EXPAND)
        PanelAlphaPostHoc.SetSizer(sizerAlphaPostHoc)

        sizerPtsConseqPostHoc = wx.BoxSizer(wx.VERTICAL)
        sizerPtsConseqPostHoc.Add(PtsConseqTextPostHoc, 0, wx.EXPAND)
        sizerPtsConseqPostHoc.Add(self.PtsConseqInputPostHoc, 0, wx.EXPAND)
        PanelPtsConseqPostHoc.SetSizer(sizerPtsConseqPostHoc)

        SizerPtsClustPostHoc = wx.BoxSizer(wx.VERTICAL)
        SizerPtsClustPostHoc.Add(TxtClustPostHoc, 0, wx.EXPAND)
        SizerPtsClustPostHoc.Add(self.ClustInputPostHoc, 0, wx.EXPAND)
        self.PanelClustPostHoc.SetSizer(SizerPtsClustPostHoc)

        sizerStats = wx.BoxSizer(wx.HORIZONTAL)
        sizerStats.Add(PanelAlphaPostHoc)
        sizerStats.AddSpacer(10)
        sizerStats.Add(PanelPtsConseqPostHoc)
        sizerStats.AddSpacer(10)
        sizerStats.Add(self.PanelClustPostHoc)
        sizerStats.AddSpacer(10)
        PanelStatsPostHoc.SetSizer(sizerStats)

        sizerPostHoc.Add(PanelParam, 0, wx.EXPAND)
        sizerPostHoc.AddSpacer(10)
        sizerPostHoc.Add(PanelStatsPostHoc, 0, wx.EXPAND)
        sizerPostHoc.AddSpacer(10)
        self.PanelPostHoc.SetSizer(sizerPostHoc)

        # Panel: Specify SPI
        self.PanelSPI = wx.Panel(self, wx.ID_ANY)

        TxtSPI = wx.StaticText(
            self.PanelSPI, wx.ID_ANY, label="Select XYZ File",
            style=wx.ALIGN_CENTER)
        self.FieldSPIFile = wx.TextCtrl(
            self.PanelSPI, wx.ID_ANY, value=self.SPIFile, style=wx.TE_READONLY)
        self.ButtonSPI = wx.Button(self.PanelSPI, wx.ID_ANY, label="Browse")
        sizerSPI = wx.GridBagSizer()
        sizerSPI.Add(TxtSPI, (0, 0), (1, 5), wx.EXPAND)
        sizerSPI.Add(self.FieldSPIFile, (1, 0), (1, 4), wx.EXPAND)
        sizerSPI.Add(self.ButtonSPI, (1, 5), (1, 1), wx.EXPAND)
        self.PanelSPI.SetSizer(sizerSPI)
        sizerSPI.AddGrowableCol(0)

        # Panel: Analyse Type (GFP, All electrodes or both)
        TxtAnalyse = wx.StaticText(
            self, wx.ID_ANY, label="Choose Analyse Type", style=wx.CENTRE)
        analyseTypes = ["All Electrodes", "GFP Only", "Both"]
        self.BoxAnalyse = wx.ComboBox(self, wx.ID_ANY, choices=analyseTypes,
                                      style=wx.CB_READONLY)
        self.BoxAnalyse.SetSelection(1)

        # Create structure of Analysis Frame
        sizerFrame = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizerFrame)
        sizerFrame.Add(self.AnovaCheckBox, 0, wx.EXPAND)
        sizerFrame.AddSpacer(5)
        sizerFrame.Add(self.PanelAnova, 0, wx.EXPAND)
        sizerFrame.AddSpacer(5)
        sizerFrame.Add(self.PostHocCheckBox, 0, wx.EXPAND)
        sizerFrame.AddSpacer(5)
        sizerFrame.Add(self.PanelPostHoc, 0, wx.EXPAND)
        sizerFrame.Add(self.PanelSPI, 0, wx.EXPAND)
        sizerFrame.AddSpacer(10)
        sizerFrame.Add(TxtAnalyse, 0, wx.EXPAND)
        sizerFrame.Add(self.BoxAnalyse, 0, wx.EXPAND)
        self.SetSizer(sizerFrame)

        # Inactive certain Sections
        self.PanelPostHoc.Disable()
        self.PanelClust.Disable()
        self.PanelClustPostHoc.Disable()
        self.PanelIter.Disable()
        self.PanelIterPostHoc.Disable()
        self.PanelSPI.Disable()

        # Events
        wx.EVT_CHECKBOX(self, self.AnovaCheckBox.Id, self.checkAnova)
        wx.EVT_RADIOBUTTON(self, self.RadioParam.Id, self.clickParam)
        wx.EVT_TEXT(self, self.AlphaInput.Id, self.chooseAlpha)
        wx.EVT_TEXT(self, self.PtsConseqInput.Id, self.choosePtsConseq)
        wx.EVT_TEXT(self, self.ClustInput.Id, self.chooseClust)
        wx.EVT_TEXT(self, self.IterInput.Id, self.chooseIter)

        wx.EVT_CHECKBOX(self, self.PostHocCheckBox.Id, self.checkPostHoc)
        wx.EVT_RADIOBUTTON(self, self.RadioParamPostHoc.Id,
                           self.clickParamPostHoc)
        wx.EVT_TEXT(self, self.AlphaInputPostHoc.Id, self.chooseAlphaPostHoc)
        wx.EVT_TEXT(self, self.PtsConseqInputPostHoc.Id,
                    self.choosePtsConseqPostHoc)
        wx.EVT_TEXT(self, self.ClustInputPostHoc.Id, self.chooseClustPostHoc)
        wx.EVT_TEXT(self, self.IterInputPostHoc.Id, self.chooseIterPostHoc)
        wx.EVT_COMBOBOX(self, self.BoxAnalyse.Id, self.AnalyseChoose)

        wx.EVT_BUTTON(self, self.ButtonSPI.Id, self.chooseSPI)

    def checkAnova(self, event):
        self.AnovaCheck = self.AnovaCheckBox.GetValue()
        if self.AnovaCheck:
            self.PanelAnova.Enable()
        else:
            self.PanelAnova.Disable()
        event.Skip()

    def checkPostHoc(self, event):
        self.PostHocCheck = self.PostHocCheckBox.GetValue()
        if self.PostHocCheck:
            self.PanelPostHoc.Enable()
            self.AnalyseType = self.BoxAnalyse.GetValue()
            if self.AnalyseType == 'GFP Only':
                self.PanelClustPostHoc.Disable()
            else:
                self.PanelClustPostHoc.Enable()

            if self.ParamPostHoc:
                self.PanelIterPostHoc.Disable()
            else:
                self.PanelIterPostHoc.Enable()
        else:
            self.PanelPostHoc.Disable()
        event.Skip()

    def clickParam(self, event):
        self.Param = self.RadioParam.GetValue()
        if self.Param:
            self.PanelIter.Disable()
        else:
            self.PanelIter.Enable()
        event.Skip()

    def clickParamPostHoc(self, event):
        self.ParamPostHoc = self.RadioParamPostHoc.GetValue()
        if self.ParamPostHoc:
            self.PanelIterPostHoc.Disable()
        else:
            self.PanelIterPostHoc.Enable()
        event.Skip()

    def messageNotInteger(self, inputStr):
        dlg = wx.MessageDialog(
            self, "'%s' is not a positive Integer" % inputStr, style=wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def messageNotAlpha(self, inputStr):
        dlg = wx.MessageDialog(
            self, "'%s' is not a float between 0 and 1" % inputStr,
            style=wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def chooseIter(self, event):
        inputStr = self.IterInput.GetValue()
        inputIsOK = inputStr.isdigit()
        if inputIsOK and int(inputStr) != 0:
            self.nIteration = int(inputStr)
            self.IterInputPostHoc.SetValue(str(self.nIteration))
        elif inputStr != '':
            self.messageNotInteger(inputStr)
            self.IterInput.SetValue(str(self.nIteration))
        event.Skip()

    def chooseIterPostHoc(self, event):
        # TODO: do the values have to be the same for normal and posthoc?
        inputStr = self.IterInputPostHoc.GetValue()
        inputIsOK = inputStr.isdigit()
        if inputIsOK and int(inputStr) != 0:
            self.nIterationPostHoc = int(inputStr)
        elif inputStr != '':
            self.messageNotInteger(inputStr)
            self.IterInputPostHoc.SetValue(str(self.nIterationPostHoc))
        event.Skip()

    def checkAlpha(self, inputStr):
        alphaOK = inputStr.replace('.', '', 1).isdigit()
        if alphaOK:
            alpha = float(inputStr)
            if alpha > 0 and alpha < 1:
                alphaOK = True
            else:
                alphaOK = False
        return alphaOK

    def chooseAlpha(self, event):
        inputStr = self.AlphaInput.GetValue()
        inputIsOK = self.checkAlpha(inputStr)
        if inputIsOK:
            self.Alpha = float(inputStr)
            self.AlphaInputPostHoc.SetValue(inputStr)
        elif inputStr not in ['', '.', '0', '0.', '0.0', '.0', '0.00', '.00',
                              '0.000', '.000', '0.0000', '.0000', '0.00000',
                              '.00000']:
            self.messageNotAlpha(inputStr)
            self.AlphaInput.SetValue(str(self.Alpha))
        event.Skip()

    def chooseAlphaPostHoc(self, event):
        # TODO: do the values have to be the same for normal and posthoc?
        inputStr = self.AlphaInputPostHoc.GetValue()
        inputIsOK = self.checkAlpha(inputStr)
        if inputIsOK:
            self.AlphaPostHoc = float(inputStr)
        elif inputStr not in ['', '.', '0', '0.', '0.0', '.0', '0.00', '.00',
                              '0.000', '.000', '0.0000', '.0000', '0.00000',
                              '.00000']:
            self.messageNotAlpha(inputStr)
            if 'e-' in str(self.AlphaPostHoc):
                output = '%.16f' % self.AlphaPostHoc
                self.AlphaInputPostHoc.SetValue(output.rstrip('0'))
            else:
                self.AlphaInputPostHoc.SetValue(str(self.AlphaPostHoc))
        event.Skip()

    def choosePtsConseq(self, event):
        inputStr = self.PtsConseqInput.GetValue()
        inputIsOK = inputStr.isdigit()
        if inputIsOK and int(inputStr) != 0:
            self.PtsConseq = int(inputStr)
            self.PtsConseqInputPostHoc.SetValue(str(self.PtsConseq))
        elif inputStr != '':
            self.messageNotInteger(inputStr)
            self.PtsConseqInput.SetValue(str(self.PtsConseq))
        event.Skip()

    def choosePtsConseqPostHoc(self, event):
        # TODO: do the values have to be the same for normal and posthoc?
        inputStr = self.PtsConseqInputPostHoc.GetValue()
        inputIsOK = inputStr.isdigit()
        if inputIsOK and int(inputStr) != 0:
            self.PtsConseqPostHoc = int(inputStr)
        elif inputStr != '':
            self.messageNotInteger(inputStr)
            self.PtsConseqInputPostHoc.SetValue(str(self.PtsConseqPostHoc))
        event.Skip()

    def chooseClust(self, event):
        inputStr = self.ClustInput.GetValue()
        inputIsOK = inputStr.isdigit()
        if inputIsOK and int(inputStr) != 0:
            self.Clust = int(inputStr)
            self.ClustInputPostHoc.SetValue(str(self.Clust))
            if self.Clust != 1:
                self.PanelSPI.Enable()
                if self.SPIFile == '':
                    self.Mainframe.ButtonStart.Disable()
            else:
                self.PanelSPI.Disable()
                self.Mainframe.ButtonStart.Enable()
        elif inputStr != '':
            self.messageNotInteger(inputStr)
            self.ClustInput.SetValue(str(self.Clust))
        event.Skip()

    def chooseClustPostHoc(self, event):
        # TODO: do the values have to be the same for normal and posthoc?
        inputStr = self.ClustInputPostHoc.GetValue()
        inputIsOK = inputStr.isdigit()
        if inputIsOK and int(inputStr) != 0:
            self.ClustPostHoc = int(inputStr)
            if self.ClustPostHoc != 1:
                self.PanelSPI.Enable()
                if self.SPIFile == '':
                    self.Mainframe.ButtonStart.Disable()
            else:
                self.PanelSPI.Disable()
                self.Mainframe.ButtonStart.Enable()
        elif inputStr != '':
            self.messageNotInteger(inputStr)
            self.ClustInputPostHoc.SetValue(str(self.ClustPostHoc))
        event.Skip()

    def chooseSPI(self, event):
        dlgXYZ = wx.FileDialog(None, "Load xyz file",
                               defaultDir=self.SPIPath,
                               wildcard='*.xyz',
                               style=wx.OPEN)
        if dlgXYZ.ShowModal() == wx.ID_OK:
            self.SPIFile = dlgXYZ.GetPath()
            self.FieldSPIFile.SetValue(self.SPIFile)
            self.SPIPath = dirname(self.SPIFile)
            self.Mainframe.ButtonStart.Enable()
        dlgXYZ.Destroy()
        event.Skip()

    def AnalyseChoose(self, event):
        self.AnalyseType = self.BoxAnalyse.GetValue()
        if self.AnalyseType != 'GFP Only':
            self.PanelClust.Enable()
            self.PanelClustPostHoc.Enable()
        else:
            self.PanelClust.Disable()
            self.PanelClustPostHoc.Disable()


class AnovaIS(wx.Panel):

    """TODO: EXPLANATION TEXT"""

    def __init__(self, notebook, Mainframe):
        wx.Panel.__init__(self, parent=notebook)

        # Specify relevant variables
        self.Mainframe = Mainframe
        self.AnovaCheck = True
        self.PostHocCheck = False
        self.Param = True
        self.ParamPostHoc = True
        self.nIteration = 1000
        self.nIterationPostHoc = 1000
        self.Alpha = 0.05
        self.AlphaPostHoc = 0.05
        self.PtsConseq = 1
        self.PtsConseqPostHoc = 1
        self.Clust = 1
        self.ClustPostHoc = 1
        self.SPIFile = ''
        self.SPIPath = ''

        # Panel: Perform ANOVA
        self.PanelAnova = wx.Panel(self, wx.ID_ANY)
        sizerAnova = wx.BoxSizer(wx.VERTICAL)

        # Add "Perform ANOVA" checkbox
        self.AnovaCheckBox = wx.CheckBox(self, wx.ID_ANY, "Perform ANOVA")
        self.AnovaCheckBox.SetValue(self.AnovaCheck)

        # Parametric / Non-Parametric Test Section
        PanelParam = wx.Panel(self.PanelAnova, wx.ID_ANY)
        PanelNonParam = wx.Panel(PanelParam, wx.ID_ANY)

        self.RadioParam = wx.RadioButton(
            PanelNonParam, wx.ID_ANY, 'Parametric Test', style=wx.RB_GROUP)
        self.RadioNonParam = wx.RadioButton(
            PanelNonParam, self.RadioParam.Id,
            'Non-Parametric Test (Bootstrapping)')

        # Iteration Section
        self.PanelIter = wx.Panel(PanelParam, wx.ID_ANY)
        TxtIter = wx.StaticText(self.PanelIter, wx.ID_ANY, label=" Iteration",
                                style=wx.ALIGN_CENTER)
        self.IterInput = wx.TextCtrl(
            self.PanelIter, wx.ID_ANY, value=str(self.nIteration),
            style=wx.TE_CENTRE)

        # Statistic (alpha, conseq pts, cluster size) Section
        PanelStats = wx.Panel(self.PanelAnova, wx.ID_ANY)
        PanelAlpha = wx.Panel(PanelStats, wx.ID_ANY)
        TxtAlpha = wx.StaticText(PanelAlpha, wx.ID_ANY, label=" Alpha Value",
                                 style=wx.ALIGN_CENTER)
        self.AlphaInput = wx.TextCtrl(
            PanelAlpha, wx.ID_ANY, value=str(self.Alpha), style=wx.TE_CENTRE)

        PanelPtsConseq = wx.Panel(PanelStats, wx.ID_ANY)
        PtsConseqText = wx.StaticText(
            PanelPtsConseq, wx.ID_ANY, label="Consecutive Time Frames",
            style=wx.ALIGN_CENTER)
        self.PtsConseqInput = wx.TextCtrl(
            PanelPtsConseq, wx.ID_ANY, value=str(self.PtsConseq),
            style=wx.TE_CENTRE)

        self.PanelClust = wx.Panel(PanelStats, wx.ID_ANY)
        TxtClust = wx.StaticText(
            self.PanelClust, wx.ID_ANY, label="Cluster Size (Voxels)",
            style=wx.ALIGN_CENTER)
        self.ClustInput = wx.TextCtrl(
            self.PanelClust, wx.ID_ANY, value=str(self.Clust),
            style=wx.TE_CENTRE)

        # Create Structure of "Perform ANOVA"
        sizerNonParam = wx.BoxSizer(wx.VERTICAL)
        sizerNonParam.Add(self.RadioParam, 0, wx.TOP)
        sizerNonParam.AddSpacer(2)
        sizerNonParam.Add(self.RadioNonParam, 0, wx.TOP)
        PanelNonParam.SetSizer(sizerNonParam)

        sizerIter = wx.BoxSizer(wx.VERTICAL)
        sizerIter.Add(TxtIter, 0, wx.EXPAND)
        sizerIter.AddSpacer(2)
        sizerIter.Add(self.IterInput, 0, wx.EXPAND)
        self.PanelIter.SetSizer(sizerIter)

        sizerParam = wx.BoxSizer(wx.HORIZONTAL)
        sizerParam.Add(PanelNonParam, 0, wx.EXPAND)
        sizerParam.AddSpacer(10)
        sizerParam.Add(self.PanelIter, 0, wx.EXPAND)
        PanelParam.SetSizer(sizerParam)

        sizerAlpha = wx.BoxSizer(wx.VERTICAL)
        sizerAlpha.Add(TxtAlpha, 0, wx.EXPAND)
        sizerAlpha.Add(self.AlphaInput, 0, wx.EXPAND)
        PanelAlpha.SetSizer(sizerAlpha)

        sizerPtsConseq = wx.BoxSizer(wx.VERTICAL)
        sizerPtsConseq.Add(PtsConseqText, 0, wx.EXPAND)
        sizerPtsConseq.Add(self.PtsConseqInput, 0, wx.EXPAND)
        PanelPtsConseq.SetSizer(sizerPtsConseq)

        SizerPtsClust = wx.BoxSizer(wx.VERTICAL)
        SizerPtsClust.Add(TxtClust, 0, wx.EXPAND)
        SizerPtsClust.Add(self.ClustInput, 0, wx.EXPAND)
        self.PanelClust.SetSizer(SizerPtsClust)

        sizerStats = wx.BoxSizer(wx.HORIZONTAL)
        sizerStats.Add(PanelAlpha)
        sizerStats.AddSpacer(10)
        sizerStats.Add(PanelPtsConseq)
        sizerStats.AddSpacer(10)
        sizerStats.Add(self.PanelClust)
        sizerStats.AddSpacer(10)
        PanelStats.SetSizer(sizerStats)

        sizerAnova.Add(PanelParam, 0, wx.EXPAND)
        sizerAnova.AddSpacer(10)
        sizerAnova.Add(PanelStats, 0, wx.EXPAND)
        sizerAnova.AddSpacer(10)
        self.PanelAnova.SetSizer(sizerAnova)

        # Panel: Perform Post hoc Analysis
        self.PanelPostHoc = wx.Panel(self, wx.ID_ANY)
        sizerPostHoc = wx.BoxSizer(wx.VERTICAL)

        # Add "Post hoc Analysis" checkbox
        titlePostHocText = "Post hoc Analysis (all possible t-test)"
        titlePostHocText += " - only on ANOVA, not on ANCOVA"
        # TODO: check that field is disabled if there is a covariate
        self.PostHocCheckBox = wx.CheckBox(self, wx.ID_ANY, titlePostHocText)
        self.PostHocCheckBox.SetValue(self.PostHocCheck)

        # Parametric / Non-Parametric Test Section
        PanelParam = wx.Panel(self.PanelPostHoc, wx.ID_ANY)
        PanelNonParam = wx.Panel(PanelParam, wx.ID_ANY)

        self.RadioParamPostHoc = wx.RadioButton(
            PanelNonParam, wx.ID_ANY, 'Parametric Test', style=wx.RB_GROUP)
        self.RadioNonParamPostHoc = wx.RadioButton(
            PanelNonParam, self.RadioParamPostHoc.Id,
            'Non-Parametric Test (Bootstrapping)')

        # IterPostHocation Section
        self.PanelIterPostHoc = wx.Panel(PanelParam, wx.ID_ANY)
        TxtIterPostHoc = wx.StaticText(
            self.PanelIterPostHoc, wx.ID_ANY, label=" Iteration",
            style=wx.ALIGN_CENTER)
        self.IterInputPostHoc = wx.TextCtrl(
            self.PanelIterPostHoc, wx.ID_ANY, style=wx.TE_CENTRE,
            value=str(self.nIterationPostHoc))

        # Statistic (alpha, conseq pts, cluster size) Section
        PanelStatsPostHoc = wx.Panel(self.PanelPostHoc, wx.ID_ANY)
        PanelAlphaPostHoc = wx.Panel(PanelStatsPostHoc, wx.ID_ANY)
        TxtAlphaPostHoc = wx.StaticText(
            PanelAlphaPostHoc, wx.ID_ANY, label=" Alpha Value",
            style=wx.ALIGN_CENTER)
        self.AlphaInputPostHoc = wx.TextCtrl(
            PanelAlphaPostHoc, wx.ID_ANY, value=str(self.Alpha),
            style=wx.TE_CENTRE)

        PanelPtsConseqPostHoc = wx.Panel(PanelStatsPostHoc, wx.ID_ANY)
        PtsConseqTextPostHoc = wx.StaticText(
            PanelPtsConseqPostHoc, wx.ID_ANY, label="Consecutive Time Frames",
            style=wx.ALIGN_CENTER)
        self.PtsConseqInputPostHoc = wx.TextCtrl(
            PanelPtsConseqPostHoc, wx.ID_ANY, value=str(self.PtsConseqPostHoc),
            style=wx.TE_CENTRE)

        self.PanelClustPostHoc = wx.Panel(PanelStatsPostHoc, wx.ID_ANY)
        TxtClustPostHoc = wx.StaticText(
            self.PanelClustPostHoc, wx.ID_ANY,
            label="Cluster Size (Voxels)", style=wx.ALIGN_CENTER)
        self.ClustInputPostHoc = wx.TextCtrl(
            self.PanelClustPostHoc, wx.ID_ANY, value=str(self.ClustPostHoc),
            style=wx.TE_CENTRE)

        # Create Structure of "Perform Post hoc Analysis"
        sizerNonParam = wx.BoxSizer(wx.VERTICAL)
        sizerNonParam.Add(self.RadioParamPostHoc, 0, wx.TOP)
        sizerNonParam.AddSpacer(2)
        sizerNonParam.Add(self.RadioNonParamPostHoc, 0, wx.TOP)
        PanelNonParam.SetSizer(sizerNonParam)

        sizerIterPostHoc = wx.BoxSizer(wx.VERTICAL)
        sizerIterPostHoc.Add(TxtIterPostHoc, 0, wx.EXPAND)
        sizerIterPostHoc.AddSpacer(2)
        sizerIterPostHoc.Add(self.IterInputPostHoc, 0, wx.EXPAND)
        self.PanelIterPostHoc.SetSizer(sizerIterPostHoc)

        sizerParam = wx.BoxSizer(wx.HORIZONTAL)
        sizerParam.Add(PanelNonParam, 0, wx.EXPAND)
        sizerParam.AddSpacer(10)
        sizerParam.Add(self.PanelIterPostHoc, 0, wx.EXPAND)
        PanelParam.SetSizer(sizerParam)

        sizerAlphaPostHoc = wx.BoxSizer(wx.VERTICAL)
        sizerAlphaPostHoc.Add(TxtAlphaPostHoc, 0, wx.EXPAND)
        sizerAlphaPostHoc.Add(self.AlphaInputPostHoc, 0, wx.EXPAND)
        PanelAlphaPostHoc.SetSizer(sizerAlphaPostHoc)

        sizerPtsConseqPostHoc = wx.BoxSizer(wx.VERTICAL)
        sizerPtsConseqPostHoc.Add(PtsConseqTextPostHoc, 0, wx.EXPAND)
        sizerPtsConseqPostHoc.Add(self.PtsConseqInputPostHoc, 0, wx.EXPAND)
        PanelPtsConseqPostHoc.SetSizer(sizerPtsConseqPostHoc)

        SizerPtsClustPostHoc = wx.BoxSizer(wx.VERTICAL)
        SizerPtsClustPostHoc.Add(TxtClustPostHoc, 0, wx.EXPAND)
        SizerPtsClustPostHoc.Add(self.ClustInputPostHoc, 0, wx.EXPAND)
        self.PanelClustPostHoc.SetSizer(SizerPtsClustPostHoc)

        sizerStats = wx.BoxSizer(wx.HORIZONTAL)
        sizerStats.Add(PanelAlphaPostHoc)
        sizerStats.AddSpacer(10)
        sizerStats.Add(PanelPtsConseqPostHoc)
        sizerStats.AddSpacer(10)
        sizerStats.Add(self.PanelClustPostHoc)
        sizerStats.AddSpacer(10)
        PanelStatsPostHoc.SetSizer(sizerStats)

        sizerPostHoc.Add(PanelParam, 0, wx.EXPAND)
        sizerPostHoc.AddSpacer(10)
        sizerPostHoc.Add(PanelStatsPostHoc, 0, wx.EXPAND)
        sizerPostHoc.AddSpacer(10)
        self.PanelPostHoc.SetSizer(sizerPostHoc)

        # Panel: Specify SPI
        self.PanelSPI = wx.Panel(self, wx.ID_ANY)

        TxtSPI = wx.StaticText(
            self.PanelSPI, wx.ID_ANY, label="Select SPI File",
            style=wx.ALIGN_CENTER)
        self.FieldSPIFile = wx.TextCtrl(
            self.PanelSPI, wx.ID_ANY, value=self.SPIFile, style=wx.TE_READONLY)
        self.ButtonSPI = wx.Button(self.PanelSPI, wx.ID_ANY, label="Browse")
        sizerSPI = wx.GridBagSizer()
        sizerSPI.Add(TxtSPI, (0, 0), (1, 5), wx.EXPAND)
        sizerSPI.Add(self.FieldSPIFile, (1, 0), (1, 4), wx.EXPAND)
        sizerSPI.Add(self.ButtonSPI, (1, 5), (1, 1), wx.EXPAND)
        self.PanelSPI.SetSizer(sizerSPI)
        sizerSPI.AddGrowableCol(0)

        # Create structure of Analysis Frame
        sizerFrame = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizerFrame)
        sizerFrame.Add(self.AnovaCheckBox, 0, wx.EXPAND)
        sizerFrame.AddSpacer(5)
        sizerFrame.Add(self.PanelAnova, 0, wx.EXPAND)
        sizerFrame.AddSpacer(5)
        sizerFrame.Add(self.PostHocCheckBox, 0, wx.EXPAND)
        sizerFrame.AddSpacer(5)
        sizerFrame.Add(self.PanelPostHoc, 0, wx.EXPAND)
        sizerFrame.Add(self.PanelSPI, 0, wx.EXPAND)
        self.SetSizer(sizerFrame)

        # Inactive certain Sections
        self.PanelPostHoc.Disable()
        self.PanelIter.Disable()
        self.PanelIterPostHoc.Disable()
        self.PanelSPI.Disable()

        # Events
        wx.EVT_CHECKBOX(self, self.AnovaCheckBox.Id, self.checkAnova)
        wx.EVT_RADIOBUTTON(self, self.RadioParam.Id, self.clickParam)
        wx.EVT_TEXT(self, self.AlphaInput.Id, self.chooseAlpha)
        wx.EVT_TEXT(self, self.PtsConseqInput.Id, self.choosePtsConseq)
        wx.EVT_TEXT(self, self.ClustInput.Id, self.chooseClust)
        wx.EVT_TEXT(self, self.IterInput.Id, self.chooseIter)

        wx.EVT_CHECKBOX(self, self.PostHocCheckBox.Id, self.checkPostHoc)
        wx.EVT_RADIOBUTTON(self, self.RadioParamPostHoc.Id,
                           self.clickParamPostHoc)
        wx.EVT_TEXT(self, self.AlphaInputPostHoc.Id, self.chooseAlphaPostHoc)
        wx.EVT_TEXT(self, self.PtsConseqInputPostHoc.Id,
                    self.choosePtsConseqPostHoc)
        wx.EVT_TEXT(self, self.ClustInputPostHoc.Id, self.chooseClustPostHoc)
        wx.EVT_TEXT(self, self.IterInputPostHoc.Id, self.chooseIterPostHoc)

        wx.EVT_BUTTON(self, self.ButtonSPI.Id, self.chooseSPI)

    def checkAnova(self, event):
        self.AnovaCheck = self.AnovaCheckBox.GetValue()
        if self.AnovaCheck:
            self.PanelAnova.Enable()
        else:
            self.PanelAnova.Disable()
        event.Skip()

    def checkPostHoc(self, event):
        self.PostHocCheck = self.PostHocCheckBox.GetValue()
        if self.PostHocCheck:
            self.PanelPostHoc.Enable()
            if self.ParamPostHoc:
                self.PanelIterPostHoc.Disable()
            else:
                self.PanelIterPostHoc.Enable()
        else:
            self.PanelPostHoc.Disable()
        event.Skip()

    def clickParam(self, event):
        self.Param = self.RadioParam.GetValue()
        if self.Param:
            self.PanelIter.Disable()
        else:
            self.PanelIter.Enable()
        event.Skip()

    def clickParamPostHoc(self, event):
        self.ParamPostHoc = self.RadioParamPostHoc.GetValue()
        if self.ParamPostHoc:
            self.PanelIterPostHoc.Disable()
        else:
            self.PanelIterPostHoc.Enable()
        event.Skip()

    def messageNotInteger(self, inputStr):
        dlg = wx.MessageDialog(
            self, "'%s' is not a positive Integer" % inputStr, style=wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def messageNotAlpha(self, inputStr):
        dlg = wx.MessageDialog(
            self, "'%s' is not a float between 0 and 1" % inputStr,
            style=wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def chooseIter(self, event):
        inputStr = self.IterInput.GetValue()
        inputIsOK = inputStr.isdigit()
        if inputIsOK and int(inputStr) != 0:
            self.nIteration = int(inputStr)
            self.IterInputPostHoc.SetValue(str(self.nIteration))
        elif inputStr != '':
            self.messageNotInteger(inputStr)
            self.IterInput.SetValue(str(self.nIteration))
        event.Skip()

    def chooseIterPostHoc(self, event):
        # TODO: do the values have to be the same for normal and posthoc?
        inputStr = self.IterInputPostHoc.GetValue()
        inputIsOK = inputStr.isdigit()
        if inputIsOK and int(inputStr) != 0:
            self.nIterationPostHoc = int(inputStr)
        elif inputStr != '':
            self.messageNotInteger(inputStr)
            self.IterInputPostHoc.SetValue(str(self.nIterationPostHoc))
        event.Skip()

    def checkAlpha(self, inputStr):
        alphaOK = inputStr.replace('.', '', 1).isdigit()
        if alphaOK:
            alpha = float(inputStr)
            if alpha > 0 and alpha < 1:
                alphaOK = True
            else:
                alphaOK = False
        return alphaOK

    def chooseAlpha(self, event):
        inputStr = self.AlphaInput.GetValue()
        inputIsOK = self.checkAlpha(inputStr)
        if inputIsOK:
            self.Alpha = float(inputStr)
            self.AlphaInputPostHoc.SetValue(inputStr)
        elif inputStr not in ['', '.', '0', '0.', '0.0', '.0', '0.00', '.00',
                              '0.000', '.000', '0.0000', '.0000', '0.00000',
                              '.00000']:
            self.messageNotAlpha(inputStr)
            self.AlphaInput.SetValue(str(self.Alpha))
        event.Skip()

    def chooseAlphaPostHoc(self, event):
        # TODO: do the values have to be the same for normal and posthoc?
        inputStr = self.AlphaInputPostHoc.GetValue()
        inputIsOK = self.checkAlpha(inputStr)
        if inputIsOK:
            self.AlphaPostHoc = float(inputStr)
        elif inputStr not in ['', '.', '0', '0.', '0.0', '.0', '0.00', '.00',
                              '0.000', '.000', '0.0000', '.0000', '0.00000',
                              '.00000']:
            self.messageNotAlpha(inputStr)
            if 'e-' in str(self.AlphaPostHoc):
                output = '%.16f' % self.AlphaPostHoc
                self.AlphaInputPostHoc.SetValue(output.rstrip('0'))
            else:
                self.AlphaInputPostHoc.SetValue(str(self.AlphaPostHoc))
        event.Skip()

    def choosePtsConseq(self, event):
        inputStr = self.PtsConseqInput.GetValue()
        inputIsOK = inputStr.isdigit()
        if inputIsOK and int(inputStr) != 0:
            self.PtsConseq = int(inputStr)
            self.PtsConseqInputPostHoc.SetValue(str(self.PtsConseq))
        elif inputStr != '':
            self.messageNotInteger(inputStr)
            self.PtsConseqInput.SetValue(str(self.PtsConseq))
        event.Skip()

    def choosePtsConseqPostHoc(self, event):
        # TODO: do the values have to be the same for normal and posthoc?
        inputStr = self.PtsConseqInputPostHoc.GetValue()
        inputIsOK = inputStr.isdigit()
        if inputIsOK and int(inputStr) != 0:
            self.PtsConseqPostHoc = int(inputStr)
        elif inputStr != '':
            self.messageNotInteger(inputStr)
            self.PtsConseqInputPostHoc.SetValue(str(self.PtsConseqPostHoc))
        event.Skip()

    def chooseClust(self, event):
        inputStr = self.ClustInput.GetValue()
        inputIsOK = inputStr.isdigit()
        if inputIsOK and int(inputStr) != 0:
            self.Clust = int(inputStr)
            self.ClustInputPostHoc.SetValue(str(self.Clust))
            if self.Clust != 1:
                self.PanelSPI.Enable()
                if self.SPIFile == '':
                    self.Mainframe.ButtonStart.Disable()
            else:
                self.PanelSPI.Disable()
                self.Mainframe.ButtonStart.Enable()
        elif inputStr != '':
            self.messageNotInteger(inputStr)
            self.ClustInput.SetValue(str(self.Clust))
        event.Skip()

    def chooseClustPostHoc(self, event):
        # TODO: do the values have to be the same for normal and posthoc?
        inputStr = self.ClustInputPostHoc.GetValue()
        inputIsOK = inputStr.isdigit()
        if inputIsOK and int(inputStr) != 0:
            self.ClustPostHoc = int(inputStr)
            if self.ClustPostHoc != 1:
                self.PanelSPI.Enable()
                if self.SPIFile == '':
                    self.Mainframe.ButtonStart.Disable()
            else:
                self.PanelSPI.Disable()
                self.Mainframe.ButtonStart.Enable()
        elif inputStr != '':
            self.messageNotInteger(inputStr)
            self.ClustInputPostHoc.SetValue(str(self.ClustPostHoc))
        event.Skip()

    def chooseSPI(self, event):
        dlgSPI = wx.FileDialog(None, "Load spi file",
                               defaultDir=self.SPIPath,
                               wildcard='*.spi',
                               style=wx.OPEN)
        if dlgSPI.ShowModal() == wx.ID_OK:
            self.SPIFile = dlgSPI.GetPath()
            self.FieldSPIFile.SetValue(self.SPIFile)
            self.SPIPath = dirname(self.SPIFile)
            self.Mainframe.ButtonStart.Enable()
        dlgSPI.Destroy()
        event.Skip()
