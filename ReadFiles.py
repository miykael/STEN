

class ReadSheet:

    def __init__(self, Sheet, NbRow, NbCol):
        self.Value = []
        self.NoEmptyCol = []
        self.NoEpmptyRow = []
        NoEmptyRow = []
        for c in range(NbCol):
            Col = []
            for r in range(NbRow):
                Col.append(Sheet.GetCellValue(r, c))
            # Non empty Colon
            if Col.count('') != len(Col):
                self.NoEmptyCol.append(c)

        for r in range(NbRow):
            Row = []
            for c in range(NbCol):
                Row.append(Sheet.GetCellValue(r, c))

            # Non empty Colon
            if Row.count('') != len(Row):
                NoEmptyRow.append(r)
        for c in self.NoEmptyCol:
            Col = []
            for r in NoEmptyRow:
                cell = Sheet.GetCellValue(r, c)
                Col.append(cell)
            self.Value.append(Col)
        self.NoEmptyRow = NoEmptyRow
