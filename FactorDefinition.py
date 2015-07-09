import wx
import numpy as np
import os
from DefineModel import DefineModel


class FactorDef(wx.Frame):

    """ TODO: translate to english
    attribution des facteurs style SPSS"""

    def __init__(self, NoEmptyCol, Sheet, Parent):
        wx.Frame.__init__(
            self, None, -1, title="Factor definition", size=(200, 250))
        FrameSizer = wx.BoxSizer(wx.VERTICAL)
        # Panel des definition
        PanelInit = wx.Panel(self, -1)
        SizerInit = wx.BoxSizer(wx.HORIZONTAL)
        self.Subject = []
        self.Within = []
        self.WithinIndex = []
        self.Between = []
        self.BetweenIndex = []
        self.Covariate = []
        self.CovariateIndex = []
        self.Level = Parent.Level
        self.Sheet = Sheet
        self.TabValue = Parent.TabValue
        self.DataEntry = Parent.DataEntry
        self.DataEntry.ColFactor = []
        self.FactorWithin = Parent
        # List des colones
        self.ColName = []
        for i in NoEmptyCol:
            self.ColName.append(Sheet.GetColLabelValue(i))
        self.ListCol = wx.ListBox(
            PanelInit, 1, choices=self.ColName, style=wx.LB_EXTENDED)
        SizerInit.Add(self.ListCol, 0, wx.EXPAND)

        # panels des case pour la définition
        PanelDef = wx.Panel(PanelInit, -1)
        SizerDef = wx.BoxSizer(wx.VERTICAL)

        # Panel Subject
        PanelSubject = wx.Panel(PanelDef, -1, size=(200, 200))
        SizerSubject = wx.BoxSizer(wx.HORIZONTAL)

        PanelSubjectButton = wx.Panel(PanelSubject, -1)
        SizerSubjectButton = wx.BoxSizer(wx.VERTICAL)
        self.SubjectAdd = wx.Button(PanelSubjectButton, 1, label='>')
        SizerSubjectButton.Add(self.SubjectAdd, 0, wx.EXPAND)
        self.SubjectAdd.Disable()
        self.SubjectRm = wx.Button(PanelSubjectButton, 2, label='<')
        SizerSubjectButton.Add(self.SubjectRm, 0, wx.EXPAND)
        self.SubjectRm.Disable()
        PanelSubjectButton.SetSizer(SizerSubjectButton)

        PanelSubjectVariable = wx.Panel(PanelSubject, -1)
        SizerSubjectVariable = wx.BoxSizer(wx.VERTICAL)
        SubjectText = wx.StaticText(PanelSubjectVariable, -1,
                                    label="Subject Variable",
                                    style=wx.ALIGN_CENTER)
        SizerSubjectVariable.Add(SubjectText, 0, wx.EXPAND)
        self.SubjectVariable = wx.TextCtrl(
            PanelSubjectVariable, 1, value="", style=wx.TE_READONLY)
        SizerSubjectVariable.Add(self.SubjectVariable, 0, wx.EXPAND)
        PanelSubjectVariable.SetSizer(SizerSubjectVariable)

        SizerSubject.Add(PanelSubjectButton, 0, wx.ALIGN_CENTRE)
        SizerSubject.Add(PanelSubjectVariable, 0, wx.ALIGN_RIGHT)
        PanelSubject.SetSizer(SizerSubject)

        SizerDef.Add(PanelSubject, 0, wx.EXPAND)

        # Panel Within
        PanelWithin = wx.Panel(PanelDef, -1)
        SizerWithin = wx.BoxSizer(wx.HORIZONTAL)

        PanelWithinButton = wx.Panel(PanelWithin, -1)
        SizerWithinButton = wx.BoxSizer(wx.VERTICAL)
        self.WithinAdd = wx.Button(PanelWithinButton, 3, label='>')
        SizerWithinButton.Add(self.WithinAdd, 0, wx.EXPAND)
        self.WithinAdd.Disable()
        self.WithinRm = wx.Button(PanelWithinButton, 4, label='<')
        SizerWithinButton.Add(self.WithinRm, 0, wx.EXPAND)
        self.WithinRm.Disable()
        PanelWithinButton.SetSizer(SizerWithinButton)

        PanelWithinVariable = wx.Panel(PanelWithin, -1)
        SizerWithinVariable = wx.BoxSizer(wx.VERTICAL)
        WithinText = wx.StaticText(PanelWithinVariable, -1,
                                   label="Within Subject Variable(s)",
                                   style=wx.ALIGN_CENTER)
        SizerWithinVariable.Add(WithinText, 0, wx.EXPAND)
        Model = DefineModel(Parent.Level, [1], [1], [1])
        if Model.Within.any():
            ListFactorWithin = Model.Within.tolist()
        else:
            ListFactorWithin = [[]]


