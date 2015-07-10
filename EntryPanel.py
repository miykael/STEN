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
    feuille de clacul sytle SPSS"""

    def __init__(self, Parent):
        wx.Frame.__init__(self, None, 1, title="DATA ENTRY",
                          style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
        FrameSizer = wx.BoxSizer(wx.VERTICAL)
        NbRow = 30
        NbCol = 9
        self.save = False
        self.info = Parent
        self.ExportData = Parent.ExportData
        # feuille de clacul style XLS)
        PanelData = wx.Panel(self, -1)
        DataSizer = wx.BoxSizer(wx.HORIZONTAL)
        PanelSheet = wx.Panel(PanelData, -1)
        SheetSizer = wx.BoxSizer(wx.VERTICAL)
        SheetSizer.AddSpacer(10)
        PanelCellContent = wx.Panel(PanelSheet, -1)
        CellContentSizer = wx.BoxSizer(wx.HORIZONTAL)
        CellContentSizer.AddSpacer(10)
        CellTxt = wx.StaticText(
            PanelCellContent, -1, label='Cell Content : ', style=wx.ALIGN_LEFT)
        CellContentSizer.Add(CellTxt, 0, wx.EXPAND)
        CellContentSizer.AddSpacer(5)
        self.CellContentTxt = wx.TextCtrl(PanelCellContent, -1, value="",
                                          style=wx.TE_READONLY, size=(600, 21))
        self.CellContentTxt.SetBackgroundColour(wx.WHITE)
        CellContentSizer.Add(self.CellContentTxt, 0, wx.EXPAND)
        PanelCellContent.SetSizer(CellContentSizer)
        SheetSizer.Add(PanelCellContent)
        SheetSizer.AddSpacer(10)
        # self.Sheet=CalculSheet(PanelSheet)
        self.Sheet = wx.grid.Grid(PanelSheet)
        dropTarget = GridFileDropTarget(self.Sheet)
        self.Sheet.SetDropTarget(dropTarget)
        self.Sheet.EnableDragRowSize()
        self.Sheet.EnableDragColSize()
        self.Sheet.CreateGrid(NbRow, NbCol)
        SheetSizer.Add(self.Sheet)
        PanelSheet.SetSizer(SheetSizer)
        DataSizer.Add(PanelSheet, 0, wx.EXPAND)
        DataSizer.AddSpacer(10)

        # Panel pour le Drop des fichier
        PanelDrop = wx.Panel(PanelData, -1)
        DropSizer = wx.BoxSizer(wx.HORIZONTAL)
        PanelCol = wx.Panel(PanelDrop, -1)
        ColSizer = wx.BoxSizer(wx.VERTICAL)
        ColSizer.AddSpacer(5)
        # liste des Valeur d'une colone
        self.ColName = wx.StaticText(
            PanelCol, -1, label='Select One Colon', style=wx.ALIGN_CENTRE)
        ColSizer.Add(self.ColName, 0, wx.ALIGN_CENTRE)
        ColSizer.AddSpacer(5)
        self.ColData = wx.ListBox(PanelCol, 1, choices="",
                                  style=wx.LB_EXTENDED |
                                  wx.LB_HSCROLL, size=(190, 400))
        ColSizer.Add(self.ColData, 0, wx.EXPAND)
        ColSize = self.ColData.GetSize()
        ColSizer.AddSpacer(10)
        self.SortButton = wx.Button(PanelCol, 14, label='sort')
        ColSizer.Add(self.SortButton, 0, wx.EXPAND)
        ColSize = self.ColData.GetSize()
        ColSizer.AddSpacer(10)
        PanelMove = wx.Panel(PanelCol, -1)
        MoveSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.MoveUpButton = wx.Button(PanelMove, 9, label='Move Up')
        MoveSizer.Add(self.MoveUpButton, 0, wx.EXPAND)
        MoveSizer.AddSpacer(5)
        self.MoveDownButton = wx.Button(PanelMove, 10, label='Move Down')
        MoveSizer.Add(self.MoveDownButton, 0, wx.EXPAND)
        PanelMove.SetSizer(MoveSizer)
        ColSizer.Add(PanelMove, 0, wx.EXPAND)
        ColSizer.AddSpacer(10)
        self.OKButton = wx.Button(PanelCol, 11, label='Add')
        ColSizer.Add(self.OKButton, 0, wx.EXPAND)
        PanelCol.SetSizer(ColSizer)

        PanelButton = wx.Panel(PanelDrop, -1)
        ButtonSizer = wx.BoxSizer(wx.VERTICAL)
        self.AddButton = wx.Button(PanelButton, 12, label='<')
        ButtonSizer.Add(self.AddButton, 0, wx.EXPAND)
        ButtonSizer.AddSpacer(10)
        self.RmButton = wx.Button(PanelButton, 13, label='>')
        ButtonSizer.Add(self.RmButton, 0, wx.EXPAND)
        ButtonSizer.AddSpacer(10)
        self.PanelMove = wx.Panel(PanelButton, -1)
        PanelButton.SetSizer(ButtonSizer)
        # List Conteant tous les eph de PathEpSh
        PanelEph = wx.Panel(PanelDrop, -1)
        EphSizer = wx.BoxSizer(wx.VERTICAL)
        EphSizer.AddSpacer(5)
        txteph = wx.StaticText(
            PanelEph, -1, label='EPH Files', style=wx.ALIGN_CENTRE)
        EphSizer.Add(txteph, 0, wx.EXPAND)
        EphSizer.AddSpacer(5)
        self.DragEph = wx.ListBox(PanelEph, 2, choices='',
                                  style=wx.LB_EXTENDED |
                                  wx.LB_HSCROLL, size=ColSize)
        EphSizer.Add(self.DragEph, 0, wx.EXPAND)
        EphSizer.AddSpacer(5)
        # selection Eph folder
        self.ButtonEph = wx.Button(
            PanelEph, 15, label="Select Folder", size=(190, 23))
        EphSizer.Add(self.ButtonEph, 0, wx.EXPAND)
        EphSizer.AddSpacer(5)
        FolderTxT = wx.StaticText(PanelEph, -1, label='Current Folder :',
                                  style=wx.ALIGN_LEFT, size=(190, 21))
        EphSizer.Add(FolderTxT, 0, wx.EXPAND)
        EphSizer.AddSpacer(5)
        self.TextEph = wx.TextCtrl(
            PanelEph, -1, value="", style=wx.TE_READONLY, size=(190, 21))
        self.TextEph.SetBackgroundColour(wx.WHITE)
        EphSizer.Add(self.TextEph, 0, wx.EXPAND)
        EphSizer.AddSpacer(5)
        FilterTxT = wx.StaticText(PanelEph, -1, label='Filter :',
                                  style=wx.ALIGN_LEFT, size=(190, 21))
        EphSizer.Add(FilterTxT, 0, wx.EXPAND)
        EphSizer.AddSpacer(5)
        self.TextFilter = wx.TextCtrl(
            PanelEph, 3, value="", style=wx.TE_PROCESS_ENTER, size=(190, 21))
        self.TextFilter.SetBackgroundColour(wx.WHITE)
        self.TextFilter.Disable()
        EphSizer.Add(self.TextFilter, 0, wx.EXPAND)
        PanelEph.SetSizer(EphSizer)
        DropSizer.Add(PanelCol, 0, wx.EXPAND)
        DropSizer.AddSpacer(5)
        DropSizer.Add(PanelButton, 0, wx.CENTER)
        DropSizer.AddSpacer(5)
        DropSizer.Add(PanelEph, 0, wx.EXPAND)
        DropSizer.AddSpacer(10)
        PanelDrop.SetSizer(DropSizer)
        DataSizer.Add(PanelDrop, 0, wx.EXPAND)
        PanelData.SetSizer(DataSizer)
        FrameSizer.Add(PanelData, 0, wx.EXPAND)
        # on met tous les bouton disable
        self.MoveUpButton.Disable()
        self.MoveDownButton.Disable()
        self.AddButton.Disable()
        self.RmButton.Disable()
        self.OKButton.Disable()
        self.SortButton.Disable()
        # Panel Buttons

        PanelButton = wx.Panel(self, -1)
        ButtonSizer = wx.BoxSizer(wx.HORIZONTAL)
        ButtonSizer.AddSpacer(10)
        # sous panel avec le bouton des data
        PanelButtonData = wx.Panel(PanelButton, -1)
        ButtonDataSizer = wx.BoxSizer(wx.HORIZONTAL)
        ButtonDefFactor = wx.Button(PanelButtonData, 1, label="Define Factor")
        ButtonDataSizer.Add(ButtonDefFactor, 0, wx.EXPAND)
        ButtonDataSizer.AddSpacer(5)

        self.Buttonsave = wx.Button(
            PanelButtonData, 4, label="Save Data and continue")
        ButtonDataSizer.Add(self.Buttonsave, 0, wx.EXPAND)
        ButtonDataSizer.AddSpacer(5)
        PanelButtonData.SetSizer(ButtonDataSizer)
        ButtonSizer.Add(PanelButtonData, 0, wx.EXPAND)
        ButtonSizer.AddSpacer(20)
        # Panel changement nom des colons
        PanelChangeCol = wx.Panel(PanelButton, -1)
        ChangeColSizer = wx.BoxSizer(wx.HORIZONTAL)
        ChangeColSizer.AddSpacer(5)
        NbCol = self.Sheet.GetNumberCols()
        self.text = [""]
        for i in range(NbCol):
            self.text.append(self.Sheet.GetColLabelValue(i))
        TextChangeCol1 = wx.StaticText(
            PanelChangeCol, -1, label="Name Colon : ")
        ChangeColSizer.Add(TextChangeCol1, 0, wx.ALIGN_CENTRE)
        ChangeColSizer.AddSpacer(5)

        self.BoxFactor = wx.ComboBox(
            PanelChangeCol, 1, choices=self.text, style=wx.CB_READONLY)
        ChangeColSizer.Add(self.BoxFactor, 0, wx.EXPAND)
        ChangeColSizer.AddSpacer(5)

        TextChangeCol2 = wx.StaticText(PanelChangeCol, -1, label="into")
        ChangeColSizer.Add(TextChangeCol2, 0, wx.ALIGN_CENTRE)
        ChangeColSizer.AddSpacer(5)

        self.NewName = wx.TextCtrl(PanelChangeCol, 1, value="")
        ChangeColSizer.Add(self.NewName, 0, wx.EXPAND)
        ChangeColSizer.AddSpacer(5)

        ButtonChange = wx.Button(PanelChangeCol, 5, label="rename process")
        ChangeColSizer.Add(ButtonChange, 0, wx.EXPAND)
        PanelChangeCol.SetSizer(ChangeColSizer)
        ButtonSizer.Add(PanelChangeCol, 0, wx.EXPAND)

        # Panel insert rows colums
        PanelButton2 = wx.Panel(self, -1)
        ButtonSizer2 = wx.BoxSizer(wx.HORIZONTAL)
        ButtonSizer2.AddSpacer(10)
        PanelInsert = wx.Panel(PanelButton2, -1)
        InsertSizer = wx.BoxSizer(wx.HORIZONTAL)
        TextInserRow = wx.StaticText(PanelInsert, -1, label="Number of Rows :")
        InsertSizer.Add(TextInserRow, 0, wx.ALIGN_CENTRE)
        InsertSizer.AddSpacer(5)
        self.NbRow = self.Sheet.GetNumberRows()
        self.Row = wx.SpinCtrl(PanelInsert, 1, str(self.NbRow),
                               min=1, max=1000, style=wx.SP_ARROW_KEYS)
        InsertSizer.Add(self.Row, 0, wx.EXPAND)
        InsertSizer.AddSpacer(20)
        TextInserCol = wx.StaticText(PanelInsert, -1, label="Number of Cols :")
        InsertSizer.Add(TextInserCol, 0, wx.ALIGN_CENTRE)
        InsertSizer.AddSpacer(5)
        self.NbCol = self.Sheet.GetNumberCols()
        self.Col = wx.SpinCtrl(PanelInsert, 2, str(self.NbCol),
                               min=1, max=100, style=wx.SP_ARROW_KEYS)
        InsertSizer.Add(self.Col, 0, wx.EXPAND)
        InsertSizer.AddSpacer(5)
        PanelInsert.SetSizerAndFit(InsertSizer)
        ButtonSizer2.Add(PanelInsert, 0, wx.EXPAND)
        ButtonSizer2.AddSpacer(10)

        # Panel clear + copy + paste + export
        PanelClear = wx.Panel(PanelButton2, -1)
        ClearSizer = wx.BoxSizer(wx.HORIZONTAL)
        ClearSizer.AddSpacer(5)
        ButtonPaste = wx.Button(
            PanelClear, 8, label="Paste Clipboard into selected Cell")
        ClearSizer.Add(ButtonPaste, 0, wx.EXPAND)
        ClearSizer.AddSpacer(5)
        ButtonClear = wx.Button(PanelClear, 6, label="clear selceted cells")
        ClearSizer.Add(ButtonClear, 0, wx.EXPAND)
        ClearSizer.AddSpacer(5)
        ButtonClearAll = wx.Button(PanelClear, 7, label="clear All")
        ClearSizer.Add(ButtonClearAll, 0, wx.EXPAND)
        ButtonCopy = wx.Button(
            PanelClear, 16, label="Copy selceted cells to the Clipboard")
        ClearSizer.Add(ButtonCopy, 0, wx.EXPAND)
        ClearSizer.AddSpacer(5)
        ButtonExport = wx.Button(
            PanelClear, 17, label="Export Table to CSV file")
        ClearSizer.Add(ButtonExport, 0, wx.EXPAND)
        ClearSizer.AddSpacer(5)

        PanelClear.SetSizerAndFit(ClearSizer)
        ClearSizer.AddSpacer(5)

        ButtonSizer2.Add(PanelClear, 0, wx.EXPAND)

        PanelButton.SetSizerAndFit(ButtonSizer)
        PanelButton2.SetSizerAndFit(ButtonSizer2)
        FrameSizer.Add(PanelButton, 0, wx.EXPAND)
        FrameSizer.Add(PanelButton2, 0, wx.EXPAND)
        # lie tout au sizer
        self.SetSizerAndFit(FrameSizer)

        # evemement
        wx.EVT_BUTTON(self, 1, self.DefFactor)
        wx.EVT_BUTTON(self, 4, self.SaveData)
        wx.EVT_BUTTON(self, 5, self.RenameCol)
        wx.EVT_BUTTON(self, 6, self.ClearSheet)
        wx.EVT_BUTTON(self, 7, self.ClearAllSheet)
        wx.EVT_BUTTON(self, 8, self.PasteClip)
        wx.EVT_BUTTON(self, 11, self.Drag)
        wx.EVT_BUTTON(self, 9, self.MoveUp)
        wx.EVT_BUTTON(self, 10, self.MoveDown)
        wx.EVT_BUTTON(self, 12, self.AddCol)
        wx.EVT_BUTTON(self, 13, self.RmCol)
        wx.EVT_BUTTON(self, 14, self.Sort)
        wx.EVT_BUTTON(self, 15, self.SelectEphFolder)
        wx.EVT_BUTTON(self, 16, self.CopySelection)
        wx.EVT_BUTTON(self, 17, self.ExportToXls)
        wx.EVT_TEXT_ENTER(self, 3, self.Filter)

        # TODO: SORT BUTTON !!!!!

        # self.ListCol.GetSelections()
        wx.EVT_LISTBOX(self, 1, self.ColSelected)
        wx.EVT_LISTBOX(self, 2, self.EphSelected)
        wx.EVT_SPINCTRL(self, 1, self.ModifRow)
        wx.EVT_SPINCTRL(self, 2, self.ModifCol)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.grid.EVT_GRID_RANGE_SELECT, self.OnColSelected)
        self.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.OnCellSelected)
        self.Sheet.Bind(wx.EVT_CHAR, self.OnKeyPress)

        self.Bind(wx.grid.EVT_GRID_LABEL_RIGHT_CLICK, self.OnLabelRightClick)

        if self.ExportData.H5 == []:
            self.Buttonsave.Disable()
            self.Show(True)
        else:
            self.ReadH5()

    def OnLabelRightClick(self, evt):
        print "OnLabelLeftClick: (%d,%d) %s\n" % (evt.GetRow(),
                                                  evt.GetCol(),
                                                  evt.GetPosition())
        menu = wx.Menu()
        Rename = wx.NewId()
        menu.Append(Rename, 'Rename Colome')
        self.PopupMenu(menu)

    def Filter(self, txt):
        Filtre = self.TextFilter.GetValue()
        eph = self.DragEph.GetItems()
        os.chdir(self.info.PathEph)
        eph = ls.glob("".join(['*', Filtre, '*.eph']))
        eph.sort()
        self.DragEph.SetItems(eph)

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
            self.NbCol = MaxColNumber
        else:
            self.NbCol = 9
        self.Col.SetValue(self.NbCol)
        self.text = ['']
        for i, col in enumerate(NoEpmtyCol):

            ColName = SheetColName[i]
            self.Sheet.SetColLabelValue(col, ColName)
            self.text.append(ColName)
            self.BoxFactor.SetItems(self.text)
            ColValue = SheetValue[i]
            if len(ColValue) > 35:
                self.Sheet.SetNumberRows(len(ColValue))
                self.NbRow = len(ColValue)
            else:
                self.NbRow = 30
            self.Row.SetValue(self.NbRow)
            for row, value in enumerate(ColValue):
                self.Sheet.SetCellValue(row, col, value)
            file.close()

    def OnKeyPress(self, event):
        if event.GetKeyCode() == 3:
            self.Sheet.Copy()
        elif event.GetKeyCode() == 22:
            self.Sheet.Paste()
        else:

            event.Skip()

    def CopySelection(self, event):
        self.Sheet.Copy()

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
        Data = ReadSheet(self.Sheet, self.NbRow, self.NbCol)
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

    def SelectEphFolder(self, event):
        self.TextFilter.Enable()
        wx.InitAllImageHandlers()
        dlg = wx.DirDialog(None, "select Folder", defaultPath=os.getcwd(
        ), style=wx.DD_DEFAULT_STYLE | wx.DD_CHANGE_DIR)
        retour = dlg.ShowModal()
        self.info.PathEph = dlg.GetPath()
        dlg.Show(True)
        dlg.Destroy()
        os.chdir(self.info.PathEph)
        eph = ls.glob('*.eph')
        eph.sort()
        self.DragEph.SetItems(eph)
        if retour == wx.ID_OK:
            self.TextEph.SetLabel(self.info.PathEph)

    def OnCellSelected(self, event):
        row = event.GetRow()
        col = event.GetCol()
        CellValue = self.Sheet.GetCellValue(row, col)
        self.CellContentTxt.SetLabel(CellValue)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyPress)
        event.Skip()

    def Sort(self, event):
        ColItems = self.ColData.GetItems()
        ColItems.sort()
        self.ColData.SetItems(ColItems)

    def Drag(self, event):
        # dplacement des eph mis dans la list vers la colone selectinee. De
        # plus le nombrre de ligne est teste et augmente si il le faut.
        ColItems = self.ColData.GetItems()
        Col = self.Sheet.GetSelectedCols()
        self.Sheet.Clear()
        ActualRow = self.Row.GetValue()
        # test du nombres de lignes
        if len(ColItems) > ActualRow:
            NewRowNeeded = len(ColItems) - ActualRow
            for i in range(NewRowNeeded):
                self.Sheet.AppendRows()
            self.Row.SetValue(len(ColItems))
            self.NbRow = self.Row.GetValue()
        for row, it in enumerate(ColItems):
            self.Sheet.SetCellValue(row, Col[0], it)
        # desactivation des boutons
        self.MoveUpButton.Disable()
        self.MoveDownButton.Disable()
        self.AddButton.Disable()
        self.RmButton.Disable()
        self.OKButton.Disable()
        self.Sheet.Enable()
        self.SortButton.Disable()
        self.Sheet.DeselectCol(Col[0])
        self.ColName.SetLabel('Select One Colon')
        self.ColData.SetItems('')

    def AddCol(self, event):
        ColItems = self.ColData.GetItems()
        EphItems = self.DragEph.GetItems()
        EphSelected = self.DragEph.GetSelections()
        for i in EphSelected:
            EphFile = [self.info.PathEph]
            EphFile.append('\\')
            EphFile.append(EphItems[i])
            ColItems.append("".join(EphFile))

        self.ColData.SetItems(ColItems)
        self.DragEph.SetItems(EphItems)
        self.TextFilter.SetValue('')
        os.chdir(self.info.PathEph)
        eph = ls.glob('*.eph')
        eph.sort()
        self.DragEph.SetItems(eph)

    def RmCol(self, event):
        ColItems = self.ColData.GetItems()
        EphItems = self.DragEph.GetItems()
        EphSelected = self.ColData.GetSelections()
        for i in EphSelected:
            EphItems.append(ColItems[i])
            ColItems[i] = 'rm'
        mark = 1
        while mark == 1:
            try:
                ColItems.remove('rm')
            except:
                mark = 2
        EphItems.sort()
        self.ColData.SetItems(ColItems)
        # self.DragEph.SetItems(EphItems)

    def MoveUp(self, event):
        Items = self.ColData.GetItems()
        ItemsSelected = self.ColData.GetSelections()
        if ItemsSelected[0] != 0:
            for i in ItemsSelected:
                Tmp = Items[i]
                TmpPrev = Items[i - 1]
                Items[i] = TmpPrev
                Items[i - 1] = Tmp
        else:
            dlg = wx.MessageDialog(
                None, 'You cannot move Up with the first line', style=wx.OK)
            retour = dlg.ShowModal()
            dlg.Destroy()
        self.ColData.SetItems(Items)

    def MoveDown(self, event):
        Items = self.ColData.GetItems()
        ItemsSelected = self.ColData.GetSelections()
        if ItemsSelected[0] != len(Items) - 1:
            for i in ItemsSelected:
                Tmp = Items[i]
                TmpPrev = Items[i + 1]
                Items[i] = TmpPrev
                Items[i + 1] = Tmp
        else:
            dlg = wx.MessageDialog(
                None, 'You cannot move Down with the last line', style=wx.OK)
            retour = dlg.ShowModal()
            dlg.Destroy()
        self.ColData.SetItems(Items)

    def EphSelected(self, event):
        self.MoveUpButton.Disable()
        self.MoveDownButton.Disable()
        self.AddButton.Enable()
        self.RmButton.Disable()
        Col = self.Sheet.GetSelectedCols()
        if Col == []:
            self.OKButton.Disable()
            self.AddButton.Disable()
        else:
            self.AddButton.Enable()
            self.OKButton.Enable()
            self.Sheet.Disable()

    def ColSelected(self, event):
        self.MoveUpButton.Enable()
        self.MoveDownButton.Enable()
        self.AddButton.Disable()
        self.RmButton.Enable()
        self.OKButton.Enable()
        self.Sheet.Disable()
        self.SortButton.Enable()

    def OnColSelected(self, event):
        Col = self.Sheet.GetSelectedCols()
        name = ['Colon Name : ']
        if Col != []:
            if len(Col) == 1:
                name.append(self.Sheet.GetColLabelValue(Col[0]))
                self.ColName.SetLabel("".join(name))
                self.ColName.SetExtraStyle(wx.ALIGN_CENTRE)
                rows = self.Sheet.GetNumberRows()
                CellValue = []
                for r in range(rows):
                    value = self.Sheet.GetCellValue(r, Col[0])
                    if value != '':
                        CellValue.append(value)
                self.ColData.SetItems(CellValue)
                if self.DragEph.GetSelections() != []:
                    self.AddButton.Enable()
                    self.OKButton.Enable()
                else:
                    self.AddButton.Disable()
                self.Sheet.Disable()
            else:
                self.ColName.SetLabel('SELECT ONE COLON !!!')

    def OnClose(self, event):
        if self.save:
            self.Destroy()
            self.ExportData.Show(True)
        else:
            dlg = wx.MessageDialog(self,
                                   "Do you really want to close this application?",
                                   "Confirm Exit",
                                   wx.OK | wx.CANCEL | wx.ICON_QUESTION)
            result = dlg.ShowModal()
            dlg.Destroy()
            if result == wx.ID_OK:
                self.Destroy()
                self.ExportData.Show(True)

    def PasteClip(self, event):
        self.Sheet.Paste()

    def DefFactor(self, event):
        self.Data = ReadSheet(self.Sheet, self.NbRow, self.NbCol)
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

    def RenameCol(self, event):
        NewName = self.NewName.GetLabel()
        # -1 car il y a un espace vide au debut
        col = self.BoxFactor.GetCurrentSelection() - 1
        self.Sheet.SetColLabelValue(col, NewName)
        self.text[col + 1] = NewName
        self.BoxFactor.SetItems(self.text)
        self.NewName.SetLabel("")

    def ClearSheet(self, event):
        self.Sheet.Clear()

    def ClearAllSheet(self, event):
        self.Sheet.SelectAll()
        self.Sheet.Clear()

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
        self.BoxFactor.SetItems(self.text)
        self.NbCol = self.Col.GetValue()
