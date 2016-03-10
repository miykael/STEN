import wx
import numpy as np
from CalculSheet import CalculSheetCov


class CovariateDefinition(wx.Dialog):

    def __init__(self, Within, Between, Subject, Covariate,
                 NameWithin, NameBetween, NameCovariate):
        wx.Dialog.__init__(
            self, None, wx.ID_ANY, title="Covariate Definition", size=(1000, 500))
        self.MakeModal(True)
        FrameSizer = wx.BoxSizer(wx.VERTICAL)
        # load panel
        self.Correction = []
        PanelSheet = wx.Panel(self, wx.ID_ANY)
        SheetSizer = wx.BoxSizer(wx.VERTICAL)
        self.Sheet = CalculSheetCov(PanelSheet)
        SheetSizer.Add(self.Sheet, 0, wx.EXPAND)
        PanelSheet.SetSizer(SheetSizer)
        FrameSizer.Add(PanelSheet, 0, wx.EXPAND)
        FrameSizer.AddSpacer(10)

        ModifPanel = wx.Panel(self, wx.ID_ANY)
        ModifiySizer = wx.BoxSizer(wx.HORIZONTAL)
        ButtonCancel = wx.Button(ModifPanel, 1, label="Cancel", size=(108, 23))
        ModifiySizer.Add(ButtonCancel, 0, wx.EXPAND)
        Buttonok = wx.Button(ModifPanel, 2, label="OK", size=(108, 23))
        ModifiySizer.Add(Buttonok, 0, wx.EXPAND)
        ModifPanel.SetSizerAndFit(ModifiySizer)
        FrameSizer.Add(ModifPanel, 0, wx.EXPAND)
        self.SetSizerAndFit(FrameSizer)

        wx.EVT_BUTTON(self, 1, self.Cancel)
        wx.EVT_BUTTON(self, 2, self.OK)
        self.Show(True)
        # subject
        row = 0
        NbRow = len(Subject)
        NbCol = 1

        if len(Within.shape) != 1:
            NbCol += Within.shape[1]
        else:
            NbCol += 1

        if len(Covariate.shape) != 1:
            NbCol += Covariate.shape[1]
        else:
            NbCol += 1

        try:
            if len(Between.shape) != 1:
                NbCol += Between.shape[1]
            else:
                NbCol += 1
        except:
            pass

        self.Sheet.SetNumberRows(NbRow)
        self.Sheet.SetNumberCols(NbCol)
        for s in Subject:
            value = str(int(s))
            self.Sheet.SetCellValue(row, 0, value)
            row += 1
        col = 1
        ColDisable = [0]
        # Within
        if NameWithin:
            for i, n in enumerate(NameWithin):
                self.Sheet.SetColLabelValue(col, n)
                if len(Within.shape) != 1:
                    ColValues = Within[:, i]
                else:
                    ColValues = Within
                row = 0
                for v in ColValues:
                    value = str(int(v))
                    self.Sheet.SetCellValue(row, col, value)
                    row += 1
                ColDisable.append(col)
                col += 1

        # Between
        if NameBetween:
            for i, n in enumerate(NameBetween):
                self.Sheet.SetColLabelValue(col, n)
                if len(Between.shape) != 1:
                    ColValues = Between[:, i]
                else:
                    ColValues = Between
                row = 0
                for v in ColValues:
                    value = str(int(v))
                    self.Sheet.SetCellValue(row, col, value)
                    row += 1
                ColDisable.append(col)
                col += 1
        self.ColCov = []
        # Covariate
        if NameCovariate:
            for i, n in enumerate(NameCovariate):
                self.Sheet.SetColLabelValue(col, n)
                if len(Covariate.shape) != 1:
                    ColValues = Covariate[:, i]
                else:
                    ColValues = Covariate
                row = 0
                for v in ColValues:
                    value = str(float(v))
                    self.Sheet.SetCellValue(row, col, value)
                    row += 1
                self.ColCov.append(col)
                col += 1
        self.NbRow = NbRow
        self.Sheet.Bind(wx.EVT_CHAR, self.OnKeyPress)
        self.Sheet.DisableCellEditControl
        self.ShowModal()

    def OK(self, event):
        NewModelCov = np.zeros((self.NbRow, len(self.ColCov)))
        for i, c in enumerate(self.ColCov):
            for r in range(self.NbRow):
                cell = self.Sheet.GetCellValue(r, c)
                NewModelCov[r, i] = float(cell)
        self.Covariate = NewModelCov
        self.Correction = True
        self.MakeModal(False)
        self.Close()

    def Cancel(self, event):
        self.Correction = False
        self.MakeModal(False)
        self.Close()

    def OnKeyPress(self, event):
        if event.GetKeyCode() == 3:
            self.Sheet.Copy()
        elif event.GetKeyCode() == 22:
            self.Sheet.Paste()
        else:

            event.Skip()