# ListFactorWithin=Model.Within.tolist()
        Fact = []

        if ListFactorWithin == [[]]:
            WithinText.SetLabel('Data')
            Fact = ['_?_']
        else:
            for i in ListFactorWithin:
                tmp = []
                for j in i:
                    number = int(j)
                    tmp.append(str(number))
                FactNumber = ",".join(tmp)
                tmp = ['_?_(']
                tmp.append(FactNumber)
                tmp.append(')')
                Fact.append("".join(tmp))
        self.WithinVariable = wx.ListBox(PanelWithinVariable, 2,
                                         choices=Fact, size=(100, 100),
                                         style=wx.LB_EXTENDED)
        SizerWithinVariable.Add(self.WithinVariable, 0, wx.EXPAND)
        PanelWithinVariable.SetSizer(SizerWithinVariable)

        SizerWithin.Add(PanelWithinButton, 0, wx.wx.ALIGN_CENTRE)
        SizerWithin.Add(PanelWithinVariable, 0, wx.wx.ALIGN_RIGHT)
        PanelWithin.SetSizer(SizerWithin)

        SizerDef.Add(PanelWithin, 0, wx.EXPAND)

        # Panel Between
        PanelBetween = wx.Panel(PanelDef, -1)
        SizerBetween = wx.BoxSizer(wx.HORIZONTAL)

        PanelBetweenButton = wx.Panel(PanelBetween, -1)
        SizerBetweenButton = wx.BoxSizer(wx.VERTICAL)
        self.BetweenAdd = wx.Button(PanelBetweenButton, 5, label='>')
        SizerBetweenButton.Add(self.BetweenAdd, 0, wx.EXPAND)
        self.BetweenAdd.Disable()
        self.BetweenRm = wx.Button(PanelBetweenButton, 6, label='<')
        SizerBetweenButton.Add(self.BetweenRm, 0, wx.EXPAND)
        self.BetweenRm.Disable()
        PanelBetweenButton.SetSizer(SizerBetweenButton)

        PanelBetweenVariable = wx.Panel(PanelBetween, -1)
        SizerBetweenVariable = wx.BoxSizer(wx.VERTICAL)
        BetweenText = wx.StaticText(PanelBetweenVariable, -1,
                                    label="Between Subject Variable(s)",
                                    style=wx.ALIGN_CENTER)
        SizerBetweenVariable.Add(BetweenText, 0, wx.EXPAND)
        self.BetweenVariable = wx.ListBox(
            PanelBetweenVariable, 3, size=(100, 100), style=wx.LB_EXTENDED)
        SizerBetweenVariable.Add(self.BetweenVariable, 0, wx.EXPAND)
        PanelBetweenVariable.SetSizer(SizerBetweenVariable)

        SizerBetween.Add(PanelBetweenButton, 0, wx.ALIGN_CENTRE)
        SizerBetween.Add(PanelBetweenVariable, 0, wx.ALIGN_RIGHT)
        PanelBetween.SetSizer(SizerBetween)

        SizerDef.Add(PanelBetween, 0, wx.EXPAND)

        # Panel Covariate
        PanelCovariate = wx.Panel(PanelDef, -1)
        SizerCovariate = wx.BoxSizer(wx.HORIZONTAL)

        PanelCovariateButton = wx.Panel(PanelCovariate, -1)
        SizerCovariateButton = wx.BoxSizer(wx.VERTICAL)
        self.CovariateAdd = wx.Button(PanelCovariateButton, 7, label='>')
        SizerCovariateButton.Add(self.CovariateAdd, 0, wx.EXPAND)
        self.CovariateAdd.Disable()
        self.CovariateRm = wx.Button(PanelCovariateButton, 8, label='<')
        SizerCovariateButton.Add(self.CovariateRm, 0, wx.EXPAND)
        self.CovariateRm.Disable()
        PanelCovariateButton.SetSizer(SizerCovariateButton)

        PanelCovariateVariable = wx.Panel(PanelCovariate, -1)
        SizerCovariateVariable = wx.BoxSizer(wx.VERTICAL)
        CovariateText = wx.StaticText(PanelCovariateVariable, -1,
                                      label="Covariate(s)",
                                      style=wx.ALIGN_CENTER)
        SizerCovariateVariable.Add(CovariateText, 0, wx.EXPAND)
        self.CovariateVariable = wx.ListBox(
            PanelCovariateVariable, 4, size=(100, 100), style=wx.LB_EXTENDED)
        SizerCovariateVariable.Add(self.CovariateVariable, 0, wx.EXPAND)
        PanelCovariateVariable.SetSizer(SizerCovariateVariable)

        SizerCovariate.Add(PanelCovariateButton, 0, wx.ALIGN_CENTRE)
        SizerCovariate.Add(PanelCovariateVariable, 0, wx.ALIGN_RIGHT)
        PanelCovariate.SetSizer(SizerCovariate)

        SizerDef.Add(PanelCovariate, 0, wx.EXPAND)

        PanelDef.SetSizer(SizerDef)
        SizerInit.Add(PanelDef, 0, wx.EXPAND)
        PanelInit.SetSizer(SizerInit)
        FrameSizer.Add(PanelInit, 0, wx.EXPAND)
        # Panel Button OK
        PanelOK = wx.Panel(self, -1)
        SizerOK = wx.BoxSizer(wx.HORIZONTAL)
        ButtonPrevious = wx.Button(
            PanelOK, 9, label='return to Within Subject factor definition')
        SizerOK.Add(ButtonPrevious, 0, wx.ALIGN_LEFT)
        ButtonOK = wx.Button(PanelOK, 10, label='OK')
        SizerOK.Add(ButtonOK, 0, wx.ALIGN_RIGHT)
        PanelOK.SetSizer(SizerOK)
        FrameSizer.Add(PanelOK, 0, wx.ALIGN_RIGHT)
        self.SetSizerAndFit(FrameSizer)

        # evenement
        # les evenements !!!!
        wx.EVT_BUTTON(self, 1, self.AddSubject)
        wx.EVT_BUTTON(self, 2, self.RmSubject)
        wx.EVT_BUTTON(self, 3, self.AddWithin)
        wx.EVT_BUTTON(self, 4, self.RmWithin)
        wx.EVT_BUTTON(self, 5, self.AddBetween)
        wx.EVT_BUTTON(self, 6, self.RmBetween)
        wx.EVT_BUTTON(self, 7, self.AddCovariate)
        wx.EVT_BUTTON(self, 8, self.RmCovariate)
        # 1: colone 2: facteur 3: between 4: covariate
        wx.EVT_LISTBOX(self, 1, self.ColSelected)
        wx.EVT_LISTBOX(self, 2, self.WithinSelected)
        wx.EVT_LISTBOX(self, 3, self.BetweenSelected)
        wx.EVT_LISTBOX(self, 4, self.CovariateSelected)
        wx.EVT_BUTTON(self, 10, self.Ok)
        wx.EVT_BUTTON(self, 9, self.Previous)

        # bouton OK avec les facteur sous forme de vecteur
    def Previous(self, event):
        self.FactorWithin.Show(True)
        self.Close()

    def Ok(self, event):
        self.DataEntry.ColFactor = self.WithinVariable.GetItems()
        level = np.array(self.Level)
        self.DataEntry.Level = level
        NbLevel = level.prod()
        error = []
        subject = []
        errortmp = []
        if self.Subject == []:
            error.append('Subject colone not define')
        for i in self.Subject:
            if type(i) == list:
                for s in i:
                    try:
                        subject.append(int(s))
                    except:
                        errortmp = 1
            else:
                try:
                    subject.append(int(s))
                except:
                    errortmp = 1

        if errortmp == 1:
            error.append('Subject colone must be an integer')
        else:
            subject = np.array(subject)
            if subject.max() > len(subject):
                error.append('Subject number bigger than length')
            else:
                self.Subject = subject.squeeze()
                self.DataEntry.Subject = subject.squeeze()

        Within = []
        errortmp = []
        for f in self.Within:
            if type(f) == list:
                tmp = []
                for e in f:
                    if e[len(e) - 4:len(e)] == '.eph':

                        tmp.append(os.path.abspath(str(e)))
                    else:
                        errortmp = 1
                Within.append(tmp)
            else:
                if f[len(f) - 4:len(f)] == '.eph':
                    Within.append(str(f))
                else:
                    errortmp = 2

        if errortmp == 1:
            error.append('Within colones must contain *.eph file')
        elif errortmp == 2:
            error.append('Within colone must contain *.eph file')
        else:
            self.DataEntry.Within = Within
        if NbLevel != len(self.Within):
            error.append('Fill all Within subject factor')

        errortmp = []
        between = []
        for f in self.Between:
            if type(f) == list:
                tmp = []
                for e in f:
                    try:
                        tmp.append(int(e))
                    except:
                        errortmp = 1
                between.append(tmp)
            else:
                try:
                    between.append(int(e))
                except:
                    errortmp = 2
        if errortmp == 1:
            error.append('Between colones must be an integer')
        elif errortmp == 2:
            error.append('Between colone must be an integer')
        else:
            between = np.array(between)
            self.DataEntry.Between = between.squeeze()
            self.DataEntry.BetweenIndex = self.BetweenIndex

        covariate = []
        errortmp = []
        for f in self.Covariate:
            if type(f) == list:
                tmp = []
                for e in f:
                    try:
                        tmp.append(float(e))
                    except:
                        errortmp = 1
                covariate.append(tmp)
            else:
                try:
                    covariate.append(float(e))
                except:
                    errortmp = 2
        if errortmp == 1:
            error.append('Covariate colones must be a float')
        elif errortmp == 2:
            error.append('Covariate colone must be a float')
        else:
            covariate = np.array(covariate)
            self.DataEntry.Covariate = covariate.squeeze()
            self.DataEntry.CovariateIndex = self.CovariateIndex

        if error != []:
            self.Show(False)
            self.DataEntry.Buttonsave.Disable()
