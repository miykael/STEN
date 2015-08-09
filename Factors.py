import wx
import numpy as np
import os
import itertools


class FactorWithin(wx.Frame):

    """Window to specify the within factors"""

    def __init__(self, DataPanel, factorNames, factorLevels):
        wx.Frame.__init__(self, None, wx.ID_ANY, size=(325, 220),
                          title="Factor Definition: Within Subject",
                          style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
        self.DataPanel = DataPanel

        # Specify relevant variables
        self.Factor = factorNames
        self.Level = factorLevels
        self.dataTable = DataPanel.dataTable
        self.Sheet = DataPanel.Sheet

        # Panel: Factor Information
        PanelFactor = wx.Panel(self, wx.ID_ANY)
        sizerFactor = wx.BoxSizer(wx.VERTICAL)
        # Factor Titles
        PanelTitle = wx.Panel(PanelFactor, wx.ID_ANY)
        sizerPanelTitle = wx.BoxSizer(wx.HORIZONTAL)
        sizerPanelTitle.AddSpacer(5)
        TextFactorName = wx.StaticText(PanelTitle, wx.ID_ANY,
                                       label="Within Subject Factor")
        sizerPanelTitle.Add(TextFactorName, 0, wx.EXPAND)
        sizerPanelTitle.AddSpacer(20)
        sizerPanelTitle.AddSpacer(20)
        TextNumLevel = wx.StaticText(PanelTitle, wx.ID_ANY,
                                     label="Number of Levels")
        sizerPanelTitle.Add(TextNumLevel, 0, wx.EXPAND)
        PanelTitle.SetSizer(sizerPanelTitle)
        # Factor Fields
        PanelInputField = wx.Panel(PanelFactor, wx.ID_ANY)
        sizerPanelInputField = wx.BoxSizer(wx.HORIZONTAL)
        sizerPanelInputField.AddSpacer(3)
        self.FactorName = wx.TextCtrl(PanelInputField, wx.ID_ANY, value="main",
                                      size=(182, 25))
        sizerPanelInputField.Add(self.FactorName, 0, wx.EXPAND)
        sizerPanelInputField.AddSpacer(5)
        self.NumLevel = wx.TextCtrl(PanelInputField, wx.ID_ANY, size=(124, 25),
                                    value=str(self.dataTable['nCols'] - 1))
        sizerPanelInputField.Add(self.NumLevel, 0, wx.EXPAND)
        PanelInputField.SetSizer(sizerPanelInputField)
        sizerFactor.AddSpacer(3)
        sizerFactor.Add(PanelTitle)
        sizerFactor.Add(PanelInputField)
        PanelFactor.SetSizerAndFit(sizerFactor)

        # Panel: Buttons and Factor Definition
        PanelDefinition = wx.Panel(self, wx.ID_ANY)
        sizerDefinition = wx.BoxSizer(wx.HORIZONTAL)
        # Button Add, Delete, Change and Continue
        PanelButton = wx.Panel(PanelDefinition, wx.ID_ANY)
        sizerButton = wx.BoxSizer(wx.VERTICAL)
        self.ButtonAdd = wx.Button(PanelButton, wx.ID_ANY, label="Add")
        sizerButton.Add(self.ButtonAdd, 0, wx.EXPAND)
        self.ButtonDelete = wx.Button(PanelButton, wx.ID_ANY, label="Delete")
        self.ButtonDelete.Disable()
        sizerButton.Add(self.ButtonDelete, 0, wx.EXPAND)
        self.ButtonChange = wx.Button(PanelButton, wx.ID_ANY, label="Change")
        self.ButtonChange.Disable()
        sizerButton.Add(self.ButtonChange, 0, wx.EXPAND)
        sizerButton.AddSpacer(30)
        self.ButtonContinue = wx.Button(PanelButton, wx.ID_ANY,
                                        label="Continue")
        self.ButtonContinue.Disable()
        sizerButton.Add(self.ButtonContinue, 0, wx.EXPAND)
        PanelButton.SetSizerAndFit(sizerButton)

        # Panel: Definition List
        PanelDefList = wx.Panel(PanelDefinition, wx.ID_ANY)
        self.ListFactor = wx.ListBox(PanelDefList, wx.ID_ANY,
                                     style=wx.LB_SINGLE,
                                     size=(175, 145))
        sizerDefinition.Add(PanelButton, 0, wx.EXPAND)
        sizerDefinition.AddSpacer(5)
        sizerDefinition.Add(PanelDefList, 0, wx.EXPAND)
        PanelDefinition.SetSizerAndFit(sizerDefinition)

        # Resize everything and create the window
        FrameSizer = wx.BoxSizer(wx.VERTICAL)
        FrameSizer.Add(PanelFactor, 0, wx.EXPAND)
        FrameSizer.AddSpacer(10)
        FrameSizer.Add(PanelDefinition, 0, wx.EXPAND)
        FrameSizer.AddSpacer(5)
        self.SetSizerAndFit(FrameSizer)

        # Specification of events
        wx.EVT_LISTBOX(self, self.ListFactor.Id, self.selectItem)
        wx.EVT_BUTTON(self, self.ButtonAdd.Id, self.addFactor)
        wx.EVT_BUTTON(self, self.ButtonDelete.Id, self.deleteFactor)
        wx.EVT_BUTTON(self, self.ButtonChange.Id, self.changeFactor)
        wx.EVT_BUTTON(self, self.ButtonContinue.Id, self.defineFactor)

        # Update List with previous elements if window was already opened
        if self.Factor != []:
            self.updateList()

    def updateList(self):
        """Adds previous factors to list if Factor Window was already open"""
        Factors = []
        factorNames = self.Factor
        factorLevels = self.Level
        for i in range(len(self.Factor)):
            newFactor = '%s(%s)' % (factorNames[i], factorLevels[i])
            Factors.append(newFactor)
        self.ListFactor.SetItems(Factors)
        self.ButtonContinue.Enable()

    def selectItem(self, event):
        """Write selected item information into fields above"""
        idx = self.ListFactor.GetSelections()[0]
        self.FactorName.SetValue(self.Factor[idx])
        self.NumLevel.SetValue(str(self.Level[idx]))
        # Change GUI layout
        self.ButtonChange.Enable()
        self.ButtonDelete.Enable()

    def addFactor(self, event):
        """Add Factor to inventar and to list field"""

        newFactorName = self.FactorName.GetValue()
        newNumLevel = self.NumLevel.GetValue()

        # Check that input is valid
        inputIsValid = self.checkInput(newFactorName, newNumLevel)
        if inputIsValid:
            # Check that name doesn't already exist
            if newFactorName in self.Factor:
                self.showMessage(
                    title='Factor name already exists',
                    message='There is already a factor called ' +
                            '"%s".\n' % newFactorName +
                            'Please use another factor name.')
            else:
                # Add factor to inventar
                self.Factor.append(newFactorName)
                self.Level.append(int(newNumLevel))

                # Add name and level to list field
                newFactor = '%s(%s)' % (newFactorName,
                                        newNumLevel)
                Factor = self.ListFactor.GetItems()
                Factor.append(newFactor)
                self.ListFactor.SetItems(Factor)

                # Change GUI layout
                self.ListFactor.DeselectAll()
                self.FactorName.SetValue('')
                self.NumLevel.SetValue('')
                self.ButtonContinue.Enable()

    def deleteFactor(self, event):
        """Delete selected factor from inventar and list field"""

        # Delete factor from list field and inventar
        idx = self.ListFactor.GetSelections()[0]
        self.ListFactor.Delete(idx)
        self.Factor.pop(idx)
        self.Level.pop(idx)

        # Change focus to next item if exists
        listLength = len(self.ListFactor.GetItems())
        if listLength == 0:
            self.ButtonDelete.Disable()
            self.ButtonChange.Disable()
            self.ButtonContinue.Disable()
        elif listLength > idx:
            self.FactorName.SetValue(self.Factor[idx])
            self.NumLevel.SetValue(unicode(self.Level[idx]))
            self.ListFactor.SetSelection(idx)
        elif listLength == idx:
            self.FactorName.SetValue(self.Factor[idx-1])
            self.NumLevel.SetValue(unicode(self.Level[idx-1]))
            self.ListFactor.SetSelection(idx-1)

    def changeFactor(self, event):
        """Changes the name and level of a selected factor"""

        newFactorName = self.FactorName.GetValue()
        newNumLevel = self.NumLevel.GetValue()

        # Check that input is valid
        inputIsValid = self.checkInput(newFactorName, newNumLevel)

        if inputIsValid:
            idx = self.ListFactor.GetSelections()[0]
            self.Factor[idx] = newFactorName
            self.Level[idx] = int(newNumLevel)
            Factor = self.ListFactor.GetItems()
            newFactor = '%s(%s)' % (newFactorName, newNumLevel)
            Factor[idx] = newFactor
            self.ListFactor.SetItems(Factor)
            self.ListFactor.SetSelection(idx)

    def showMessage(self, title, message):
        """Shows Warning Popup Window"""
        dlg = wx.MessageDialog(self, style=wx.OK,
                               caption=title, message=message)
        dlg.ShowModal()
        dlg.Destroy()

    def checkInput(self, name, level):
        """Checks if a factor input is valid or not"""

        inputIsValid = False

        if name == '' or level == '':
            self.showMessage(
                title='Fill out all fields',
                message='Please specify the name of the factor (string)\n' +
                        'and the number of levels (integer)!')
        elif name[0].isdigit():
            self.showMessage(
                title='Not a valid name',
                message='Value for factor name must start with a letter!')

        elif not level.isdigit():
            self.showMessage(
                title='Not a valid number',
                message='Value for number of levels must be an integer!')
        elif int(level) <= 1:
            self.showMessage(
                title='Number of levels to small',
                message='Number of levels must be bigger than 1!')
        else:
            inputIsValid = True

        return inputIsValid

    def defineFactor(self, event):

        self.ModelFull = FactorDef(self.Sheet, self)
        self.ModelFull.Show(True)
        self.Show(False)


class FactorDef(wx.Frame):

    """ TODO: translate to english
    attribution des facteurs"""

    def __init__(self, Sheet, FactorWithin):
        wx.Frame.__init__(self, None, wx.ID_ANY, size=(200, 250),
                          title="Factor definition")

        # Specify relevant variables
        self.ColName = FactorWithin.dataTable['labels']
        self.Subject = ''
        #TODO: which variables are needed?
        self.Within = []
        self.WithinIndex = []
        self.Between = []
        self.BetweenIndex = []
        self.Covariate = []
        self.CovariateIndex = []
        self.Level = FactorWithin.Level
        self.Sheet = Sheet
        self.TabValue = FactorWithin.dataTable['content']
        self.FactorWithin = FactorWithin

        # Panel: Left Input Area
        PanelInput = wx.Panel(self, wx.ID_ANY)
        sizerInput = wx.BoxSizer(wx.HORIZONTAL)
        self.ListInput = wx.ListBox(PanelInput, wx.ID_ANY,
                                    choices=self.ColName,
                                    style=wx.LB_EXTENDED)
        sizerInput.Add(self.ListInput, 0, wx.EXPAND)
        self.ListInput.SetSelection(0)

        # Panel: Right Definition Area
        PanelDef = wx.Panel(PanelInput, wx.ID_ANY)
        sizerDef = wx.BoxSizer(wx.VERTICAL)

        # Subject Panel Area
        PanelSubject = wx.Panel(PanelDef, wx.ID_ANY)
        sizerSubject = wx.BoxSizer(wx.HORIZONTAL)
        PanelSubjectButton = wx.Panel(PanelSubject, wx.ID_ANY)
        sizerSubjectButton = wx.BoxSizer(wx.VERTICAL)
        self.ButtonSubjectAdd = wx.Button(PanelSubjectButton, wx.ID_ANY,
                                          label='>')
        self.ButtonSubjectRm = wx.Button(PanelSubjectButton, wx.ID_ANY,
                                         label='<')
        sizerSubjectButton.Add(self.ButtonSubjectAdd, 0, wx.EXPAND)
        sizerSubjectButton.Add(self.ButtonSubjectRm, 0, wx.EXPAND)
        self.ButtonSubjectAdd.Enable()
        self.ButtonSubjectRm.Disable()
        PanelSubjectButton.SetSizer(sizerSubjectButton)
        PanelSubjectVariable = wx.Panel(PanelSubject, wx.ID_ANY)
        sizerSubjectVariable = wx.BoxSizer(wx.VERTICAL)
        TextSubject = wx.StaticText(PanelSubjectVariable, wx.ID_ANY,
                                    label="Subject Variable",
                                    style=wx.ALIGN_CENTER)
        sizerSubjectVariable.Add(TextSubject, 0, wx.EXPAND)
        self.SubjectVariable = wx.TextCtrl(PanelSubjectVariable, wx.ID_ANY,
                                           value="", size=(180, 25),
                                           style=wx.TE_READONLY)
        sizerSubjectVariable.Add(self.SubjectVariable, 0, wx.EXPAND)
        PanelSubjectVariable.SetSizer(sizerSubjectVariable)
        sizerSubject.Add(PanelSubjectButton, 0, wx.wx.EXPAND)
        sizerSubject.Add(PanelSubjectVariable, 0, wx.wx.EXPAND)
        PanelSubject.SetSizer(sizerSubject)

        # Within Panel Area
        PanelWithin = wx.Panel(PanelDef, wx.ID_ANY)
        sizerWithin = wx.BoxSizer(wx.HORIZONTAL)
        PanelWithinButton = wx.Panel(PanelWithin, wx.ID_ANY)
        sizerWithinButton = wx.BoxSizer(wx.VERTICAL)
        self.ButtonWithinAdd = wx.Button(PanelWithinButton, wx.ID_ANY,
                                         label='>')
        self.ButtonWithinRm = wx.Button(PanelWithinButton, wx.ID_ANY,
                                        label='<')
        sizerWithinButton.Add(self.ButtonWithinAdd, 0, wx.EXPAND)
        sizerWithinButton.Add(self.ButtonWithinRm, 0, wx.EXPAND)
        self.ButtonWithinAdd.Enable()
        self.ButtonWithinRm.Disable()
        PanelWithinButton.SetSizer(sizerWithinButton)
        PanelWithinVariable = wx.Panel(PanelWithin, wx.ID_ANY)
        sizerWithinVariable = wx.BoxSizer(wx.VERTICAL)
        TextWithin = wx.StaticText(PanelWithinVariable, wx.ID_ANY,
                                   label="Within Subject Factor(s)",
                                   style=wx.ALIGN_CENTER)
        sizerWithinVariable.Add(TextWithin, 0, wx.EXPAND)
        supportext = '(%s)' % ', '.join(FactorWithin.Factor)
        TextSupport = wx.StaticText(PanelWithinVariable, wx.ID_ANY,
                                    label=supportext, style=wx.ALIGN_CENTER)
        sizerWithinVariable.Add(TextSupport, 0, wx.EXPAND)
        iterationFactor = [range(1, e+1) for e in FactorWithin.Level]
        iterList = list(itertools.product(*iterationFactor))
        factorLabels = ['_?_%s' % str(e).replace(' ', '') if len(e) > 1
                        else '_?_(%s)' % str(e[0]) for e in iterList]
        self.ListWithin = wx.ListBox(PanelWithinVariable, wx.ID_ANY,
                                     choices=factorLabels, size=(180, 300),
                                     style=wx.LB_EXTENDED)
        sizerWithinVariable.Add(self.ListWithin, 0, wx.EXPAND)
        PanelWithinVariable.SetSizer(sizerWithinVariable)
        sizerWithin.Add(PanelWithinButton, 0, wx.wx.ALIGN_CENTRE)
        sizerWithin.Add(PanelWithinVariable, 0, wx.wx.ALIGN_RIGHT)
        PanelWithin.SetSizer(sizerWithin)

        # Between Panel Area
        PanelBetween = wx.Panel(PanelDef, wx.ID_ANY)
        sizerBetween = wx.BoxSizer(wx.HORIZONTAL)
        PanelBetweenButton = wx.Panel(PanelBetween, wx.ID_ANY)
        sizerBetweenButton = wx.BoxSizer(wx.VERTICAL)
        self.ButtonBetweenAdd = wx.Button(PanelBetweenButton, wx.ID_ANY,
                                          label='>')
        self.ButtonBetweenRm = wx.Button(PanelBetweenButton, wx.ID_ANY,
                                         label='<')
        sizerBetweenButton.Add(self.ButtonBetweenAdd, 0, wx.EXPAND)
        sizerBetweenButton.Add(self.ButtonBetweenRm, 0, wx.EXPAND)
        self.ButtonBetweenAdd.Enable()
        self.ButtonBetweenRm.Disable()
        PanelBetweenButton.SetSizer(sizerBetweenButton)
        PanelBetweenVariable = wx.Panel(PanelBetween, wx.ID_ANY)
        sizerBetweenVariable = wx.BoxSizer(wx.VERTICAL)
        TextBetween = wx.StaticText(PanelBetweenVariable, wx.ID_ANY,
                                    label="Between Subject Factor(s)",
                                    style=wx.ALIGN_CENTER)
        sizerBetweenVariable.Add(TextBetween, 0, wx.EXPAND)
        self.ListBetween = wx.ListBox(PanelBetweenVariable, wx.ID_ANY,
                                      size=(180, 100), style=wx.LB_EXTENDED)
        sizerBetweenVariable.Add(self.ListBetween, 0, wx.EXPAND)
        PanelBetweenVariable.SetSizer(sizerBetweenVariable)
        sizerBetween.Add(PanelBetweenButton, 0, wx.ALIGN_CENTRE)
        sizerBetween.Add(PanelBetweenVariable, 0, wx.ALIGN_RIGHT)
        PanelBetween.SetSizer(sizerBetween)

        # Covariate Panel Area
        PanelCovariate = wx.Panel(PanelDef, wx.ID_ANY)
        sizerCovariate = wx.BoxSizer(wx.HORIZONTAL)
        PanelCovariateButton = wx.Panel(PanelCovariate, wx.ID_ANY)
        sizerCovariateButton = wx.BoxSizer(wx.VERTICAL)
        self.ButtonCovariateAdd = wx.Button(PanelCovariateButton, wx.ID_ANY,
                                            label='>')
        self.ButtonCovariateRm = wx.Button(PanelCovariateButton, wx.ID_ANY,
                                           label='<')
        sizerCovariateButton.Add(self.ButtonCovariateAdd, 0, wx.EXPAND)
        sizerCovariateButton.Add(self.ButtonCovariateRm, 0, wx.EXPAND)
        self.ButtonCovariateAdd.Enable()
        self.ButtonCovariateRm.Disable()
        PanelCovariateButton.SetSizer(sizerCovariateButton)
        PanelCovariateVariable = wx.Panel(PanelCovariate, wx.ID_ANY)
        sizerCovariateVariable = wx.BoxSizer(wx.VERTICAL)
        TextCovariate = wx.StaticText(PanelCovariateVariable, wx.ID_ANY,
                                      label="Covariate(s)",
                                      style=wx.ALIGN_CENTER)
        sizerCovariateVariable.Add(TextCovariate, 0, wx.EXPAND)
        self.ListCovariate = wx.ListBox(PanelCovariateVariable, wx.ID_ANY,
                                        size=(180, 100), style=wx.LB_EXTENDED)
        sizerCovariateVariable.Add(self.ListCovariate, 0, wx.EXPAND)
        PanelCovariateVariable.SetSizer(sizerCovariateVariable)
        sizerCovariate.Add(PanelCovariateButton, 0, wx.ALIGN_CENTRE)
        sizerCovariate.Add(PanelCovariateVariable, 0, wx.ALIGN_RIGHT)
        PanelCovariate.SetSizer(sizerCovariate)

        # Resize everything and create the input area
        sizerDef.AddSpacer(3)
        sizerDef.Add(PanelSubject, 0, wx.EXPAND)
        sizerDef.AddSpacer(5)
        sizerDef.Add(PanelWithin, 0, wx.EXPAND)
        sizerDef.AddSpacer(5)
        sizerDef.Add(PanelBetween, 0, wx.EXPAND)
        sizerDef.AddSpacer(5)
        sizerDef.Add(PanelCovariate, 0, wx.EXPAND)
        PanelDef.SetSizer(sizerDef)
        sizerInput.Add(PanelDef, 0, wx.EXPAND)
        PanelInput.SetSizer(sizerInput)

        # Panel: OK and previous window Button
        PanelButtons = wx.Panel(self, wx.ID_ANY)
        sizerButtons = wx.BoxSizer(wx.HORIZONTAL)
        ButtonPrevious = wx.Button(PanelButtons, wx.ID_ANY,
                                   label='Change Within Subject Factors')
        sizerButtons.Add(ButtonPrevious, 0, wx.ALIGN_LEFT)
        sizerButtons.AddSpacer(27)
        sizerButtons.AddSpacer(27)
        ButtonOK = wx.Button(PanelButtons, wx.ID_ANY, label='OK')
        sizerButtons.Add(ButtonOK, 0, wx.ALIGN_RIGHT)
        PanelButtons.SetSizer(sizerButtons)

        # Resize everything and create the window
        FrameSizer = wx.BoxSizer(wx.VERTICAL)
        FrameSizer.Add(PanelInput, 0, wx.EXPAND)
        FrameSizer.AddSpacer(5)
        FrameSizer.Add(PanelButtons, 0, wx.EXPAND)
        FrameSizer.AddSpacer(3)
        self.SetSizerAndFit(FrameSizer)

        # Specification of events
        wx.EVT_BUTTON(self, self.ButtonSubjectAdd.Id, self.addSubject)
        wx.EVT_BUTTON(self, self.ButtonSubjectRm.Id, self.rmSubject)
        wx.EVT_BUTTON(self, self.ButtonWithinAdd.Id, self.addWithin)
        wx.EVT_BUTTON(self, self.ButtonWithinRm.Id, self.rmWithin)
        wx.EVT_BUTTON(self, self.ButtonBetweenAdd.Id, self.addBetween)
        wx.EVT_BUTTON(self, self.ButtonBetweenRm.Id, self.rmBetween)
        wx.EVT_BUTTON(self, self.ButtonCovariateAdd.Id, self.addCovariate)
        wx.EVT_BUTTON(self, self.ButtonCovariateRm.Id, self.rmCovariate)
        wx.EVT_BUTTON(self, ButtonOK.Id, self.Ok)
        wx.EVT_BUTTON(self, ButtonPrevious.Id, self.onClose)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        wx.EVT_LISTBOX(self, self.ListInput.Id, self.ColSelected)
        wx.EVT_LISTBOX(self, self.ListWithin.Id, self.WithinSelected)
        wx.EVT_LISTBOX(self, self.ListBetween.Id, self.BetweenSelected)
        wx.EVT_LISTBOX(self, self.ListCovariate.Id, self.CovariateSelected)

    def onClose(self, event):
        """Show previous window and close current one"""
        self.FactorWithin.Show(True)
        self.Show(False)

    def showMessage(self, title, message):
        """Shows Warning Popup Window"""
        dlg = wx.MessageDialog(self, style=wx.OK,
                               caption=title, message=message)
        dlg.ShowModal()
        dlg.Destroy()

    def addSubject(self, event):
        """Add selected factor to subject variable"""
        idx = self.ListInput.GetSelections()
        items = self.ListInput.GetItems()

        # Make sure that only one element is selected
        if len(idx) != 1:
            self.showMessage(
                title='Subject Variable',
                message='Only select one element as subject variable.')
        else:
            subjectVariable = items.pop(idx[0])
            self.SubjectVariable.SetValue(subjectVariable)
            self.ListInput.SetItems(items)
            self.Subject = subjectVariable
            self.SubjectId = idx[0]

            # Change GUI layout
            self.ButtonSubjectAdd.Disable()
            self.ButtonSubjectRm.Enable()

    def rmSubject(self, event):
        """Remove selected factor from subject variable"""
        items = self.ListInput.GetItems()
        subjectVariable = self.SubjectVariable.GetValue()

        items.insert(self.SubjectId, subjectVariable)
        self.ListInput.SetItems(items)
        self.Subject = ''
        self.SubjectVariable.SetValue('')

        # Change GUI layout
        self.ButtonSubjectAdd.Enable()
        self.ButtonSubjectRm.Disable()

    def addWithin(self, event):
        """Add selected factor to within subject factors"""
        idx = self.ListInput.GetSelections()
        items = self.ListInput.GetItems()
        factors = self.ListWithin.GetItems()
        numberOfFactors = len(factors)

        # Make sure that not too many elements were selected
        if len(idx) > numberOfFactors:
            self.showMessage(
                title='To many factors selected',
                message='The number of selected elements exceeds ' +
                        'the number of possible within subject factors.')
        # Make sure that the list is not already to full
        elif len(self.Within) + len(idx) > numberOfFactors:
            self.showMessage(
                title='Within Subject Factor Full',
                message='Within subject factor is full.')
        else:
            for j, f in enumerate(factors):
                if '_?_' in f:

                    i = idx[0]
                    idx = idx[1:len(idx)]

                    factors[j] = f.replace('_?_', items[i])
                    self.Within.append(items[i])
                    self.WithinIndex.append(i)

                    items[i] = ''

                    if idx == ():
                        break

            while '' in items:
                items.remove('')

            self.ListInput.SetItems(items)
            self.ListWithin.SetItems(factors)

    def rmWithin(self, event):
        """Remove selected factors from within subject factors"""
        idx = self.ListWithin.GetSelections()
        factors = self.ListWithin.GetItems()
        items = self.ListInput.GetItems()

        for i in idx:
            if '_?_' not in factors[i]:
                splitterId = factors[i].find('(')
                factorName = factors[i][0:splitterId]
                factorLevel = factors[i][splitterId:]

                popId = self.Within.index(factorName)
                self.Within.pop(popId)
                oldId = self.WithinIndex.pop(popId)

                # Update ListInput
                items.insert(oldId, factorName)

                # Update ListWithin
                factors[i] = '_?_%s' % factorLevel

        self.ListInput.SetItems(items)
        self.ListWithin.SetItems(factors)

    def addBetween(self, event):
        ColNumber = self.ListInput.GetSelections()
        ColName = self.ListInput.GetItems()
        name = self.ListBetween.GetItems()
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
        self.ListInput.SetItems(ColNameNew)
        self.ListBetween.SetItems(name)

    def rmBetween(self, event):
        Selections = self.ListBetween.GetSelections()
        name = self.ListBetween.GetItems()
        ColName = self.ListInput.GetItems()
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
        self.ListInput.SetItems(ColNameNew)
        self.ListBetween.SetItems(NameNew)

    def addCovariate(self, event):
        ColNumber = self.ListInput.GetSelections()
        ColName = self.ListInput.GetItems()
        name = self.ListCovariate.GetItems()
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

        self.ListInput.SetItems(ColNameNew)
        self.ListCovariate.SetItems(name)

    def rmCovariate(self, event):
        Selections = self.ListCovariate.GetSelections()
        name = self.ListCovariate.GetItems()
        ColName = self.ListInput.GetItems()
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
        self.ListInput.SetItems(ColNameNew)
        self.ListCovariate.SetItems(NameNew)

    def ColSelected(self, event):
        self.ButtonWithinAdd.Enable()
        self.ButtonBetweenAdd.Enable()
        self.ButtonCovariateAdd.Enable()
        self.ButtonWithinRm.Disable()
        self.ButtonBetweenRm.Disable()
        self.ButtonCovariateRm.Disable()
        if self.SubjectVariable.GetValue() == '':
            self.ButtonSubjectRm.Disable()
            self.ButtonSubjectAdd.Enable()
        else:
            self.ButtonSubjectRm.Enable()
            self.ButtonSubjectAdd.Disable()

    def WithinSelected(self, event):
        self.ButtonSubjectAdd.Disable()
        self.ButtonWithinAdd.Disable()
        self.ButtonBetweenAdd.Disable()
        self.ButtonCovariateAdd.Disable()
        self.ButtonSubjectRm.Disable()
        self.ButtonWithinRm.Enable()
        self.ButtonBetweenRm.Disable()
        self.ButtonCovariateRm.Disable()

    def BetweenSelected(self, event):
        self.ButtonSubjectAdd.Disable()
        self.ButtonWithinAdd.Disable()
        self.ButtonBetweenAdd.Disable()
        self.ButtonCovariateAdd.Disable()
        self.ButtonSubjectRm.Disable()
        self.ButtonWithinRm.Disable()
        self.ButtonBetweenRm.Enable()
        self.ButtonCovariateRm.Disable()

    def CovariateSelected(self, event):
        self.ButtonSubjectAdd.Disable()
        self.ButtonWithinAdd.Disable()
        self.ButtonBetweenAdd.Disable()
        self.ButtonCovariateAdd.Disable()
        self.ButtonSubjectRm.Disable()
        self.ButtonWithinRm.Disable()
        self.ButtonBetweenRm.Disable()
        self.ButtonCovariateRm.Enable()





    def Ok(self, event):
        self.DataEntry.ColFactor = self.ListWithin.GetItems()
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