import wx
import numpy as np
import glob as ls
import os
import tables
from Actions import GridFileDropTarget
from ReadFiles import ReadSheet
from FactorWithin import FactorWithin
from DataProcessing import DataProcessing
from Information import ReturnInfomation


class DataEntry(wx.Frame):

    """ TODO: translate to english
    feuille de clacul sytle SPSS
    """

    def __init__(self, Parent):

        # Create data table window
        wx.Frame.__init__(self, None, wx.ID_ANY, title="Data Entry",
                          style=wx.DEFAULT_FRAME_STYLE | wx.RESIZE_BORDER)

        # Panel: Data Entry
        PanelDataEntry = wx.Panel(self, wx.ID_ANY)
        sizerPanelDataEntry = wx.BoxSizer(wx.HORIZONTAL)

        # Panel: Data Sheet (XLS-style)
        PanelSheet = wx.Panel(PanelDataEntry, wx.ID_ANY)
        sizerPanelSheet = wx.BoxSizer(wx.VERTICAL)
        sizerPanelSheet.AddSpacer(10)

        # Panel: Cell content field at top of data sheet
        PanelCellContent = wx.Panel(PanelSheet, wx.ID_ANY)
        sizerPanelCellContent = wx.BoxSizer(wx.HORIZONTAL)
        sizerPanelCellContent.AddSpacer(10)
        CellTxt = wx.StaticText(
            PanelCellContent, wx.ID_ANY, label='Cell Content: ',
            style=wx.ALIGN_LEFT)
        sizerPanelCellContent.Add(CellTxt, 0, wx.EXPAND)
        sizerPanelCellContent.AddSpacer(3)
        self.CellContentTxt = wx.TextCtrl(
            PanelCellContent, wx.ID_ANY, value="", size=(600, 23))
        self.CellContentTxt.SetBackgroundColour(wx.WHITE)
        sizerPanelCellContent.Add(self.CellContentTxt, 0, wx.EXPAND)
        PanelCellContent.SetSizer(sizerPanelCellContent)
        sizerPanelSheet.Add(PanelCellContent)
        sizerPanelSheet.AddSpacer(10)

        # Grid: XLS (XLS-style)
        self.Sheet = wx.grid.Grid(PanelSheet)

        # Default values of grid
        self.Sheet.nRow = 30
        self.Sheet.nCol = 8
        self.Sheet.content4undo = [0, 0, '']
        self.Sheet.filePath = ''

        # Creating the grid object (specify label names)
        self.Sheet.CreateGrid(self.Sheet.nRow, self.Sheet.nCol)
        self.Sheet.SetColLabelValue(0, "Subject")
        for i in xrange(1, self.Sheet.nCol):
            self.Sheet.SetColLabelValue(i, "F%d" % i)

        # Specify grid events
        self.Sheet.Bind(wx.EVT_KEY_DOWN, self.onControlKey)
        self.Sheet.Bind(wx.grid.EVT_GRID_EDITOR_CREATED, self.onCellEdit)
        self.Sheet.Bind(wx.grid.EVT_GRID_LABEL_RIGHT_CLICK,
                        self.onLabelRightClick)
        self.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.onCellRightClick)

        "TODO: OLD CODE - check what's needed"
        # dropTarget = GridFileDropTarget(self.Sheet)
        # self.Sheet.SetDropTarget(dropTarget)
        # self.Sheet.EnableDragRowSize()
        # self.Sheet.EnableDragColSize()

        # Create the grid object
        sizerPanelSheet.Add(self.Sheet)
        PanelSheet.SetSizer(sizerPanelSheet)
        sizerPanelDataEntry.Add(PanelSheet, 0, wx.EXPAND)
        sizerPanelDataEntry.AddSpacer(10)

        """
        # Panel Buttons
        PanelButton = wx.Panel(self, wx.ID_ANY)
        sizerButton = wx.BoxSizer(wx.HORIZONTAL)
        sizerButton.AddSpacer(10)
        # sous panel avec le bouton des data
        PanelButtonData = wx.Panel(PanelButton, wx.ID_ANY)
        sizerButtonData = wx.BoxSizer(wx.HORIZONTAL)
        ButtonDefFactor = wx.Button(PanelButtonData, 1, label="Define Factor")
        sizerButtonData.Add(ButtonDefFactor, 0, wx.EXPAND)
        sizerButtonData.AddSpacer(5)

        self.Buttonsave = wx.Button(
            PanelButtonData, 4, label="Save Data and continue")
        sizerButtonData.Add(self.Buttonsave, 0, wx.EXPAND)
        sizerButtonData.AddSpacer(5)
        PanelButtonData.SetSizer(sizerButtonData)
        sizerButton.Add(PanelButtonData, 0, wx.EXPAND)
        sizerButton.AddSpacer(20)
        """

        # Panel: Button field below table
        PanelButton = wx.Panel(self, wx.ID_ANY)
        sizerButton = wx.BoxSizer(wx.HORIZONTAL)
        sizerButton.AddSpacer(10)
        PanelInsert = wx.Panel(PanelButton, wx.ID_ANY)
        sizerInsert = wx.BoxSizer(wx.HORIZONTAL)
        TextInserRow = wx.StaticText(
            PanelInsert, wx.ID_ANY, label="Number of Rows :")
        sizerInsert.Add(TextInserRow, 0, wx.ALIGN_CENTRE)
        sizerInsert.AddSpacer(5)
        self.Sheet.nRow = self.Sheet.GetNumberRows()
        self.Row = wx.SpinCtrl(PanelInsert, 1, str(self.Sheet.nRow),
                               min=1, max=1000, style=wx.SP_ARROW_KEYS)
        sizerInsert.Add(self.Row, 0, wx.EXPAND)
        sizerInsert.AddSpacer(20)
        TextInserCol = wx.StaticText(
            PanelInsert, wx.ID_ANY, label="Number of Cols :")
        sizerInsert.Add(TextInserCol, 0, wx.ALIGN_CENTRE)
        sizerInsert.AddSpacer(5)
        self.Sheet.nCol = self.Sheet.GetNumberCols()
        self.Col = wx.SpinCtrl(PanelInsert, 2, str(self.Sheet.nCol),
                               min=1, max=100, style=wx.SP_ARROW_KEYS)
        sizerInsert.Add(self.Col, 0, wx.EXPAND)
        sizerInsert.AddSpacer(5)
        PanelInsert.SetSizerAndFit(sizerInsert)
        sizerButton.Add(PanelInsert, 0, wx.EXPAND)
        sizerButton.AddSpacer(10)



        wx.EVT_SPINCTRL(self,1,self.ModifRow)
        wx.EVT_SPINCTRL(self,2,self.ModifCol)

       

        """
        # Panel clear + copy + paste + export
        PanelClear = wx.Panel(PanelButton, wx.ID_ANY)
        sizerClear = wx.BoxSizer(wx.HORIZONTAL)
        sizerClear.AddSpacer(5)
        ButtonExport = wx.Button(
            PanelClear, 17, label="Export Table to CSV file")
        sizerClear.Add(ButtonExport, 0, wx.EXPAND)
        sizerClear.AddSpacer(5)

        PanelClear.SetSizerAndFit(sizerClear)
        sizerClear.AddSpacer(5)

        sizerButton.Add(PanelClear, 0, wx.EXPAND)

        PanelButton.SetSizerAndFit(sizerButton)
        PanelButton.SetSizerAndFit(sizerButton)
        """

        sizerFrame = wx.BoxSizer(wx.VERTICAL)
        sizerFrame.Add(PanelDataEntry, 0, wx.EXPAND)
        #sizerFrame.Add(PanelButton, 0, wx.EXPAND)
        sizerFrame.Add(PanelButton, 0, wx.EXPAND)
        # lie tout au sizer
        PanelDataEntry.SetSizer(sizerPanelDataEntry)
        self.SetSizerAndFit(sizerFrame)

        """
        # evemement
        wx.EVT_BUTTON(self, 1, self.DefFactor)
        wx.EVT_BUTTON(self, 4, self.SaveData)
        wx.EVT_BUTTON(self, 11, self.Drag)
        wx.EVT_BUTTON(self, 17, self.ExportToXls)

        # TODO: SORT BUTTON !!!!!

        """
        # Default variables
        self.save = False
        """
        self.info = Parent
        self.ExportData = Parent.ExportData
        """
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.onCellSelected)
        """
        if self.ExportData.H5 == []:
            self.Buttonsave.Disable()
            self.Show(True)
        else:
            self.ReadH5()

        """

    def onCellEdit(self, event):
        """Get control during cell editing"""
        editor = event.GetControl()
        editor.Bind(wx.EVT_KEY_DOWN, self.onEditorKey)
        event.Skip()

    def onEditorKey(self, event):
        """Key event handler during cell editing (only UP or DOWN)"""
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_UP:
            self.Sheet.MoveCursorUp(False)
        elif keycode == wx.WXK_DOWN:
            self.Sheet.MoveCursorDown(False)
        else:
            pass
        event.Skip()

    def onControlKey(self, event):
        """Key event handler if Ctrl is pressed"""
        controlKeyDown = event.ControlDown()
        keycode = event.GetKeyCode()
        if controlKeyDown:
            if keycode == 67:  # If Ctrl+C is pressed
                self.onCtrlCopy()
            elif keycode == 86:  # If Ctrl+V is pressed
                self.onCtrlPaste('clip')
            elif keycode == 90:  # If Ctrl+Z is pressed
                if self.Sheet.content4undo[2] != '':
                    self.onCtrlPaste('undo')
            elif keycode == 65:  # If Ctrl+A is pressed
                self.Sheet.SelectAll()
        if keycode == 127:   # If del is pressed
            self.onDelete()
        else:
            event.Skip()

    def onCtrlCopy(self):
        """Copy cell content to the clipboard"""
        # Get extend of cells to copy
        if self.Sheet.GetSelectionBlockTopLeft() == []:
            rows = 1
            cols = 1
            iscell = True
        else:
            rows = self.Sheet.GetSelectionBlockBottomRight()[0][0] \
                - self.Sheet.GetSelectionBlockTopLeft()[0][0] + 1
            cols = self.Sheet.GetSelectionBlockBottomRight()[0][1] \
                - self.Sheet.GetSelectionBlockTopLeft()[0][1] + 1
            iscell = False

        # cell content that should be copied to the clipboard
        cellcontent = ''

        # get content for each cell - add '\t' for cols and '\n' for rows
        for r in range(rows):
            for c in range(cols):
                if iscell:
                    cellcontent += str(self.Sheet.GetCellValue(
                        self.Sheet.GetGridCursorRow() + r,
                        self.Sheet.GetGridCursorCol() + c))
                else:
                    cellcontent += str(self.Sheet.GetCellValue(
                        self.Sheet.GetSelectionBlockTopLeft()[0][0] + r,
                        self.Sheet.GetSelectionBlockTopLeft()[0][1] + c))
                if c < cols - 1:
                    cellcontent += '\t'
            cellcontent += '\n'

        # Put the content into a text data object
        clipboard = wx.TextDataObject()
        clipboard.SetText(cellcontent)
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(clipboard)
            wx.TheClipboard.Close()
        else:
            wx.MessageBox("Can't open the clipboard", "Error")

    def onCtrlPaste(self, stage):
        """Paste copied content from the clipoard or undo previous paste"""
        # Get content to paste from clipboard
        if stage == 'clip':
            clipboard = wx.TextDataObject()
            if wx.TheClipboard.Open():
                wx.TheClipboard.GetData(clipboard)
                wx.TheClipboard.Close()
            else:
                wx.MessageBox("Can't open the clipboard", "Error")
            cellcontent = clipboard.GetText()
            if self.Sheet.GetSelectionBlockTopLeft() == []:
                rowstart = self.Sheet.GetGridCursorRow()
                colstart = self.Sheet.GetGridCursorCol()
            else:
                rowstart = self.Sheet.GetSelectionBlockTopLeft()[0][0]
                colstart = self.Sheet.GetSelectionBlockTopLeft()[0][1]
        # Get content to paste from previous cell content
        elif stage == 'undo':
            cellcontent = self.Sheet.content4undo[2]
            rowstart = self.Sheet.content4undo[0]
            colstart = self.Sheet.content4undo[1]
        else:
            wx.MessageBox("Paste method " + stage + " does not exist", "Error")

        # Do the pasting of content or undo a previous pasting
        newText4undo = ''
        # Convert cell content from clipboard text to cell values
        for row_id, column in enumerate(cellcontent.splitlines()):
            for col_id, content in enumerate(column.split('\t')):
                if row_id + rowstart < self.Sheet.NumberRows \
                        and col_id + colstart < self.Sheet.NumberCols:
                    newText4undo += str(self.Sheet.GetCellValue(
                        rowstart + row_id, colstart + col_id)) + '\t'
                    self.Sheet.SetCellValue(
                        rowstart + row_id, colstart + col_id, content)
            newText4undo = newText4undo[:-1] + '\n'

        # store undo content
        if stage == 'clip':
            self.Sheet.content4undo = [rowstart, colstart, newText4undo]
        else:
            self.Sheet.content4undo = [0, 0, '']

    def onDelete(self):
        """Delete cell content in selected area"""
        # Get extend of cells to delete
        if self.Sheet.GetSelectionBlockTopLeft() == []:
            rows = 1
            cols = 1
        else:
            rows = self.Sheet.GetSelectionBlockBottomRight()[0][0] \
                - self.Sheet.GetSelectionBlockTopLeft()[0][0] + 1
            cols = self.Sheet.GetSelectionBlockBottomRight()[0][1] \
                - self.Sheet.GetSelectionBlockTopLeft()[0][1] + 1

        # Clear cells contents
        for r in range(rows):
            for c in range(cols):
                if self.Sheet.GetSelectionBlockTopLeft() == []:
                    self.Sheet.SetCellValue(
                        self.Sheet.GetGridCursorRow() + r,
                        self.Sheet.GetGridCursorCol() + c, '')
                else:
                    self.Sheet.SetCellValue(
                        self.Sheet.GetSelectionBlockTopLeft()[0][0] + r,
                        self.Sheet.GetSelectionBlockTopLeft()[0][1] + c, '')

    def onCellRightClick(self, event):
        """Opens file selection window and enters file paths into table"""
        # Get cell location and row size
        col_id = event.GetCol()
        row_id = event.GetRow()
        nRow = self.Sheet.GetNumberRows()

        # Highlight Cell
        self.Sheet.SetGridCursor(row_id, col_id)
        self.Sheet.SetCellBackgroundColour(row_id, col_id,
                                           wx.Colour(192, 192, 192))

        # File Selection Popup
        wildcard = "EPH files (*.eph) | *.eph | " \
            "Python source (*.txt; *.rst; *.dat)|*.txt;*.rst;*.dat|" \
            "All files (*.*) | *.*"
        dlg = wx.FileDialog(
            None, defaultDir=self.Sheet.filePath, wildcard=wildcard,
            style=wx.FD_MULTIPLE, message="Add files to the table")
        answer = dlg.ShowModal()
        if answer == wx.ID_OK:
            # Store file paths into table
            content = dlg.GetPaths()
            for i, e in enumerate(content):
                if row_id + i < nRow:
                    self.Sheet.SetCellValue(row_id + i, col_id, e)

        # Get current folder path and store it for next time
        self.Sheet.filePath = os.path.dirname(dlg.GetPath())

        # Restore all temporal function changes
        dlg.Destroy()
        self.Sheet.SetCellBackgroundColour(row_id, col_id, wx.WHITE)
        event.Skip()

    def onLabelRightClick(self, event):
        """Open popup window to change column label name on right click"""
        if event.GetCol() != -1:
            dlg = wx.TextEntryDialog(None, 'Change column name to')
            dlg.ShowModal()
            newLabelName = dlg.GetValue()
            dlg.Destroy()

            # Make sure that answer is not empty
            if newLabelName:
                self.Sheet.SetColLabelValue(event.GetCol(),
                                            newLabelName)
        event.Skip()

    def onClose(self, event):
        """Show exit message when Data Panel gets closed"""
        # TODO: when is save true? should I add CTRL+S function?
        if self.save:
            self.Destroy()
        else:
            dlg = wx.MessageDialog(
                self, "Do you really want to close the data entry window?",
                "Exit Data Entry Window",
                wx.OK | wx.CANCEL | wx.ICON_QUESTION)
            answer = dlg.ShowModal()
            dlg.Destroy()
            if answer == wx.ID_OK:
                self.Destroy()





    def ModifRow(self, event):
        ActualRow = self.Row.GetValue()
        SheetRow = self.Sheet.GetNumberRows()
        while SheetRow != ActualRow:
            if SheetRow < ActualRow:
                self.Sheet.AppendRows()
            # Add Row
            elif SheetRow > ActualRow:
                self.Sheet.DeleteRows(ActualRow)
            SheetRow = self.Sheet.GetNumberRows()
        self.NbRow = self.Row.GetValue()

    def ModifCol(self, event):
        ActualCol = self.Col.GetValue()
        SheetCol = self.Sheet.GetNumberCols()
        while SheetCol != ActualCol:
            # Add Row
            if SheetCol < ActualCol:
                self.Sheet.AppendCols()
                ####self.Sheet.SetColLabelValue(ActualCol, "F%d" % ActualCol)
                txt = []
                for c in range(ActualCol):
                    txt.append(self.Sheet.GetColLabelValue(c))
                self.text = txt

            elif SheetCol > ActualCol:
                self.Sheet.DeleteCols(ActualCol)
                txt = []
                for c in range(ActualCol):
                    txt.append(self.Sheet.GetColLabelValue(c))
                self.text = txt
            SheetCol = self.Sheet.GetNumberCols()
        self.text.insert(0, '')
        self.NbCol = self.Col.GetValue()



    def ReadH5(self):
        self.Show(True)
        self.Buttonsave.Disable()
        file = tables.openFile(self.ExportData.H5, mode='r')
        FactorName = file.getNode('/Names/Within')
        self.FactorName = FactorName.read()
        Level = file.getNode('/Info/Level')
        self.Level = Level.read()
        NoEpmtyCol = file.getNode('/Sheet/NoEmptyCol')
        NoEpmtyCol = NoEpmtyCol.read()
        SheetColName = file.getNode('/Sheet/ColName')
        SheetColName = SheetColName.read()
        SheetValue = file.getNode('/Sheet/Value')
        SheetValue = SheetValue.read()
        MaxColNumber = np.array(NoEpmtyCol).max() + 1
        if MaxColNumber > 9:
            self.Sheet.SetNumberCols(MaxColNumber)
            self.Sheet.nCol = MaxColNumber
        else:
            self.Sheet.nCol = 9
        self.Col.SetValue(self.Sheet.nCol)
        self.text = ['']
        for i, col in enumerate(NoEpmtyCol):

            ColName = SheetColName[i]
            self.Sheet.SetColLabelValue(col, ColName)
            self.text.append(ColName)
            self.BoxFactor.SetItems(self.text)
            ColValue = SheetValue[i]
            if len(ColValue) > 35:
                self.Sheet.SetNumberRows(len(ColValue))
                self.Sheet.nRow = len(ColValue)
            else:
                self.Sheet.nRow = 30
            self.Row.SetValue(self.Sheet.nRow)
            for row, value in enumerate(ColValue):
                self.Sheet.SetCellValue(row, col, value)
            file.close()


    def ExportToXls(self, event):
        wx.InitAllImageHandlers()
        dlg = wx.FileDialog(None, "Save Table to", wildcard="*.csv",
                            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        retour = dlg.ShowModal()
        chemin = dlg.GetPath()
        fichier = dlg.GetFilename()
        dlg.Destroy()
        dlg.Show(True)
        CsvFile = open(chemin, "w")
        Data = ReadSheet(self.Sheet, self.Sheet.nRow, self.Sheet.nCol)
        row = np.array(Data.NoEmptyRow).max() + 1
        col = np.array(Data.NoEmptyCol).max() + 1
        for r in range(row):
            tmp = []
            for c in range(col):
                cell = self.Sheet.GetCellValue(r, c)
                tmp.append(';')
                tmp.append(cell)
            tmp.remove(';')
            CsvFile.write("".join(tmp))
            CsvFile.write('\n')

    def onCellSelected(self, event):
        """Show content of select cell in content field"""
        row = event.GetRow()
        col = event.GetCol()
        CellValue = self.Sheet.GetCellValue(row, col)
        self.CellContentTxt.SetValue(CellValue)   
        event.Skip()

    def DefFactor(self, event):
        self.Data = ReadSheet(self.Sheet, self.Sheet.nRow, self.Sheet.nCol)
        self.ModelDef = FactorWithin(
            self.Data.NoEmptyCol, self.Sheet, self, Level=[], Factor=[])
        self.ModelDef.Show(True)

    def SaveData(self, event):
        self.Show(False)
        wx.InitAllImageHandlers()
        dlg = wx.FileDialog(None, "Save Model to", wildcard="*.h5",
                            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        retour = dlg.ShowModal()
        chemin = dlg.GetPath()
        fichier = dlg.GetFilename()
        dlg.Destroy()
        dlg.Show(True)

        try:
            self.ModelDef.Close()
            self.ModelDef.ModelFull.Close()
        except:
            pass
        self.info.DataFile.SetLabel(chemin)
        # creation du fichier H5 pour les donee importante
        self.file = tables.openFile(chemin, mode='w')
        self.DataGroup = self.file.createGroup('/', 'Data')
        self.DataGFPGroup = self.file.createGroup('/', 'DataGFP')
        self.ModelGroup = self.file.createGroup('/', 'Model')
        self.InfoGroup = self.file.createGroup('/', 'Info')
        self.SheetGroup = self.file.createGroup('/', 'Sheet')
        self.NamesGroup = self.file.createGroup('/', 'Names')
        self.ErrorGroup = self.file.createGroup('/', 'Error')
        ResultGroup = self.file.createGroup('/', 'Result')
        IntermediateResults = self.file.createGroup(
            ResultGroup, 'IntermediateResult')
        Aov = self.file.createGroup(ResultGroup, 'Anova')
        PH = self.file.createGroup(ResultGroup, 'PostHoc')
        self.file.createGroup(Aov, 'All')
        self.file.createGroup(Aov, 'GFP')
        self.file.createGroup(PH, 'All')
        self.file.createGroup(PH, 'GFP')
        SavingObj = DataProcessing(self)
        self.file.close()

        # export fichier H5
        self.ExportData.H5 = chemin
        info = ReturnInfomation(chemin)
        self.info.TxtInfo.SetLabel("".join(info.text))
        if info.CovariatePresent:
            self.info.ExportData.AnovaWave.PostHocCheckBox.Disable()
            self.info.ExportData.AnovaIS.PostHocCheckBox.Disable()
            self.info.ExportData.AnovaWave.PostHocCheckBox.SetValue(False)
            self.info.ExportData.AnovaIS.PostHocCheckBox.SetValue(False)
        else:
            self.info.ExportData.AnovaWave.PostHocCheckBox.Enable()
            self.info.ExportData.AnovaIS.PostHocCheckBox.Enable()
        self.save = True
        self.Close()