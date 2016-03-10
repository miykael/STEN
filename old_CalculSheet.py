import wx.lib.sheet as sheet


class CalculSheet(sheet.CSheet):

    def __init__(self, parent, size=(2, 2)):
        sheet.CSheet.__init__(self, parent)
        self.SetNumberRows(30)
        self.SetNumberCols(9)
        self.SetColLabelValue(0, 'subject')


class CalculSheetCov(sheet.CSheet):

    def __init__(self, l):
        sheet.CSheet.__init__(self)
        self.SetNumberRows(40)
        self.SetNumberCols(9)
        self.SetColLabelValue(0, 'subject')
