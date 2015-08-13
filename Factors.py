import wx
import os
import itertools


class WithinFactor(wx.Frame):

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
        self.ButtonAdd = wx.Button(PanelButton, wx.ID_ANY, label="&Add")
        sizerButton.Add(self.ButtonAdd, 0, wx.EXPAND)
        self.ButtonDelete = wx.Button(PanelButton, wx.ID_ANY, label="&Delete")
        self.ButtonDelete.Disable()
        sizerButton.Add(self.ButtonDelete, 0, wx.EXPAND)
        self.ButtonChange = wx.Button(PanelButton, wx.ID_ANY, label="Chan&ge")
        self.ButtonChange.Disable()
        sizerButton.Add(self.ButtonChange, 0, wx.EXPAND)
        sizerButton.AddSpacer(30)
        self.ButtonContinue = wx.Button(PanelButton, wx.ID_ANY,
                                        label="&Continue")
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
        self.Bind(wx.EVT_CHAR_HOOK, self.onKeyDown)

        # Update List with previous elements if window was already opened
        if self.Factor != []:
            self.updateList()

        # Fill in table if dataset already exists
        if self.DataPanel.MainFrame.Dataset != {}:
            self.loadDataset()

    def onKeyDown(self, event):
        """Key event handler if key is pressed within frame"""
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_ESCAPE:  # If ESC is pressed
            self.DataPanel.Show(True)
            self.Show(False)
        else:
            event.Skip()

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
        event.Skip()

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
        event.Skip()

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
            self.FactorName.SetValue(self.Factor[idx - 1])
            self.NumLevel.SetValue(unicode(self.Level[idx - 1]))
            self.ListFactor.SetSelection(idx - 1)
        event.Skip()

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
        event.Skip()

    def showMessage(self, title, message):
        """Shows Warning Popup Window"""
        dlg = wx.MessageDialog(self, style=wx.OK,
                               caption=title, message=message)
        dlg.ShowModal()
        dlg.Destroy()
        event.Skip()

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
        event.Skip()
        return inputIsValid

    def loadDataset(self):
        """Loads the dataset under Mainframe.Dataset if it already exists"""
        factors = self.DataPanel.MainFrame.Dataset['Factors']
        Factors = []
        for i in range(len(factors[0])):
            newFactor = '%s(%s)' % (factors[0][i], factors[1][i])
            Factors.append(newFactor)
        self.Factor = factors[0]
        self.Level = factors[1]
        self.ListFactor.SetItems(Factors)
        self.ButtonContinue.Enable()

    def defineFactor(self, event):
        """Move on to the Factor Definition window"""
        self.ModelFull = FactorDefinition(self.Sheet, self)
        self.ModelFull.Show(True)
        self.Show(False)

        # If something was changed, drop MainFrame.Ddataset
        if self.DataPanel.MainFrame.Dataset != {}:
            oldFactors = self.DataPanel.MainFrame.Dataset['Factors']
            newFactor = self.Factor
            newLevel = self.Level
            if oldFactors[0] != newFactor or oldFactors[0] != newLevel:
                self.DataPanel.MainFrame.Dataset = {}
        event.Skip()


