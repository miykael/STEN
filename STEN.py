import wx
import Interface

"""
Start STEN and open the GUI
"""


class StartSTEN(wx.App):

    """Calls STEN Splash Screen"""

    def OnInit(self):
        STENSplash = STENSplashScreen()
        STENSplash.Show()
        return True


class STENSplashScreen(wx.SplashScreen):

    """Opens STEN Splash Screen and after exit starts STEN"""

    def __init__(self, parent=None):
        aBitmap = wx.Image(name="STEN_logo.png").ConvertToBitmap()
        splashStyle = wx.SPLASH_CENTRE_ON_SCREEN | wx.SPLASH_TIMEOUT
        splashDuration = 1000
        wx.SplashScreen.__init__(self, aBitmap, splashStyle,
                                 splashDuration, parent)
        self.Bind(wx.EVT_CLOSE, self.OnExit)
        wx.Yield()

    def OnExit(self, event):
        self.Hide()
        MyFrame = Interface.MainFrame()
        app.SetTopWindow(MyFrame)
        MyFrame.Show(True)
        event.Skip()

# Opens the GUI if script is run directly
if __name__ == "__main__":
    app = StartSTEN()
    app.MainLoop()


# TODO: For More Logo's Check
# Logo Maker - http://logotypemaker.com/logo-maker
# Design Mantic - www.designmantic.com/logo-design/samples
