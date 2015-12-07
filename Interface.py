import wx
import PanelData
import PanelAnalysis
import Calculation_new


class MainFrame(wx.Frame):

    """
    Initiation of MainFrame with PanelData, PanelOption and ButtonStart
    """

    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, title="STEN 1.0",
                          pos=(0, 0), size=(1000, 500))

        # Panel: MainFrame
        self.panel = wx.Panel(self, wx.ID_ANY)

        # Specify BoxSizer
        sizerMainV = wx.BoxSizer(wx.VERTICAL)
        sizerMainH = wx.BoxSizer(wx.HORIZONTAL)
        sizerStart = wx.BoxSizer(wx.HORIZONTAL)

        # Panel: Data
        self.PanelData = PanelData.CreateDataset(self.panel, self)
        sizerMainH.Add(self.PanelData, 1, wx.EXPAND)

        # Panel: Option
        self.PanelOption = wx.Notebook(self.panel, 1, style=wx.NB_TOP)
        self.AnovaWave = PanelAnalysis.AnovaWave(self.PanelOption, self)
        self.AnovaIS = PanelAnalysis.AnovaIS(self.PanelOption, self)
        self.PanelOption.AddPage(self.AnovaWave, 'ANOVA on Wave/GFP')
        self.PanelOption.AddPage(self.AnovaIS, 'ANOVA in Brain Space')
        self.AnovaWave.SetFocus()
        sizerMainH.Add(self.PanelOption, 1, wx.EXPAND)
        self.panel.SetSizer(sizerMainH)
        sizerMainV.Add(self.panel, 1, wx.EXPAND)

        # Button: Start
        PanelStart = wx.Panel(self, wx.ID_ANY)
        self.ButtonStart = wx.Button(PanelStart, wx.ID_ANY,
                                     label="Start Calculation")
        sizerStart.Add(self.ButtonStart, wx.ID_ANY, wx.EXPAND)
        PanelStart.SetSizer(sizerStart)
        sizerMainV.Add(PanelStart, 0, wx.EXPAND)
        self.SetSizerAndFit(sizerMainV)
        self.Show(True)

        # Specification of events
        self.Bind(wx.EVT_CLOSE, self.onClose)
        wx.EVT_BUTTON(self, self.ButtonStart.Id, self.startAction)
        self.Bind(wx.EVT_CHAR_HOOK, self.onKeyDown)
        self.PanelData.SetFocus()

        # MenuBar
        menuBar = wx.MenuBar()
        menu = wx.Menu()
        m_exit = menu.Append(wx.ID_EXIT, "E&xit\tAlt-X",
                             "Close window and exit program.")
        self.Bind(wx.EVT_MENU, self.onClose, m_exit)
        menuBar.Append(menu, "&File")
        menu = wx.Menu()
        m_about = menu.Append(wx.ID_ABOUT, "&About", "Information about STEN")
        self.Bind(wx.EVT_MENU, self.onAbout, m_about)
        menuBar.Append(menu, "&Help")
        self.SetMenuBar(menuBar)

    def onKeyDown(self, event):
        """Key event handler if key is pressed within frame"""
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_ESCAPE:  # If ESC is pressed
            self.onClose(event)
        else:
            event.Skip()

    def onAbout(self, event):
        """Show about message when About Menu opened"""
        dlg = wx.MessageDialog(
            self,
            "For more Information about STEN, go to " +
            "https://github.com/jknebel/STEN",
            "About STEN", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()
        event.Skip()

    def onClose(self, event):
        """Show exit message when MainFrame gets closed"""
        dlg = wx.MessageDialog(
            self, "Do you really want to close STEN?", "Exit STEN",
            wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        answer = dlg.ShowModal()
        dlg.Destroy()
        if answer == wx.ID_OK:
            self.DestroyChildren()
            self.Destroy()
        event.Skip()

    def startAction(self, event):
        """Starts the calculation"""
        # Make sure that a dataset is present and saved before continuing
        startCalculation = False
        if self.Dataset == {}:
            dlg = wx.MessageDialog(
                self, caption='No dataset loaded',
                message='No dataset is loaded. Create a new dataset or load ' +
                        'an already existing one to continue.',
                style=wx.OK | wx.ICON_QUESTION)
            dlg.ShowModal()
            dlg.Destroy()
        elif self.PanelData.TextResult.GetValue() == '':
            dlg = wx.MessageDialog(
                self, caption='No result folder selected',
                message='Results folder was not indicated. Please specify ' +
                        'where the results of the computation should be ' +
                        'stored at.',
                style=wx.OK | wx.ICON_QUESTION)
            dlg.ShowModal()
            dlg.Destroy()
            self.PanelData.resultFolder(event)
        elif self.Dataset != {} and not self.saved:
            dlg = wx.MessageDialog(
                self, caption='Unsaved Dataset',
                message='Are you sure that you want to continue ' +
                        'without saving the loaded dataset first?',
                style=wx.OK | wx.CANCEL | wx.ICON_QUESTION)
            answer = dlg.ShowModal()
            dlg.Destroy()
            if answer == wx.ID_OK:
                startCalculation = True
        else:
            startCalculation = True

        # Start Calculation
        if startCalculation:
            self.ButtonStart.Disable()
            calc = Calculation_new.Start(self)
            self.PanelData.TxtProgress.SetLabel('\n'.join(calc.ProgressTxt))
            self.ButtonStart.Enable()
        event.Skip()