class FactorDefinition(wx.Frame):

    """TODO: Better description, perhaps also another name for window?
    Window to specify the factors"""

    def __init__(self, Sheet, WithinFactor):
        wx.Frame.__init__(self, None, wx.ID_ANY, size=(200, 250),
                          title="Factor definition")

        # Specify relevant variables
        self.WithinFactor = WithinFactor
        self.LabelNames = WithinFactor.dataTable['labels']
        self.Subject = ''

        # Panel: Left Input Area
        PanelInput = wx.Panel(self, wx.ID_ANY)
        sizerInput = wx.BoxSizer(wx.HORIZONTAL)
        self.ListInput = wx.ListBox(PanelInput, wx.ID_ANY,
                                    choices=self.LabelNames,
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
        supportext = '(%s)' % ', '.join(WithinFactor.Factor)
        TextSupport = wx.StaticText(PanelWithinVariable, wx.ID_ANY,
                                    label=supportext, style=wx.ALIGN_CENTER)
        sizerWithinVariable.Add(TextSupport, 0, wx.EXPAND)
        iterationFactor = [range(1, e + 1) for e in WithinFactor.Level]
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
        ButtonOK = wx.Button(PanelButtons, wx.ID_ANY, label='&OK')
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
        self.Bind(wx.EVT_CLOSE, self.onClose)
        wx.EVT_BUTTON(self, self.ButtonSubjectAdd.Id, self.addSubject)
        wx.EVT_BUTTON(self, self.ButtonSubjectRm.Id, self.rmSubject)
        wx.EVT_BUTTON(self, self.ButtonWithinAdd.Id, self.addWithin)
        wx.EVT_BUTTON(self, self.ButtonWithinRm.Id, self.rmWithin)
        wx.EVT_BUTTON(self, self.ButtonBetweenAdd.Id, self.addBetween)
        wx.EVT_BUTTON(self, self.ButtonBetweenRm.Id, self.rmBetween)
        wx.EVT_BUTTON(self, self.ButtonCovariateAdd.Id, self.addCovariate)
        wx.EVT_BUTTON(self, self.ButtonCovariateRm.Id, self.rmCovariate)
        wx.EVT_BUTTON(self, ButtonPrevious.Id, self.onClose)
        wx.EVT_BUTTON(self, ButtonOK.Id, self.finishFactors)
        wx.EVT_LISTBOX(self, self.ListInput.Id, self.inputListSelected)
        wx.EVT_LISTBOX(self, self.ListWithin.Id, self.withinListSelected)
        wx.EVT_LISTBOX(self, self.ListBetween.Id, self.betweenListSelected)
        wx.EVT_LISTBOX(self, self.ListCovariate.Id, self.covariateListSelected)
        self.Bind(wx.EVT_CHAR_HOOK, self.onKeyDown)

        # Fill in table if dataset already exists
        if self.WithinFactor.DataPanel.MainFrame.Dataset != {}:
            self.loadDataset()

    def onKeyDown(self, event):
        """Key event handler if key is pressed within frame"""
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_ESCAPE:  # If ESC is pressed
            self.onClose(event)
        else:
            event.Skip()

    def onClose(self, event):
        """Show previous window and close current one"""
        self.WithinFactor.Show(True)
        self.Show(False)

    def showMessage(self, title, message):
        """Shows Warning Popup Window"""
        dlg = wx.MessageDialog(self, style=wx.OK,
                               caption=title, message=message)
        dlg.ShowModal()
        dlg.Destroy()
        event.Skip()

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
        event.Skip()

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
        event.Skip()

    def addWithin(self, event):
        """Add selected factor to within subject factors"""
        idx = self.ListInput.GetSelections()
        items = self.ListInput.GetItems()
        factors = self.ListWithin.GetItems()
        numberOfFactors = len(factors)
        emptyFactorsLeft = sum([1 for e in factors if '_?_' in e])

        # Make sure that something is selected
        if len(idx) == 0:
            self.showMessage(
                title='No Within Factor Selected',
                message='Please select a Within Factor to add to the list.')
        # Make sure that not too many elements were selected
        elif len(idx) > numberOfFactors:
            self.showMessage(
                title='To many factors selected',
                message='The number of selected elements exceeds ' +
                        'the number of possible within subject factors.')
        # Make sure that the list is not already to full
        elif emptyFactorsLeft < len(idx):
            self.showMessage(
                title='Within Subject Factor Full',
                message='Within subject factor is full.')
        else:
            # Go through the list of '_?_' and fill in a slected factor
            for j, f in enumerate(factors):
                if '_?_' in f:
                    i = idx[0]
                    idx = idx[1:len(idx)]
                    factors[j] = f.replace('_?_', items[i])
                    items[i] = ''
                    if idx == ():
                        break
            while '' in items:
                items.remove('')

            self.ListInput.SetItems(items)
            self.ListWithin.SetItems(factors)
        event.Skip()

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

                # Reset the Within List
                factors[i] = '_?_%s' % factorLevel

                # Reset the Input List
                items.append(factorName)

        items = [e for e in self.LabelNames if e in items]

        self.ListInput.SetItems(items)
        self.ListWithin.SetItems(factors)
        event.Skip()

    def addBetween(self, event):
        """Add selected factor to between subject factors"""
        idx = self.ListInput.GetSelections()
        items = self.ListInput.GetItems()
        factors = self.ListBetween.GetItems()

        # Make sure that something is selected
        if len(idx) == 0:
            self.showMessage(
                title='No Between Factor Selected',
                message='Please select a Between Factor to add to the list.')
        else:
            # Add selected factors to the list
            for i in idx:
                factors.append(items[i])
                items[i] = ''
            while '' in items:
                items.remove('')
            self.ListInput.SetItems(items)
            self.ListBetween.SetItems(factors)
        event.Skip()

    def rmBetween(self, event):
        """Remove selected factor from the between subject factors"""
        idx = self.ListBetween.GetSelections()
        factors = self.ListBetween.GetItems()
        items = self.ListInput.GetItems()

        for i in idx:
            factorName = factors[i]
            items.append(factorName)
            factors[i] = ''
        while '' in factors:
            factors.remove('')

        items = [e for e in self.LabelNames if e in items]

        self.ListInput.SetItems(items)
        self.ListBetween.SetItems(factors)
        event.Skip()

    def addCovariate(self, event):
        """Add selected factor to covariate subject factors"""
        idx = self.ListInput.GetSelections()
        items = self.ListInput.GetItems()
        factors = self.ListCovariate.GetItems()

        # Make sure that something is selected
        if len(idx) == 0:
            self.showMessage(
                title='No Covariate Factor Selected',
                message='Please select a Covariate Factor to add to the list.')
        else:
            # Add selected factors to the list
            for i in idx:
                factors.append(items[i])
                items[i] = ''
            while '' in items:
                items.remove('')
            self.ListInput.SetItems(items)
            self.ListCovariate.SetItems(factors)
        event.Skip()

    def rmCovariate(self, event):
        """Remove selected factor from the covariate subject factors"""
        idx = self.ListCovariate.GetSelections()
        factors = self.ListCovariate.GetItems()
        items = self.ListInput.GetItems()

        for i in idx:
            factorName = factors[i]
            items.append(factorName)
            factors[i] = ''
        while '' in factors:
            factors.remove('')

        items = [e for e in self.LabelNames if e in items]

        self.ListInput.SetItems(items)
        self.ListCovariate.SetItems(factors)
        event.Skip()

    def inputListSelected(self, event):
        """GUI reconfiguration if Input list is selected"""
        self.ButtonBetweenAdd.Enable()
        self.ButtonBetweenRm.Disable()
        self.ButtonCovariateAdd.Enable()
        self.ButtonCovariateRm.Disable()
        self.ButtonWithinAdd.Enable()
        self.ButtonWithinRm.Disable()
        if self.SubjectVariable.GetValue() == '':
            self.ButtonSubjectAdd.Enable()
            self.ButtonSubjectRm.Disable()
        else:
            self.ButtonSubjectAdd.Disable()
            self.ButtonSubjectRm.Enable()
        event.Skip()

    def withinListSelected(self, event):
        """GUI reconfiguration if Within list is selected"""
        self.ButtonBetweenAdd.Disable()
        self.ButtonBetweenRm.Disable()
        self.ButtonCovariateAdd.Disable()
        self.ButtonCovariateRm.Disable()
        self.ButtonWithinAdd.Disable()
        self.ButtonWithinRm.Enable()
        event.Skip()

    def betweenListSelected(self, event):
        """GUI reconfiguration if Between list is selected"""
        self.ButtonBetweenAdd.Disable()
        self.ButtonBetweenRm.Enable()
        self.ButtonCovariateAdd.Disable()
        self.ButtonCovariateRm.Disable()
        self.ButtonWithinAdd.Disable()
        self.ButtonWithinRm.Disable()
        event.Skip()

    def covariateListSelected(self, event):
        """GUI reconfiguration if Input Covariate is selected"""
        self.ButtonBetweenAdd.Disable()
        self.ButtonBetweenRm.Disable()
        self.ButtonCovariateAdd.Disable()
        self.ButtonCovariateRm.Enable()
        self.ButtonWithinAdd.Disable()
        self.ButtonWithinRm.Disable()
        event.Skip()

    def checkInput(self):
        """Checks if a factor input is valid or not"""
        subjectVariable = self.SubjectVariable.GetValue()
        withinList = self.ListWithin.GetItems()
        betweenList = self.ListBetween.GetItems()
        covariates = self.ListCovariate.GetItems()
        dataTable = self.WithinFactor.dataTable

        # Check Subject Variable
        if subjectVariable == u'':
            self.showMessage(
                title='Subject Variable not specified',
                message='Please specify Subject Variable to continue.')
            return False
        subjectId = dataTable['labels'].index(subjectVariable)
        subjectList = dataTable['content'][subjectId]
        for e in subjectList:
            if not e.isdigit() or int(e) < 0:
                self.showMessage(
                    title='Subject List not valid',
                    message='Not all values in the Subject List are ' +
                            'positive integers.')
                return False

        # Check Within Subject Factors
        notSpecified = sum([1 for e in withinList if '_?_' in e])
        if notSpecified != 0:
            self.showMessage(
                title='Within Subject Factor not filled out',
                message='Not all Within Subject Factors are specified.')
            return False
        for factor in withinList:
            splitterId = factor.find('(')
            factorName = factor[0:splitterId]
            listId = dataTable['labels'].index(factorName)
            factorList = dataTable['content'][listId]
            for f in factorList:
                if not os.path.isfile(f):
                    self.showMessage(
                        title='Within Subject Factor not valid',
                        message='Each Within Subject Factor has to consist ' +
                                'of valid file paths.\n ' +
                                'Factor "%s" is not valid.' % factorName)
                    return False

        # Check Between Factors
        if betweenList != []:
            for factor in betweenList:
                betweenId = dataTable['labels'].index(factor)
                betweenList = dataTable['content'][betweenId]
                for e in betweenList:
                    if not e.isdigit() or int(e) < 0:
                        self.showMessage(
                            title='Between Factor not valid',
                            message='Not all values in the Between Factor ' +
                                    '"%s" are positive integers.' % factor)
                        return False

        # Check Covariate
        if covariates != []:
            for factor in covariates:
                covariateId = dataTable['labels'].index(factor)
                covariateList = dataTable['content'][covariateId]
                for e in covariateList:
                    try:
                        float(e)
                    except:
                        self.showMessage(
                            title='Covariate not valid',
                            message='Not all values in the Covariate ' +
                                    '"%s" are float numbers.' % factor)
                        return False

        # If all inputs are valid, return True
        return True

    def loadDataset(self):
        """Loads the dataset under Mainframe.Dataset if it already exists"""
        dataset = self.WithinFactor.DataPanel.MainFrame.Dataset

        # Collect the variables to write
        subjectVariable = dataset['Subject'][0]
        listWithin = [e[0] + e[1] for e in dataset['WithinFactor']]
        listWithinLabels = [e[0] for e in dataset['WithinFactor']]
        listBetween = [e[0] for e in dataset['BetweenFactor']]
        listCovariate = [e[0] for e in dataset['Covariate']]
        listInput = dataset['Table']['labels']
        listInput = [e for e in listInput if e not in subjectVariable]
        listInput = [e for e in listInput if e not in listWithinLabels]
        listInput = [e for e in listInput if e not in listBetween]
        listInput = [e for e in listInput if e not in listCovariate]

        # Write all values in specific cells
        self.ListInput.SetItems(listInput)
        self.SubjectVariable.SetValue(subjectVariable)
        self.ListWithin.SetItems(listWithin)
        self.ListBetween.SetItems(listBetween)
        self.ListCovariate.SetItems(listCovariate)

    def finishFactors(self, event):
        """
        Finishes Factor Definition window and opens MainFrame again.
        All relevant values are stored under MainFrame.Dataset.
        """

        # Check if input factors are valid
        inputIsValid = self.checkInput()
        if inputIsValid:

            # Create output dataset
            self.Dataset = {}

            # Collect the Data Table
            dataTable = self.WithinFactor.dataTable
            self.Dataset['Table'] = dataTable

            # Collect Subject Variable
            subjectVariable = self.SubjectVariable.GetValue()
            subjectListId = dataTable['labels'].index(subjectVariable)
            self.Dataset['Subject'] = [
                subjectVariable,
                map(int, dataTable['content'][subjectListId])]

            # Collect Within Subject Factor(s)
            withinListLabels = [e[0:e.find('(')]
                                for e in self.ListWithin.GetItems()]
            withinListLevel = [e[e.find('('):]
                               for e in self.ListWithin.GetItems()]
            withinListIdx = [dataTable['labels'].index(i)
                             for i in withinListLabels]
            withinListTable = [dataTable['content'][l] for l in withinListIdx]
            self.Dataset['WithinFactor'] = zip(withinListLabels,
                                               withinListLevel,
                                               withinListTable)

            # Collect Between Subject Factor(s)
            betweenListLabels = self.ListBetween.GetItems()
            betweenListIdx = [dataTable['labels'].index(i)
                              for i in betweenListLabels]
            betweenListTable = [map(int, dataTable['content'][l])
                                for l in betweenListIdx]
            self.Dataset['BetweenFactor'] = zip(betweenListLabels,
                                                betweenListTable)

            # Collect Covariate(s)
            covariateLabels = self.ListCovariate.GetItems()
            covariateIdx = [dataTable['labels'].index(i)
                            for i in covariateLabels]
            covariateTable = [map(float, dataTable['content'][l])
                              for l in covariateIdx]
            self.Dataset['Covariate'] = zip(covariateLabels, covariateTable)

            # Collect within Factor names and levels
            self.Dataset['Factors'] = [self.WithinFactor.Factor,
                                       self.WithinFactor.Level]

            # Close Factor Within window
            self.Show(False)
            self.WithinFactor.DataPanel.Show(False)
            self.WithinFactor.DataPanel.MainFrame.Show(True)
            self.WithinFactor.DataPanel.MainFrame.Dataset = self.Dataset
            self.WithinFactor.DataPanel.MainFrame.ButtonDataModify.Enable()
            self.WithinFactor.DataPanel.MainFrame.ButtonDataSave.Enable()
            event.Skip()
