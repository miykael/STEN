import wx
import os
from Factors import FactorWithin


class DataEntry(wx.Frame):

    """
    Window to create the dataset and specify the factors
    """

    def __init__(self, MainFrame):

        # Create data table window
        wx.Frame.__init__(self, None, wx.ID_ANY, title="Data Entry",
                          style=wx.DEFAULT_FRAME_STYLE | wx.RESIZE_BORDER)
        self.MainFrame = MainFrame

        # Panel: Data Entry
        PanelDataEntry = wx.Panel(self, wx.ID_ANY)
        sizerPanelDataEntry = wx.BoxSizer(wx.HORIZONTAL)

        # Panel: Data Sheet (XLS-style)
        PanelSheet = wx.Panel(PanelDataEntry, wx.ID_ANY)
        sizerPanelSheet = wx.BoxSizer(wx.VERTICAL)
        sizerPanelSheet.AddSpacer(5)

        # Panel: Cell content field at top of data sheet
        PanelCellContent = wx.Panel(PanelSheet, wx.ID_ANY)
        sizerPanelCellContent = wx.BoxSizer(wx.HORIZONTAL)
        sizerPanelCellContent.AddSpacer(10)
        TextContentCell = wx.StaticText(
            PanelCellContent, wx.ID_ANY, label='Cell Content:',
            style=wx.ALIGN_LEFT)
        sizerPanelCellContent.Add(TextContentCell, 0, wx.EXPAND)
        sizerPanelCellContent.AddSpacer(3)
        self.CellContentTxt = wx.TextCtrl(PanelCellContent, wx.ID_ANY,
                                          value="", size=(861, 23),
                                          style=wx.TE_READONLY)
        sizerPanelCellContent.Add(self.CellContentTxt, 0, wx.EXPAND)
        PanelCellContent.SetSizer(sizerPanelCellContent)
        sizerPanelSheet.Add(PanelCellContent)
        sizerPanelSheet.AddSpacer(5)

        # Grid: XLS (XLS-style)
        self.Sheet = wx.grid.Grid(PanelSheet)

        # Specify relevant variables
        self.factorNames = []
        self.factorLevels = []
        self.Sheet.nRow = 30
        self.Sheet.nCol = 11
        self.Sheet.content4undo = [0, 0, '']
        self.Sheet.filePath = ''

        # Creating the grid object (specify label names)
        self.Sheet.CreateGrid(self.Sheet.nRow, self.Sheet.nCol)
        self.Sheet.SetColLabelValue(0, "Subject")
        for i in xrange(1, self.Sheet.nCol):
            self.Sheet.SetColLabelValue(i, "F%d" % i)

        # Specify grid events
        self.Sheet.Bind(wx.EVT_KEY_DOWN, self.onControlKey)
        self.Sheet.Bind(wx.grid.EVT_GRID_LABEL_RIGHT_CLICK,
                        self.onLabelRightClick)
        self.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.onCellRightClick)

        # Create the grid object
        sizerPanelSheet.Add(self.Sheet)
        PanelSheet.SetSizer(sizerPanelSheet)
        sizerPanelDataEntry.Add(PanelSheet, 0, wx.EXPAND)
        sizerPanelDataEntry.AddSpacer(10)

        # Panel: Button field below table
        PanelButton = wx.Panel(self, wx.ID_ANY)
        sizerButton = wx.BoxSizer(wx.HORIZONTAL)
        sizerButton.AddSpacer(10)
        # Number of Rows Field
        TextInserRow = wx.StaticText(
            PanelButton, wx.ID_ANY, label="Number of Rows: ")
        sizerButton.Add(TextInserRow, 0, wx.ALIGN_CENTRE)
        self.Sheet.nRow = self.Sheet.GetNumberRows()
        self.Row = wx.SpinCtrl(PanelButton, 1, str(self.Sheet.nRow),
                               size=(75, 25), min=1, max=1000,
                               style=wx.SP_ARROW_KEYS)
        sizerButton.Add(self.Row, 0, wx.EXPAND)
        sizerButton.AddSpacer(20)
        # Number of Columns Field
        TextInserCol = wx.StaticText(
            PanelButton, wx.ID_ANY, label="Number of Columns: ")
        sizerButton.Add(TextInserCol, 0, wx.ALIGN_CENTRE)
        self.Sheet.nCol = self.Sheet.GetNumberCols()
        self.Col = wx.SpinCtrl(PanelButton, 2, str(self.Sheet.nCol),
                               size=(75, 25), min=1, max=1000,
                               style=wx.SP_ARROW_KEYS)
        sizerButton.Add(self.Col, 0, wx.EXPAND)
        sizerButton.AddSpacer(20)
        # Define Import Button
        ButtonImport = wx.Button(PanelButton, wx.ID_ANY, size=(130, 25),
                                 label="Import CSV Data")
        sizerButton.Add(ButtonImport, 0, wx.EXPAND)
        sizerButton.AddSpacer(20)
        # Define Export Button
        ButtonExport = wx.Button(PanelButton, wx.ID_ANY, size=(130, 25),
                                 label="Export CSV Data")
        sizerButton.Add(ButtonExport, 0, wx.EXPAND)
        sizerButton.AddSpacer(20)
        # Define Factor Button
        ButtonDefineFactor = wx.Button(PanelButton, wx.ID_ANY, size=(130, 25),
                                       label="Define Factor")
        sizerButton.Add(ButtonDefineFactor, 0, wx.EXPAND)
        sizerButton.AddSpacer(20)

        # Resize everything and create the window
        PanelButton.SetSizerAndFit(sizerButton)
        sizerFrame = wx.BoxSizer(wx.VERTICAL)
        sizerFrame.Add(PanelDataEntry, 0, wx.EXPAND)
        sizerFrame.AddSpacer(5)
        sizerFrame.Add(PanelButton, 0, wx.EXPAND)
        sizerFrame.AddSpacer(5)
        PanelDataEntry.SetSizer(sizerPanelDataEntry)
        self.SetSizerAndFit(sizerFrame)

        # Specification of events
        wx.EVT_SPINCTRL(self, self.Row.Id, self.modifyRow)
        wx.EVT_SPINCTRL(self, self.Col.Id, self.modifyCol)
        wx.EVT_BUTTON(self, ButtonDefineFactor.Id, self.defineFactor)
        wx.EVT_BUTTON(self, ButtonExport.Id, self.exportData)
        wx.EVT_BUTTON(self, ButtonImport.Id, self.importData)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.onCellSelected)

        # Drag and Drop Function
        dropTarget = GridFileDropTarget(self.Sheet)
        self.Sheet.SetDropTarget(dropTarget)
        self.Sheet.EnableDragRowSize()
        self.Sheet.EnableDragColSize()

        # Fill in table if dataset already exists
        if self.MainFrame.Dataset != {}:
            self.loadDataset()

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
            elif keycode == 83:  # If Ctrl+S is pressed
                self.exportData(event)
            elif keycode == 79:  # If Ctrl+O is pressed
                self.importData(event)
            elif keycode == 68:  # If Ctrl+D is pressed
                self.defineFactor(event)
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
        wildcard = "EPH files (*.eph)|*.eph|" \
            "Python source (*.txt; *.rst; *.dat)|*.txt;*.rst;*.dat|" \
            "All files (*.*)|*.*"
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

            # If first column is called 'Subject' fill out all none empty cells
            if self.Sheet.GetColLabelValue(0) == 'Subject':
                for i in range(len(content)):
                    if self.Sheet.GetCellValue(row_id + i, 0) == '':
                        self.Sheet.SetCellValue(row_id + i, 0,
                                                unicode(row_id + i + 1))

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
        dlg = wx.MessageDialog(
            self, "Do you really want to close the data entry window?",
            "Exit Data Entry Window",
            wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        answer = dlg.ShowModal()
        dlg.Destroy()
        if answer == wx.ID_OK:
            self.Destroy()
            self.MainFrame.Show(True)

    def modifyRow(self, event):
        "Adds or deletes number of rows"
        ActualRow = self.Row.GetValue()
        SheetRow = self.Sheet.GetNumberRows()
        while SheetRow != ActualRow:
            # Add Row
            if SheetRow < ActualRow:
                self.Sheet.AppendRows()
            # Delete Row
            elif SheetRow > ActualRow:
                self.Sheet.DeleteRows(ActualRow)
            SheetRow = self.Sheet.GetNumberRows()

    def modifyCol(self, event):
        "Adds or deletes number of columns"
        ActualCol = self.Col.GetValue()
        SheetCol = self.Sheet.GetNumberCols()
        while SheetCol != ActualCol:
            # Add Column
            if SheetCol < ActualCol:
                self.Sheet.AppendCols()
                self.Sheet.SetColLabelValue(SheetCol, "F%d" % SheetCol)
            # Delete Column
            elif SheetCol > ActualCol:
                self.Sheet.DeleteCols(ActualCol)
            SheetCol = self.Sheet.GetNumberCols()

    def onCellSelected(self, event):
        """Show content of select cell in content field"""
        cellRow = event.GetRow()
        cellCol = event.GetCol()
        CellValue = self.Sheet.GetCellValue(cellRow, cellCol)
        self.CellContentTxt.SetValue(CellValue)
        event.Skip()

    def readTable(self):
        """Reads the label and content of the current table
        and checks if table is empty or rectangular"""

        dataTable = {}

        # Get Label Values
        dataTable['labels'] = [self.Sheet.GetColLabelValue(i)
                               for i in range(self.Sheet.GetNumberCols())]

        # Get Table Content
        dataTable['content'] = []
        for j in range(self.Sheet.GetNumberCols()):
            currentRow = [self.Sheet.GetCellValue(i, j)
                          for i in range(self.Sheet.GetNumberRows())]
            if filter(None, currentRow) != []:
                dataTable['content'].append(filter(None, currentRow))

        # make sure that table is not empty
        if dataTable['content'] == []:
            errorMessage = 'tableIsEmpty'
        else:
            # make sure that column have the same length
            rowsFirstColumn = len(dataTable['content'][0])
            errorMessage = ''
            for i in range(1, len(dataTable['content'])):
                # make sure that font color of column is black
                for c in range(len(dataTable['content'][i])):
                    self.Sheet.SetCellTextColour(c, i,
                                                 wx.Colour(76, 76, 76, 255))
                # check length of column
                if rowsFirstColumn != len(dataTable['content'][i]):
                    errorMessage = 'tableIsRectangular'
                    # change color of unequal columns
                    for c in range(len(dataTable['content'][i])):
                        self.Sheet.SetCellTextColour(c, i, wx.RED)

            dataTable['nRows'] = rowsFirstColumn
            dataTable['nCols'] = len(dataTable['content'])

            # Drop the unspecified labels
            dataTable['labels'] = dataTable['labels'][:dataTable['nCols']]

        return dataTable, errorMessage

    def checkTableContent(self, dataTable):
        errorNotAFile = ''
        # Go through table
        for i in range(dataTable['nCols']):
            for j in range(dataTable['nRows']):

                cellcontent = dataTable['content'][i][j]

                # Check if content could be a file
                if os.path.dirname(cellcontent) != '':
                    # Check if file is exists or not
                    if not os.path.exists(cellcontent):
                        self.Sheet.SetCellTextColour(j, i, wx.RED)
                        errorNotAFile = 'errorNotAFile'

        return errorNotAFile

    def getTableInfo(self):
        """Gets table information and ok if possible to proceed"""

        # Read Table and handle error messages
        dataTable, errorMessage = self.readTable()
        ok2proceed = False

        # Error message if table is not rectangular
        if errorMessage == 'tableIsRectangular':
            dlg = wx.MessageDialog(
                self, style=wx.OK | wx.ICON_WARNING,
                caption="Warning: Column length is unequal",
                message="Not all columns have the same length!" +
                        "\nPlease correct that.")
            dlg.ShowModal()
            dlg.Destroy()
        # Error message if table is empty
        elif errorMessage == 'tableIsEmpty':
            dlg = wx.MessageDialog(
                self, style=wx.OK | wx.ICON_WARNING,
                caption="Warning: Table is empty",
                message="Table is empty.\nFill it with content first!")
            dlg.ShowModal()
            dlg.Destroy()
        else:
            # Check if table content contains existing files
            errorNotAFile = self.checkTableContent(dataTable)
            if errorNotAFile == 'errorNotAFile':
                dlg = wx.MessageDialog(
                    self, style=wx.OK | wx.ICON_WARNING,
                    caption="Warning: File doesn't exist",
                    message="Some files don't exist." +
                            "\nPlease specify only existing file names!")
                dlg.ShowModal()
                dlg.Destroy()
            else:
                ok2proceed = True

        return dataTable, ok2proceed

    def defineFactor(self, event):
        """Opens Factor Definition Window if everything is ok"""
        # Get Table info
        self.dataTable, ok2proceed = self.getTableInfo()
        # Open Factor definition dialog
        if ok2proceed:
            self.ModelDef = FactorWithin(self, self.factorNames,
                                         self.factorLevels)
            self.ModelDef.Show(True)

    def exportData(self, event):
        """Saves Table content into a csv-file"""
        # Get Table info
        self.dataTable, ok2proceed = self.getTableInfo()
        if ok2proceed:
            # Ask for csv filename
            dlg = wx.FileDialog(None, "Save Table to", wildcard="*.csv",
                                style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
            answer = dlg.ShowModal()
            dlg.Destroy()

            # If file name has been specified
            if answer == wx.ID_OK:
                path2csv = dlg.GetPath()

                # Add ".csv" if not specified
                filename, file_extension = os.path.splitext(path2csv)
                if file_extension != '.csv':
                    path2csv += '.csv'

                # Structure output together
                output = [[self.dataTable['content'][j][i]
                           for j in range(self.dataTable['nCols'])]
                          for i in range(self.dataTable['nRows'])]

                # Write output to csv file
                import csv
                with open(path2csv, 'w') as fcsv:
                    a = csv.writer(fcsv, delimiter=',')
                    a.writerow(self.dataTable['labels'])
                    a.writerows(output)

    def importData(self, event):
        """Get content from a csv-file and write it into the table"""

        # Ask for csv filename to load
        dlg = wx.FileDialog(None, "Load CSV file", wildcard="*.csv",
                            style=wx.FD_OPEN)
        answer = dlg.ShowModal()
        dlg.Destroy()

        # If file name has been specified
        if answer == wx.ID_OK:
            path2csv = dlg.GetPath()

            # If file exists
            if os.path.exists(path2csv):

                dataTable = {}
                inputdata = []

                # Get CSV content and store it in dataTable variable
                import csv
                with open(path2csv, 'rb') as fcsv:
                    reader = csv.reader(fcsv)
                    for row in reader:

                        row = [unicode(cell, 'utf-8') for cell in row]

                        # Save Labels and number of columns
                        if dataTable == {}:
                            dataTable['labels'] = row
                            dataTable['nCols'] = len(row)

                        else:
                            inputdata.append(row)

                dataTable['content'] = map(list, zip(*inputdata))
                dataTable['nRows'] = len(dataTable['content'][0])

                # Change name of labels
                for i, l in enumerate(dataTable['labels']):
                    self.Sheet.SetColLabelValue(i, l)

                # Write content to table
                self.Sheet.ClearGrid()
                for r in range(dataTable['nRows']):
                    for c in range(dataTable['nCols']):
                        value = dataTable['content'][c][r]
                        self.Sheet.SetCellValue(r, c, value)

            # If file doesn't exists
            else:
                dlg = wx.MessageDialog(
                    self, style=wx.OK | wx.ICON_WARNING,
                    caption="Warning: File doesn't exist",
                    message="Can't load CSV-file:\n%s" % (path2csv) +
                            "\nFile doesn't exist!")
                dlg.ShowModal()
                dlg.Destroy()

    def loadDataset(self):
        """Loads the dataset under Mainframe.Dataset if it already exists"""
        dataTable = self.MainFrame.Dataset['Table']

        # Change name of labels
        for i, l in enumerate(dataTable['labels']):
            self.Sheet.SetColLabelValue(i, l)

        # Write content to table
        for r in range(dataTable['nRows']):
            for c in range(dataTable['nCols']):
                value = dataTable['content'][c][r]
                self.Sheet.SetCellValue(r, c, value)


class GridFileDropTarget(wx.FileDropTarget):

    """File Drop Target"""

    def __init__(self, grid):
        wx.FileDropTarget.__init__(self)
        self.grid = grid

    def OnDropFiles(self, x, y, filenames):
        # the x,y coordinates are Unscrolled coordinates.
        # They must be changed to scrolled coordinates.
        x, y = self.grid.CalcUnscrolledPosition(x, y)

        # now we need to get the row and column from the grid
        col = self.grid.XToCol(x)
        row = self.grid.YToRow(y)

        # if drop objects are files, add them to the column
        if not os.path.isdir(filenames[0]):
            for i, f in enumerate(filenames):
                if row > -1 and col > -1:
                    self.grid.SetCellValue(row + i, col, f)
            linesAdded = len(filenames)

        # if drop objects are folders add them successively to columns
        else:
            for j, f in enumerate(filenames):
                listOfFiles = sorted(os.listdir(filenames[j]))
                for i, f in enumerate(listOfFiles):
                    if row > -1 and col > -1:
                        self.grid.SetCellValue(row + i, col + j,
                                               os.path.join(filenames[j], f))
            linesAdded = len(listOfFiles)

        # If first column is called 'Subject' fill out all none empty cells
        if self.grid.GetColLabelValue(0) == 'Subject':
            for i in range(linesAdded):
                if self.grid.GetCellValue(row + i, 0) == '':
                    self.grid.SetCellValue(row + i, 0,
                                           unicode(row + i + 1))
