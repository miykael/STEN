import wx
import tables
import Stat


class ReturnInfomation:

    def __init__(self, chemin):
        text = []
        info = Stat.Anova(chemin, self)
        info.file.close()
        file = tables.openFile(chemin, mode='r')
        formule = ['R-FORMULA : aov(']
        formule.append(info.Formule)
        formule.append(')\n\n')
        text.append("".join(formule))
        Within = ['Within FACTOR(S) NAME(S)[LEVELS] : ']
        Factor = file.getNode('/Names/Within')
        Factor = Factor.read()
        Level = file.getNode('/Info/Level')
        Level = Level.read()

        if Factor:
            for i, f in enumerate(Factor):
                Within.append(', ')
                Within.append(f)
                Within.append(' [')
                Within.append(str(Level[i]))
                Within.append(']')
            Within.remove(', ')
            Within.append('\n\n')
            text.append("".join(Within))

        NameBetween = file.getNode('/Names/Between')
        BetweenFactor = file.getNode('/Model/Between')
        BetweenFactor = BetweenFactor.read()
        NameBetween = NameBetween.read()
        if NameBetween:
            between = ['BETWEEN FACTOR(S) NAME(S): ']
            for i, f in enumerate(NameBetween):
                between.append(', ')
                tmp = []
                try:
                    BetweenLevel = str(int(BetweenFactor[:, i].max()))
                except:
                    BetweenLevel = str(int(BetweenFactor.max()))
                tmp.append(f)
                tmp.append('[')
                tmp.append(BetweenLevel)
                tmp.append(']')
                between.append("".join(tmp))
            between.remove(', ')
            between.append('\n\n')
            text.append("".join(between))
        Namecov = file.getNode('/Names/Covariate')
        Namecov = Namecov.read()
        if Namecov:
            cov = ['COVARIATE NAME(S): ']
            for f in Namecov:
                cov.append(', ')
                cov.append(f)
            cov.remove(', ')
            cov.append('\n\n')
            text.append("".join(cov))
            self.CovariatePresent = True
        else:
            self.CovariatePresent = False
        ErrorEph = file.getNode('/Error/Eph')
        ErrorEph = ErrorEph.read()
        if ErrorEph:
            error = 'ALL EPH FILES ARE READED !!!'
        else:
            error = ['This Eph Files have a problem : \n']
            n = 0
            for i, e in enumerate(ErrorEph):
                if n == 10:
                    n = 0
                    error.append(', ')
                    error.append(e)
                    error.append('\n')
                else:
                    error.append(', ')
                    error.append(e)
            error.remove(', ')
            txt = "".join(error)
            txt = txt.replace(',', '\n')
            dlg = wx.MessageDialog(
                None, txt, "Error Eph Files", wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()
            dlg.Destroy()
        self.text = text
        file.close()