# self.DataEntry.ButtonModify.Disable()
            dlg = wx.MessageDialog(self, " \n ".join(error), style=wx.OK)
            retour = dlg.ShowModal()
            dlg.Destroy()

        else:
            self.DataEntry.Buttonsave.Enable()
# self.DataEntry.ButtonModify.Enable()
            self.Show(False)

        # Summary(self.WithinVariable.GetItems(),self.BetweenVariable.GetItems(),self.SubjectVariable.GetLabel(),self.CovariateVariable.GetItems(),self.DataEntry.SummaryTxT)
    def AddSubject(self, event):
        self.SubjectAdd.Disable()
        self.SubjectRm.Enable()
        ColNumber = self.ListCol.GetSelections()
        ColName = self.ListCol.GetItems()
        if len(ColNumber) == 1:
            name = ColName[ColNumber[0]]
            self.SubjectVariable.SetLabel(name)
            ColName.pop(ColNumber[0])
            # ColName.append('')
            self.ListCol.SetItems(ColName)
            ColNumber = self.ColName.index(name)
            self.ColNumberSubject = ColNumber
            self.Subject.append(self.TabValue[ColNumber])
        else:
            dlg = wx.MessageDialog(
                self, 'Select only one variables for Subject', style=wx.OK)
            retour = dlg.ShowModal()
            dlg.Destroy()

    def RmSubject(self, event):
        self.SubjectRm.Disable()
        self.SubjectAdd.Enable()
        ColName = self.ListCol.GetItems()
        VariableSubject = self.SubjectVariable.GetLabel()
        ColName.insert(self.ColNumberSubject, VariableSubject)
        self.Subject = []
        self.SubjectVariable.SetLabel("")
        self.ListCol.SetItems(ColName)

    def AddWithin(self, event):
        ColNumber = self.ListCol.GetSelections()
        ColName = self.ListCol.GetItems()
        Factor = self.WithinVariable.GetItems()
        NbFactor = len(Factor)
        if len(self.Within) + len(ColNumber) > NbFactor:
            dlg = wx.MessageDialog(
                self, 'Within subject factor is full', style=wx.OK)
            retour = dlg.ShowModal()
            dlg.Destroy()
        else:
            if len(ColNumber) > NbFactor:
                dlg = wx.MessageDialog(self,
                                       'Number of selected Variable exceed number of Factor',
                                       style=wx.OK)
                retour = dlg.ShowModal()
                dlg.Destroy()
            else:
                Selections = ColNumber[0:NbFactor]
                for i in Selections:
                    # i is a integer
                    nametmp = []
                    nametmp.append(ColName[i])
                    n = -1
                    mark = -1
                    while mark == -1:
                        n += 1
                        mark = Factor[n].find('?')
                    tmpfact = Factor[n]
                    debut = tmpfact.find('(')
                    if debut != -1:
                        nametmp.append(tmpfact[debut:len(tmpfact)])
                    Factor[n] = "".join(nametmp)

                    index = self.ColName.index(ColName[i])
                    self.WithinIndex.append(index)
                    self.Within.append(self.TabValue[index])
                    ColName[i] = ''
                ColNameNew = []
                for i in ColName:
                    if i != '':
                        ColNameNew.append(i)

                self.ListCol.SetItems(ColNameNew)
                self.WithinVariable.SetItems(Factor)

    def RmWithin(self, event):
        FactorSelections = self.WithinVariable.GetSelections()
        Factor = self.WithinVariable.GetItems()
        ColName = self.ListCol.GetItems()
        for i in FactorSelections:
            name = Factor[i]
            fin = name.find('(')
            facttmp = ['_?_']
            if fin != -1:
                facttmp.append(name[fin:len(name)])
                name = name[0:fin]
            Factor[i] = "".join(facttmp)
            ColName.insert(self.WithinIndex[i], name)
            self.WithinIndex[i] = ''
            self.Within[i] = []

        tmp = []
        for i in self.WithinIndex:
            if i != '':
                tmp.append(i)
        self.WithinIndex = tmp
        tmpvalue = []
        for i in self.Within:
            if i != []:
                tmpvalue.append(i)
        ColNameNew = []
        for i in ColName:
            if i != '':
                ColNameNew.append(i)
        for i in ColName:
            if i == '':
                ColNameNew.append('')
        self.Within = tmpvalue
        self.ListCol.SetItems(ColNameNew)
        self.WithinVariable.SetItems(Factor)

    def AddBetween(self, event):
        ColNumber = self.ListCol.GetSelections()
        ColName = self.ListCol.GetItems()
        name = self.BetweenVariable.GetItems()
        for i in ColNumber:
            name.append(ColName[i])
            index = self.ColName.index(ColName[i])
            self.BetweenIndex.append(index)
            self.Between.append(self.TabValue[index])
            ColName[i] = ''
        ColNameNew = []
        for i in ColName:
            if i != '':
                ColNameNew.append(i)
        self.ListCol.SetItems(ColNameNew)
        self.BetweenVariable.SetItems(name)

    def RmBetween(self, event):
        Selections = self.BetweenVariable.GetSelections()
        name = self.BetweenVariable.GetItems()
        ColName = self.ListCol.GetItems()
        for i in Selections:
            ColName.insert(self.BetweenIndex[i], name[i])
            self.Between[i] = []
            self.BetweenIndex = ''
            name[i] = ''

        tmp = []

        for i in self.BetweenIndex:
            if i != '':
                tmp.append(i)
        NameNew = []
        for i in name:
            if i != '':
                NameNew.append(i)
        self.BetweenIndex = tmp
        tmpvalue = []
        for i in self.Between:
            if i != []:
                tmpvalue.append(i)
        ColNameNew = []
        for i in ColName:
            if i != '':
                ColNameNew.append(i)
        for i in ColName:
            if i == '':
                ColNameNew.append('')
        self.Between = tmpvalue
        self.ListCol.SetItems(ColNameNew)
        self.BetweenVariable.SetItems(NameNew)

    def AddCovariate(self, event):
        ColNumber = self.ListCol.GetSelections()
        ColName = self.ListCol.GetItems()
        name = self.CovariateVariable.GetItems()
        for i in ColNumber:
            name.append(ColName[i])
            index = self.ColName.index(ColName[i])
            self.CovariateIndex.append(index)
            self.Covariate.append(self.TabValue[index])
            ColName[i] = ''
        ColNameNew = []
        for i in ColName:
            if i != '':
                ColNameNew.append(i)

        self.ListCol.SetItems(ColNameNew)
        self.CovariateVariable.SetItems(name)

    def RmCovariate(self, event):
        Selections = self.CovariateVariable.GetSelections()
        name = self.CovariateVariable.GetItems()
        ColName = self.ListCol.GetItems()
        for i in Selections:
            ColName.insert(self.CovariateIndex[i], name[i])
            self.CovariateIndex[i] = ''
            self.Covariate[i] = []
            name[i] = ''

        tmp = []
        for i in self.CovariateIndex:
            if i != '':
                tmp.append(i)
        NameNew = []
        for i in name:
            if i != '':
                NameNew.append(i)
        tmpvalue = []
        for i in self.Covariate:
            if i != []:
                tmpvalue.append(i)
        ColNameNew = []
        for i in ColName:
            if i != '':
                ColNameNew.append(i)
        for i in ColName:
            if i == '':
                ColNameNew.append('')
        self.Covariate = tmpvalue
        self.CovariateIndex = tmp
        self.ListCol.SetItems(ColNameNew)
        self.CovariateVariable.SetItems(NameNew)

    def ColSelected(self, event):
        self.WithinAdd.Enable()
        self.BetweenAdd.Enable()
        self.CovariateAdd.Enable()
        self.WithinRm.Disable()
        self.BetweenRm.Disable()
        self.CovariateRm.Disable()
        if self.SubjectVariable.GetLabel() == "":
            self.SubjectRm.Disable()
            self.SubjectAdd.Enable()
        else:
            self.SubjectRm.Enable()
            self.SubjectAdd.Disable()

    def WithinSelected(self, event):
        self.SubjectAdd.Disable()
        self.WithinAdd.Disable()
        self.BetweenAdd.Disable()
        self.CovariateAdd.Disable()
        self.SubjectRm.Disable()
        self.WithinRm.Enable()
        self.BetweenRm.Disable()
        self.CovariateRm.Disable()

    def BetweenSelected(self, event):
        self.SubjectAdd.Disable()
        self.WithinAdd.Disable()
        self.BetweenAdd.Disable()
        self.CovariateAdd.Disable()
        self.SubjectRm.Disable()
        self.WithinRm.Disable()
        self.BetweenRm.Enable()
        self.CovariateRm.Disable()

    def CovariateSelected(self, event):
        self.SubjectAdd.Disable()
        self.WithinAdd.Disable()
        self.BetweenAdd.Disable()
        self.CovariateAdd.Disable()
        self.SubjectRm.Disable()
        self.WithinRm.Disable()
        self.BetweenRm.Disable()
        self.CovariateRm.Enable()
