import wx
import PanelAnalysis
import PanelData
from Calculation import startCalculation


class MainFrame(wx.Frame):

    """
    Initiation of MainFrame with PanelData, PanelOption and ButtonStart
    """

    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, title="STEN 1.0",
                          size=(1000, 500))

        # MainFrame panel
        self.panel = wx.Panel(self, wx.ID_ANY)

        # Specify BoxSizer
        mainSizerV = wx.BoxSizer(wx.VERTICAL)
        mainSizerH = wx.BoxSizer(wx.HORIZONTAL)
        startSizer = wx.BoxSizer(wx.HORIZONTAL)

        # Data Panel
        self.PanelData = PanelData.OnOpen(self.panel, self)
        mainSizerH.Add(self.PanelData, 1, wx.EXPAND)

        # Option Panel
        self.PanelOption = wx.Notebook(self.panel, 1, style=wx.NB_TOP)
        self.AnovaWave = PanelAnalysis.PanelAnovaWave(self.PanelOption)
        self.AnovaIS = PanelAnalysis.PanelAnovaIS(self.PanelOption)
        self.PanelOption.AddPage(self.AnovaWave, 'ANOVA on Wave/GFP')
        self.PanelOption.AddPage(self.AnovaIS, 'ANOVA on Brain Space')
        self.AnovaWave.SetFocus()
        mainSizerH.Add(self.PanelOption, 1, wx.EXPAND)
        self.panel.SetSizer(mainSizerH)
        mainSizerV.Add(self.panel, 1, wx.EXPAND)

        # Start button
        PanelStart = wx.Panel(self, wx.ID_ANY)
        self.ButtonStart = wx.Button(PanelStart, wx.ID_ANY,
                                     label="Start Calculation")
        startSizer.Add(self.ButtonStart, wx.ID_ANY, wx.EXPAND)
        PanelStart.SetSizer(startSizer)
        mainSizerV.Add(PanelStart, 0, wx.EXPAND)
        self.SetSizerAndFit(mainSizerV)
        self.Show(True)
        wx.EVT_BUTTON(self, self.ButtonStart.Id, self.startAction)

        # Execute when STEN gets closed
        self.Bind(wx.EVT_CLOSE, self.onClose)

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

    def onAbout(self, event):
        """Show about message when About Menu opened"""
        dlg = wx.MessageDialog(
            self,
            "For more Information about STEN, go to " +
            "https://github.com/jknebel/STEN",
            "About STEN", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def onClose(self, event):
        """Show exit message when MainFrame gets closed"""
        dlg = wx.MessageDialog(
            self, "Do you really want to close STEN?", "Exit STEN",
            wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        answer = dlg.ShowModal()
        dlg.Destroy()
        if answer == wx.ID_OK:
            self.Destroy()

    def startAction(self, event):
        """Starts the calculation"""
        startCalculation(self)
