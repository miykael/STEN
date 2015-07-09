import wx
from FactorDefinition import FactorDef


class FactorWithin(wx.Frame):

    """ TODO: translate to english
    définition des facteur Within stype SPSS"""

    def __init__(self, NoEmptyCol, Sheet, Parent, Level, Factor):
        wx.Frame.__init__(
            self, None, -1, title="Within subject definition", size=(200, 250))
        FrameSizer = wx.BoxSizer(wx.VERTICAL)
        self.Level = Level
        self.Factor = Factor
        self.NoEmptyCol = NoEmptyCol
        self.Sheet = Sheet
        self.ColWithin = []
        self.ColBetween = []
        self.ColSubject = []
        self.ColCovariate = []
        self.TabValue = Parent.Data.Value
        self.DataEntry = Parent

        # panel Factor
        PanelFactor = wx.Panel(self, -1)
        FactorSizer = wx.BoxSizer(wx.VERTICAL)
        TextNameFactor = wx.StaticText(
            PanelFactor, -1, label="   Within Subject Factor Name : ")
        FactorSizer.Add(TextNameFactor, 0, wx.ALIGN_LEFT)
        self.FactorName = wx.TextCtrl(PanelFactor, 1, value="")
        FactorSizer.Add(self.FactorName, 0, wx.ALIGN_RIGHT)

        TextNbLevel = wx.StaticText(
            PanelFactor, -1, label="   Number of Levels : ")
        FactorSizer.Add(TextNbLevel, 0, wx.ALIGN_LEFT)
        self.LevelNb = wx.TextCtrl(PanelFactor, 1, value="")
        FactorSizer.Add(self.LevelNb, 0, wx.ALIGN_RIGHT)
        PanelFactor.SetSizerAndFit(FactorSizer)
        FrameSizer.Add(PanelFactor, 0, wx.EXPAND)
        FrameSizer.AddStretchSpacer()

        # Panel button et def
        PanelDef = wx.Panel(self, -1)
        DefSizer = wx.BoxSizer(wx.HORIZONTAL)

        # Panel avec les button
        PanelButton = wx.Panel(PanelDef, -1)
        ButtonSizer = wx.BoxSizer(wx.VERTICAL)
        self.ButtonAdd = wx.Button(PanelButton, 1, label="Add")
        ButtonSizer.Add(self.ButtonAdd, 0, wx.EXPAND)
        self.ButtonClear = wx.Button(PanelButton, 2, label="Clear")
        self.ButtonClear.Disable()
        ButtonSizer.Add(self.ButtonClear, 0, wx.EXPAND)
        self.ButtonChange = wx.Button(PanelButton, 3, label="Change")
        self.ButtonChange.Disable()
        ButtonSizer.Add(self.ButtonChange, 0, wx.EXPAND)
        PanelButton.SetSizerAndFit(ButtonSizer)
        DefSizer.Add(PanelButton, 0, wx.EXPAND)
        # panel avec la liste non modifiable
        PanelList = wx.Panel(PanelDef, -1)
        self.ListFactor = wx.ListBox(
            PanelList, 1, size=(100, 100), style=wx.LB_SINGLE)
        DefSizer.Add(PanelList, wx.EXPAND)
        PanelDef.SetSizerAndFit(DefSizer)
        FrameSizer.Add(PanelDef, 0, wx.EXPAND)
        FrameSizer.AddStretchSpacer()

        # Panel Continue
        PanelContinue = wx.Panel(self, -1)
        ContinueSizer = wx.BoxSizer(wx.VERTICAL)
        ContinueButton = wx.Button(PanelContinue, 4, label="Continue")
        ContinueSizer.Add(ContinueButton, 0, wx.ALIGN_RIGHT)
        PanelContinue.SetSizer(ContinueSizer)
        FrameSizer.Add(PanelContinue, 0, wx.EXPAND)
        self.SetSizer(FrameSizer)
        Factor = []
        for i in range(len(self.Factor)):
            name = []
            name.append(self.Factor[i])
            name.append('(')
            name.append(str(self.Level[i]))
            name.append(')')
            Factor.append("".join(name))
        self.ListFactor.SetItems(Factor)

        # les evenements !!!!
        wx.EVT_BUTTON(self, 1, self.Add)
        wx.EVT_BUTTON(self, 2, self.Clear)
        wx.EVT_BUTTON(self, 3, self.Change)
        wx.EVT_BUTTON(self, 4, self.Continue)
        wx.EVT_LISTBOX(self, 1, self.ItemSelected)

    def ItemSelected(self, event):
        self.ButtonChange.Enable()
        self.ButtonClear.Enable()
        self.ButtonAdd.Disable()
        idx = self.ListFactor.GetSelections()
        self.FactorName.SetValue(self.Factor[idx[0]])
        self.LevelNb.SetValue(str(self.Level[idx[0]]))

    def Add(self, event):

        name = []
        name.append(self.FactorName.GetValue())
        name.append('(')
        name.append(self.LevelNb.GetValue())
        name.append(')')
        Factor = self.ListFactor.GetItems()
        try:
            level = int(self.LevelNb.GetValue())
            if level == 1:
                dlg = wx.MessageDialog(
                    'Level must be bigger than 1', style=wx.OK)
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
            dlg = wx.MessageDialog(
                self, 'Numbers of level must be integer', style=wx.OK)
            retour = dlg.ShowModal()
            dlg.Destroy()
            self.FactorName.SetValue('')
            self.LevelNb.SetValue('')

    def Clear(self, event):
        idx = self.ListFactor.GetSelections()
        idx = idx[0]
        self.ListFactor.Delete(idx)
        self.ButtonChange.Disable()
        self.ButtonAdd.Enable()
        self.ButtonClear.Disable()
        self.FactorName.SetValue('')
        self.LevelNb.SetValue('')

    def Change(self, event):
        self.ButtonChange.Disable()
        self.ButtonAdd.Enable()
        self.ButtonClear.Disable()
        idx = self.ListFactor.GetSelections()
        idx = idx[0]
        Factor = self.ListFactor.GetItems()
        name = []
        name.append(self.FactorName.GetValue())
        name.append('(')
        name.append(self.LevelNb.GetValue())
        name.append(')')
        try:
            level = int(self.LevelNb.GetValue())
            if level == 1:
                dlg = wx.MessageDialog(
                    'Level must be bigger than 1', style=wx.OK)
                retour = dlg.ShowModal()
                dlg.Destroy()
                self.FactorName.SetValue(self.Factor[idx])
                self.LevelNb.SetValue(str(self.Level[idx]))
            else:
                self.Level[idx] = level
                self.Factor[idx] = self.FactorName.GetValue()
                Factor[idx] = "".join(name)
                self.ListFactor.SetItems(Factor)
                self.ListFactor.DeselectAll()
                self.FactorName.SetValue('')
                self.LevelNb.SetValue('')
        except:
            dlg = wx.MessageDialog(
                self, 'Numbers of level must be integer', style=wx.OK)
            retour = dlg.ShowModal()
            dlg.Destroy()
            self.FactorName.SetValue(self.Factor[idx])
            self.LevelNb.SetValue(str(self.Level[idx]))

    def Continue(self, event):
        self.ModelFull = FactorDef(self.NoEmptyCol, self.Sheet, self)
        self.ModelFull.Show(True)
        self.Show(False)
        self.DataEntry.FactorName = self.Factor
