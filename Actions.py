import wx
import wx.lib.sheet as sheet
import numpy as np
import os
import tables
import Stat
from EntryPanel import DataEntry
from FactorDefinition import FactorDef


class GridFileDropTarget(wx.FileDropTarget):

    def __init__(self, grid):
        wx.FileDropTarget.__init__(self)
        self.grid = grid

    def OnDropFiles(self, x, y, filenames):
        row, col = self.grid.XYToCell(x, y)
        for f in filenames:

            if row > -1 and col > -1:
                self.grid.SetCellValue(row, col, f)
                self.grid.Refresh()
                row += 1
