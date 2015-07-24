import wx
from Interface import MainFrame

"""
Start STEN and open the GUI
"""


class STEN(wx.App):

    def OnInit(self):
        fen = MainFrame()
        fen.Show(True)
        self.SetTopWindow(fen)
        return True

# Opens the GUI if script is run directly
if __name__ == "__main__":
    app = STEN()
    app.MainLoop()
