import wx
class PanelAnovaWave(wx.Panel):
	def __init__(self,conteneur):
		wx.Panel.__init__(self,parent = conteneur)
                FrameSizer = wx.BoxSizer(wx.VERTICAL)
		#definition des OutPut
		self.Param = True
		self.PostHocParam = True
		self.Analyse = None
		self.Alpha = 0.05
		self.AlphaPostHoc= None
		self.PtsConseq = 1
		self.Clust=1
		self.ClustPostHoc=1
		self.PtsConseqPostHoc= 1
		self.PostHoc = False
		self.AnovaPerformed= True
		self.Iter=1000
		self.IterPostHoc=1000
		self.Spi=None
		# on cree les panels 1 a 1
		###
		FrameSizer.AddSpacer(10)
		# Panel Anova perormed
		PanelAnova=wx.Panel(self,-1)
		SizerAnova=wx.BoxSizer(wx.VERTICAL)
		self.AnovaCheckBox=wx.CheckBox(PanelAnova,12,"Performed ANOVA")
		SizerAnova.Add(self.AnovaCheckBox,0,wx.TOP)
		PanelAnova.SetSizer(SizerAnova)
		FrameSizer.Add(PanelAnova,0,wx.EXPAND)
		FrameSizer.AddSpacer(10)
		self.AnovaCheckBox.SetValue(True)
		####
                self.PanelInfoAnova=wx.Panel(self,-1)
		SizerInfoAnova=wx.BoxSizer(wx.VERTICAL)
		############
		#panel pour les parma /non param
		PanelParamAll= wx.Panel(self.PanelInfoAnova,-1)
		SizerParamAll = wx.BoxSizer(wx.HORIZONTAL)
		PanelParam = wx.Panel(PanelParamAll,-1)
		SizerParam = wx.BoxSizer(wx.VERTICAL)
		# creation des radio button
		self.RadioParam = wx.RadioButton(PanelParam, 10, 'Parametric Test', (-1, -1), style=wx.RB_GROUP)
		SizerParam.Add(self.RadioParam,0,wx.TOP)
		SizerParam.AddSpacer(5)
		self.RadioNonParam = wx.RadioButton(PanelParam, 10, 'Non-Parametric Test (Bootstraping)', (-1, -1))
		SizerParam.Add(self.RadioNonParam,0,wx.TOP)
		# lie les sizer au panel
		PanelParam.SetSizer(SizerParam)
                SizerParamAll.Add(PanelParam,0,wx.EXPAND)
                # Bouton iteration
                self.PanelIter=wx.Panel(PanelParamAll,-1)
                IterSizer = wx.BoxSizer(wx.VERTICAL)
		IterText=wx.StaticText(self.PanelIter,-1,label = "Iteration",style=wx.ALIGN_CENTER)
		IterSizer.Add(IterText,0,wx.EXPAND)
		IterSizer.AddSpacer(5)
		self.IterInput=wx.TextCtrl(self.PanelIter,4,value=str(self.Iter),style=wx.TE_CENTRE)
		IterSizer.Add(self.IterInput,0,wx.EXPAND)
		self.PanelIter.SetSizer(IterSizer)
		SizerParamAll.Add(self.PanelIter,0,wx.EXPAND)
		PanelParamAll.SetSizer(SizerParamAll)
		# on mets le panel de fichier dans le sizer de la frame
		SizerInfoAnova.Add(PanelParamAll,0,wx.EXPAND)
		SizerInfoAnova.AddSpacer(10)
		#############
		# panel avec les infos Statitstique (alpha,pts conseq)
                PanelInfo = wx.Panel(self.PanelInfoAnova,-1)
		SizerInfo=wx.BoxSizer(wx.HORIZONTAL)
		
		PanelAlpha=wx.Panel(PanelInfo,-1)
		SizerAlpha=wx.BoxSizer(wx.VERTICAL)
		AlphaText=wx.StaticText(PanelAlpha,-1,label = "Alpha Value",style=wx.ALIGN_CENTER)
		SizerAlpha.Add(AlphaText,0,wx.EXPAND)
                self.AlphaInput=wx.TextCtrl(PanelAlpha,1,value=str(self.Alpha),style=wx.TE_CENTRE)
		SizerAlpha.Add(self.AlphaInput,0,wx.EXPAND)
		PanelAlpha.SetSizer(SizerAlpha)
		SizerInfo.Add(PanelAlpha)
		SizerInfo.AddSpacer(10)
		
		PanelPtsConseq=wx.Panel(PanelInfo,-1)
		SizerPtsConseq=wx.BoxSizer(wx.VERTICAL)
                PtsConseqText=wx.StaticText(PanelPtsConseq,-1,label = "Consecutive Time Frame",style=wx.ALIGN_CENTER)
		SizerPtsConseq.Add(PtsConseqText,0,wx.EXPAND)
                self.PtsConsequInput=wx.TextCtrl(PanelPtsConseq,2,value=str(self.PtsConseq),style=wx.TE_CENTRE)
		SizerPtsConseq.Add(self.PtsConsequInput,0,wx.EXPAND)
		PanelPtsConseq.SetSizer(SizerPtsConseq)
                SizerInfo.Add(PanelPtsConseq)
		SizerInfo.AddSpacer(10)
		
		self.PanelClust=wx.Panel(PanelInfo,-1)
		SizerPtsClust=wx.BoxSizer(wx.VERTICAL)
                ClustText=wx.StaticText(self.PanelClust,-1,label = "Cluster Size (Electrodes)",style=wx.ALIGN_CENTER)
		SizerPtsClust.Add(ClustText,0,wx.EXPAND)
		self.ClustInput=wx.TextCtrl(self.PanelClust,3,value=str(self.Clust),style=wx.TE_CENTRE)
		SizerPtsClust.Add(self.ClustInput,0,wx.EXPAND)
		self.PanelClust.SetSizer(SizerPtsClust)
		SizerInfo.Add(self.PanelClust)
		SizerInfo.AddSpacer(10)
		self.PanelClust.Disable()

		# lie les sizer au panel
		PanelInfo.SetSizer(SizerInfo)
		# on mets le panel de fichier dans le sizer de la frame
		SizerInfoAnova.Add(PanelInfo,0,wx.EXPAND)
		SizerInfoAnova.AddSpacer(10)
		self.PanelInfoAnova.SetSizer(SizerInfoAnova)
		FrameSizer.Add(self.PanelInfoAnova,0,wx.EXPAND)
		#############
		# Panel Post-Hoc
		PanelPostHoc = wx.Panel(self,-1)
		SizerPostHoc=wx.BoxSizer(wx.VERTICAL)
		self.PostHocCheckBox=wx.CheckBox(PanelPostHoc,13,"Post hoc analysis (all possible t-test only on ANOVA not on ANCOVA)")
		SizerPostHoc.Add(self.PostHocCheckBox,0,wx.EXPAND)
		SizerPostHoc.AddSpacer(10)
		# on mets le panel de fichier dans le sizer de la frame
		FrameSizer.Add(PanelPostHoc,0,wx.EXPAND)
		# lie les sizer au panel
		PanelPostHoc.SetSizer(SizerPostHoc)
		# lie le sizer de la fenetre a la fenetre
                #####
		# Panel Info Post-Hoc
                self.PanelInfoPostHoc=wx.Panel(self,-1)
                SizerInfoPostHoc=wx.BoxSizer(wx.VERTICAL)
                ##########################
                # panel Param
                PanelParamAll= wx.Panel(self.PanelInfoPostHoc,-1)
		SizerParamAll = wx.BoxSizer(wx.HORIZONTAL)
                PanelParam = wx.Panel(PanelParamAll,-1)
		SizerParam = wx.BoxSizer(wx.VERTICAL)
		self.RadioParamPostHoc = wx.RadioButton(PanelParam, 11, 'Parametric Test', (-1, -1), style=wx.RB_GROUP)
		SizerParam.Add(self.RadioParamPostHoc,0,wx.EXPAND)
		SizerParam.AddSpacer(5)
		self.RadioNonParamPostHoc = wx.RadioButton(PanelParam, 11, 'Non-Parametric Test (Bootstraping)', (-1, -1))
		SizerParam.Add(self.RadioNonParamPostHoc,0,wx.EXPAND)
		# lie les sizer au panel
		PanelParam.SetSizer(SizerParam)
                SizerParamAll.Add(PanelParam,0,wx.EXPAND)
                self.PanelIterPostHoc=wx.Panel(PanelParamAll,-1)
                IterSizer = wx.BoxSizer(wx.VERTICAL)
		IterText=wx.StaticText(self.PanelIterPostHoc,-1,label = "Iteration",style=wx.ALIGN_CENTER)
		IterSizer.Add(IterText,0,wx.EXPAND)
		IterSizer.AddSpacer(5)
		self.IterInputPostHoc=wx.TextCtrl(self.PanelIterPostHoc,8,value="",style=wx.TE_CENTRE)
		IterSizer.Add(self.IterInputPostHoc,0,wx.EXPAND)
		self.PanelIterPostHoc.SetSizer(IterSizer)
		SizerParamAll.Add(self.PanelIterPostHoc,0,wx.EXPAND)
		PanelParamAll.SetSizer(SizerParamAll)
		# on mets le panel de fichier dans le sizer de la frame
		SizerInfoPostHoc.Add(PanelParamAll,0,wx.EXPAND)
                SizerInfoPostHoc.AddSpacer(10)
                #############
                # panel avec les infos Statitstique (alpha,pts conseq, Clust)
		PanelInfo = wx.Panel(self.PanelInfoPostHoc,-1)
		SizerInfo=wx.BoxSizer(wx.HORIZONTAL)
		
		PanelAlpha=wx.Panel(PanelInfo,-1)
		SizerAlpha=wx.BoxSizer(wx.VERTICAL)
		AlphaText=wx.StaticText(PanelAlpha,-1,label = "Alpha Value",style=wx.ALIGN_CENTER)
		SizerAlpha.Add(AlphaText,0,wx.EXPAND)
                self.AlphaInputPostHoc=wx.TextCtrl(PanelAlpha,5,value=str(self.Alpha),style=wx.TE_CENTRE)
		SizerAlpha.Add(self.AlphaInputPostHoc,0,wx.EXPAND)
		PanelAlpha.SetSizer(SizerAlpha)
		SizerInfo.Add(PanelAlpha)
		SizerInfo.AddSpacer(10)
		
		PanelPtsConseq=wx.Panel(PanelInfo,-1)
		SizerPtsConseq=wx.BoxSizer(wx.VERTICAL)
                PtsConseqText=wx.StaticText(PanelPtsConseq,-1,label = "Consecutive Time Frame",style=wx.ALIGN_CENTER)
		SizerPtsConseq.Add(PtsConseqText,0,wx.EXPAND)
                self.PtsConsequInputPostHoc=wx.TextCtrl(PanelPtsConseq,6,value=str(self.PtsConseq),style=wx.TE_CENTRE)
		SizerPtsConseq.Add(self.PtsConsequInputPostHoc,0,wx.EXPAND)
		PanelPtsConseq.SetSizer(SizerPtsConseq)
                SizerInfo.Add(PanelPtsConseq)
		SizerInfo.AddSpacer(10)
		
		self.PanelClustPostHoc=wx.Panel(PanelInfo,-1)
		SizerPtsClust=wx.BoxSizer(wx.VERTICAL)
                ClustText=wx.StaticText(self.PanelClustPostHoc,-1,label = "Cluster Size (Electrodes)",style=wx.ALIGN_CENTER)
		SizerPtsClust.Add(ClustText,0,wx.EXPAND)
		self.ClustInputPostHoc=wx.TextCtrl(self.PanelClustPostHoc,7,value=str(self.Clust),style=wx.TE_CENTRE)
		SizerPtsClust.Add(self.ClustInputPostHoc,0,wx.EXPAND)
		self.PanelClustPostHoc.SetSizer(SizerPtsClust)
		SizerInfo.Add(self.PanelClustPostHoc)
		SizerInfo.AddSpacer(10)
		self.PanelClustPostHoc.Disable()
		
		# lie les sizer au panel
		PanelInfo.SetSizer(SizerInfo)
		
		# on mets le panel POstHoc dans le sizer de la frame
		SizerInfoPostHoc.Add(PanelInfo,0,wx.EXPAND)
		self.PanelInfoPostHoc.SetSizer(SizerInfoPostHoc)
		FrameSizer.Add(self.PanelInfoPostHoc,0,wx.EXPAND)
		FrameSizer.AddSpacer(10)
		self.PanelInfoPostHoc.Disable()
                ##################
		#panel analyse (gfp, all elelctordes ou both)
		PanelAnalyse = wx.Panel(self,-1)
		SizerAnalyse=wx.BoxSizer(wx.VERTICAL)
		#choix de l'analyse
		TextAnalyse=wx.StaticText(PanelAnalyse,-1,label = "Choose your Analyse",style=wx.CENTRE)
		text=["","All Electrodes","GFP Only","Both"]
		self.BoxAnalyse=wx.ComboBox(PanelAnalyse, 9, choices=text,style=wx.CB_READONLY)
		SizerAnalyse.Add(TextAnalyse,0,wx.CENTRE)
		SizerAnalyse.Add(self.BoxAnalyse,0,wx.EXPAND)
		# lie les sizer au panel
		PanelAnalyse.SetSizer(SizerAnalyse)
		FrameSizer.Add(PanelAnalyse,0,wx.EXPAND)
		self.SetSizer(FrameSizer)
                self.Show(True)
                self.PanelIter.Disable()
                self.PanelIterPostHoc.Disable()

                #panel SPI (donner le ficheir SPI pour le calcul des pts conseq)
		self.PanelSpi = wx.Panel(self,-1)
		SizerSpi=wx.GridBagSizer()
                # selection Spi file
                TextSpi=wx.StaticText(self.PanelSpi,-1,label = "Select xyz File",style=wx.ALIGN_CENTER)
                SizerSpi.Add(TextSpi,(0,0),(1,5),wx.EXPAND)
		self.TextSpi=wx.TextCtrl(self.PanelSpi,-1,value="",style =wx.TE_READONLY)
		self.TextSpi.SetBackgroundColour(wx.WHITE)
		SizerSpi.Add(self.TextSpi,(1,0),(1,4),wx.EXPAND)
		ButtonSpi=wx.Button(self.PanelSpi,14,label ="Browse")
		SizerSpi.Add(ButtonSpi,(1,5),(1,1),wx.EXPAND)
		self.PanelSpi.Disable()
		# lie les sizer au panel
		self.PanelSpi.SetSizer(SizerSpi)
		SizerSpi.AddGrowableCol(0)
		# on mets le panel de fichier dans le sizer de la frame
		FrameSizer.Add(self.PanelSpi,0,wx.EXPAND)
		self.PanelSpi.Disable()
                
                
		wx.EVT_RADIOBUTTON(self,10,self.ClickParam)
		wx.EVT_RADIOBUTTON(self,11,self.ClickParamPostHoc)
		#wx.EVT_RADIOBOX(self,2,self.ClickParam)
		wx.EVT_COMBOBOX(self,9,self.AnalyseChoose)
		# alpha
		wx.EVT_TEXT(self,1,self.AlphaChoose)
		wx.EVT_TEXT(self,5,self.AlphaChoosePostHoc)
		
		# Pts Conseq
		wx.EVT_TEXT(self,2,self.PtsConseqChoose)
		wx.EVT_TEXT(self,6,self.PtsConseqChoosePostHoc)
		# Pts Conseq
		wx.EVT_TEXT(self,3,self.ClustChoose)
		wx.EVT_TEXT(self,7,self.ClustChoosePostHoc)
		# iteration
		wx.EVT_TEXT(self,4,self.IterChoose)
		wx.EVT_TEXT(self,8,self.IterChoosePostHoc)
		
		wx.EVT_CHECKBOX(self,12,self.AnovaCheck)
                wx.EVT_CHECKBOX(self,13,self.PostHocCheck)

                # browse xyz
		wx.EVT_BUTTON(self,14,self.XYZChoose)
		
		
	def ClickParam(self,event):
		self.Param=self.RadioParam.GetValue()
		if self.Param:
                        self.PanelIter.Disable()       
                else:
                        self.PanelIter.Enable()
		
	def ClickParamPostHoc(self,event):
		self.PostHocParam=self.RadioParamPostHoc.GetValue()
		if self.PostHocParam:
                        self.PanelIterPostHoc.Disable()
                else:
                        Iter=self.IterInput.GetValue()
                        self.IterInputPostHoc.SetValue(str(Iter))
                        self.PanelIterPostHoc.Enable()
                        self.IterPostHoc=Iter
                        
			
	def AnalyseChoose(self,event):
                self.Analyse=self.BoxAnalyse.GetValue()
                self.BoxAnalyse.SetBackgroundColour(wx.WHITE)
                if self.Analyse !='GFP Only':
                        self.PanelClust.Enable()
                        if self.PostHoc:
                                self.PanelClustPostHoc.Enable()
                        if self.Clust!=1 or self.ClustPostHoc!=1:
                                self.PanelSpi.Enable()
                        else:
                                self.PanelSpi.Disable()
                                
                else:
                        self.PanelClust.Disable()
                        self.PanelClustPostHoc.Disable()
                        self.PanelSpi.Disable()
                        
	def AlphaChoose(self,event):
		alpha=self.AlphaInput.GetValue()
		if alpha!="":
			try:
				alpha=float(alpha)
				self.Alpha=alpha
			except:
				dlg = wx.MessageDialog(self, "float number for alpha", style = wx.OK)
				retour = dlg.ShowModal()
				dlg.Destroy()
		if self.PostHocCheckBox.GetValue():
                        self.AlphaInputPostHoc.SetValue(str(alpha))
                        
				
	def AlphaChoosePostHoc(self,event):
		alpha=self.AlphaInputPostHoc.GetValue()
		if alpha!="":
			try:
				alpha=float(alpha)
				self.AlphaPostHoc=alpha
			except:
				dlg = wx.MessageDialog(self, "float number for alpha", style = wx.OK)
				retour = dlg.ShowModal()
				dlg.Destroy()
			
				
		
	def PtsConseqChoose(self,event):
		pts_consec=self.PtsConsequInput.GetValue()
		if pts_consec!="":
			try:
				pts_consec=int(pts_consec)
				self.PtsConseq=pts_consec
			except:
				dlg = wx.MessageDialog(self, "Integer number for Consecutive Time Frame", style = wx.OK)
				retour = dlg.ShowModal()
				dlg.Destroy()
		if self.PostHocCheckBox.GetValue():
                        self.PtsConsequInputPostHoc.SetValue(str(pts_consec))
				
	def PtsConseqChoosePostHoc(self,event):
		pts_consec=self.PtsConsequInputPostHoc.GetValue()
		if pts_consec!="":
			try:
				pts_consec=int(pts_consec)
				self.PtsConseqPostHoc=int(pts_consec)
			except:
				dlg = wx.MessageDialog(self, "Integer number for Consecutive Time Frame", style = wx.OK)
				retour = dlg.ShowModal()
				dlg.Destroy()
				
	def PostHocCheck(self,event):
                self.PostHoc=self.PostHocCheckBox.GetValue()
                if self.PostHocCheckBox.GetValue():
                        self.PanelInfoPostHoc.Enable()
                        alpha=self.AlphaInput.GetValue()
                        clust=self.ClustInput.GetValue()
                        pts_consec=self.PtsConsequInput.GetValue()
                        self.PtsConsequInputPostHoc.SetValue(str(pts_consec))
                        self.AlphaInputPostHoc.SetValue(str(alpha))
                        if self.Analyse =='GFP Only' or self.Analyse== None:
                                self.PanelClustPostHoc.Disable()
                        else:
                                self.PanelClustPostHoc.Enable()
                                self.ClustInputPostHoc.SetValue(str(clust))
                        self.ClustPostHoc=int(clust)
                        self.AlphaPostHoc=float(alpha)
                        self.PtsConseqPostHoc=int(pts_consec)
                        if self.PostHocParam:
                                self.PanelIterPostHoc.Disable()
                        else:
                                Iter=self.IterInput.GetValue()
                                self.IterInputPostHoc.SetValue(str(Iter))
                                self.PanelIterPostHoc.Enable()
                                self.IterPostHoc=int(Iter)
                else:
                        self.PanelInfoPostHoc.Disable()
	def AnovaCheck(self,evemt):
                self.AnovaPerformed=self.AnovaCheckBox.GetValue()
                if self.AnovaCheckBox.GetValue():
                        self.PanelInfoAnova.Enable()
                else:
                        self.PanelInfoAnova.Disable()
        def IterChoose(self,event):
		Iter=self.IterInput.GetValue()
		if Iter!="":
			try:
				Iter=int(Iter)
				self.Iter=Iter
			except:
				dlg = wx.MessageDialog(self, "Integer number for Iteration", style = wx.OK)
				retour = dlg.ShowModal()
				dlg.Destroy()
		if self.PostHocCheckBox.GetValue():
                        self.IterInputPostHoc.SetValue(str(Iter))
                        
				
	def IterChoosePostHoc(self,event):
		Iter=self.IterInputPostHoc.GetValue()
		if Iter!="":
			try:
				Iter=int(Iter)
				self.IterPostHoc=Iter
			except:
				dlg = wx.MessageDialog(self, "Integer number for Iteration in Post-Hoc Panel", style = wx.OK)
				retour = dlg.ShowModal()
				dlg.Destroy()
				
	def ClustChoose(self,event):
		clust=self.ClustInput.GetValue()
		if clust!="":
			try:
				clust=int(clust)
				self.Clust=clust
                                if clust==1:
                                        self.PanelSpi.Disable()
                                else:
                                        self.PanelSpi.Enable()
			except:
				dlg = wx.MessageDialog(self, "Integer number for Cluster size", style = wx.OK)
				retour = dlg.ShowModal()
				dlg.Destroy()
		if self.PostHocCheckBox.GetValue():
                        self.ClustInputPostHoc.SetValue(str(clust))

				
	def ClustChoosePostHoc(self,event):
		clust=self.ClustInputPostHoc.GetValue()
		if clust!="":
			try:
				clust=int(clust)
				self.ClustPostHoc=clust
				if clust==1:
                                        self.PanelSpi.Disable()
                                else:
                                        self.PanelSpi.Enable()
			except:
				dlg = wx.MessageDialog(self, "Integer number for Cluster size", style = wx.OK)
				retour = dlg.ShowModal()
				dlg.Destroy()
	def XYZChoose(self,event):
		wx.InitAllImageHandlers()
		dlg = wx.FileDialog(None, "select XYZ file",wildcard = "*.xyz",style = wx.OPEN)
		retour = dlg.ShowModal()
		chemin = dlg.GetPath()
		fichier = dlg.GetFilename()
		self.TextSpi.SetLabel(chemin)
		self.Spi=chemin
		dlg.Destroy()
		dlg.Show(True)


                        
class PanelAnovaIS(wx.Panel):
	def __init__(self,conteneur):
		wx.Panel.__init__(self,parent = conteneur)
                FrameSizer = wx.BoxSizer(wx.VERTICAL)
		#definition des OutPut
		self.Param = True
		self.PostHocParam = True
		self.Alpha = 0.05
		self.AlphaPostHoc = None
		self.PtsConseq = 1
		self.PtsConseqPostHoc = 1
		self.Clust= 1
		self.ClustPostHoc = None
		self.Spi=None
		self.PostHoc = False
		self.AnovaPerformed = True
		self.Iter=1000
		self.IterPostHoc=None
		# on cree les panels 1 a 1
                # Panel Anova perormed
                FrameSizer.AddSpacer(10)
		PanelAnova=wx.Panel(self,-1)
		SizerAnova=wx.BoxSizer(wx.VERTICAL)
		self.AnovaCheckBox=wx.CheckBox(PanelAnova,1,"Performed ANOVA")
		SizerAnova.Add(self.AnovaCheckBox,0,wx.EXPAND)
		PanelAnova.SetSizer(SizerAnova)
		FrameSizer.Add(PanelAnova,0,wx.EXPAND)
		FrameSizer.AddSpacer(10)
		self.AnovaCheckBox.SetValue(True)
		####
                self.PanelInfoAnova=wx.Panel(self,-1)
		SizerInfoAnova=wx.BoxSizer(wx.VERTICAL)
		############
                #panel pour les parma /non param
		PanelParamAll= wx.Panel(self.PanelInfoAnova,-1)
		SizerParamAll = wx.BoxSizer(wx.HORIZONTAL)
		PanelParam = wx.Panel(PanelParamAll,-1)
		SizerParam = wx.BoxSizer(wx.VERTICAL)
		# creation des radio button
		self.RadioParam = wx.RadioButton(PanelParam, 1, 'Parametric Test', (-1, -1), style=wx.RB_GROUP)
		SizerParam.Add(self.RadioParam,0,wx.TOP)
		SizerParam.AddSpacer(5)
		self.RadioNonParam = wx.RadioButton(PanelParam, 1, 'Non-Parametric Test (Bootstraping)', (-1, -1))
		SizerParam.Add(self.RadioNonParam,0,wx.TOP)
		# lie les sizer au panel
		PanelParam.SetSizer(SizerParam)
                SizerParamAll.Add(PanelParam,0,wx.EXPAND)
                # Bouton iteration
                self.PanelIter=wx.Panel(PanelParamAll,-1)
                IterSizer = wx.BoxSizer(wx.VERTICAL)
		IterText=wx.StaticText(self.PanelIter,-1,label = "Iteration",style=wx.ALIGN_CENTER)
		IterSizer.Add(IterText,0,wx.EXPAND)
		IterSizer.AddSpacer(5)
		self.IterInput=wx.TextCtrl(self.PanelIter,4,value=str(self.Iter),style=wx.TE_CENTRE)
		IterSizer.Add(self.IterInput,0,wx.EXPAND)
		self.PanelIter.SetSizer(IterSizer)
		SizerParamAll.Add(self.PanelIter,0,wx.EXPAND)
		PanelParamAll.SetSizer(SizerParamAll)
		# on mets le panel de fichier dans le sizer de la frame
		SizerInfoAnova.Add(PanelParamAll,0,wx.EXPAND)
		SizerInfoAnova.AddSpacer(10)
                ############
		# panel avec les infos Statitstique (alpha,pts conseq, Clust)
                PanelInfo = wx.Panel(self.PanelInfoAnova,-1)
		SizerInfo=wx.BoxSizer(wx.HORIZONTAL)
		
		PanelAlpha=wx.Panel(PanelInfo,-1)
		SizerAlpha=wx.BoxSizer(wx.VERTICAL)
		AlphaText=wx.StaticText(PanelAlpha,-1,label = "Alpha Value",style=wx.ALIGN_CENTER)
		SizerAlpha.Add(AlphaText,0,wx.EXPAND)
                self.AlphaInput=wx.TextCtrl(PanelAlpha,1,value=str(self.Alpha),style=wx.TE_CENTRE)
		SizerAlpha.Add(self.AlphaInput,0,wx.EXPAND)
		PanelAlpha.SetSizer(SizerAlpha)
		SizerInfo.Add(PanelAlpha)
		SizerInfo.AddSpacer(10)
		
		PanelPtsConseq=wx.Panel(PanelInfo,-1)
		SizerPtsConseq=wx.BoxSizer(wx.VERTICAL)
                PtsConseqText=wx.StaticText(PanelPtsConseq,-1,label = "Consecutive Time Frame",style=wx.ALIGN_CENTER)
		SizerPtsConseq.Add(PtsConseqText,0,wx.EXPAND)
                self.PtsConsequInput=wx.TextCtrl(PanelPtsConseq,2,value=str(self.PtsConseq),style=wx.TE_CENTRE)
		SizerPtsConseq.Add(self.PtsConsequInput,0,wx.EXPAND)
		PanelPtsConseq.SetSizer(SizerPtsConseq)
                SizerInfo.Add(PanelPtsConseq)
		SizerInfo.AddSpacer(10)
		
		self.PanelClust=wx.Panel(PanelInfo,-1)
		SizerPtsClust=wx.BoxSizer(wx.VERTICAL)
                ClustText=wx.StaticText(self.PanelClust,-1,label = "Cluster Size (Voxels)",style=wx.ALIGN_CENTER)
		SizerPtsClust.Add(ClustText,0,wx.EXPAND)
		self.ClustInput=wx.TextCtrl(self.PanelClust,3,value=str(self.Clust),style=wx.TE_CENTRE)
		SizerPtsClust.Add(self.ClustInput,0,wx.EXPAND)
		self.PanelClust.SetSizer(SizerPtsClust)
		SizerInfo.Add(self.PanelClust)
		SizerInfo.AddSpacer(10)
		# lie les sizer au panel
		PanelInfo.SetSizerAndFit(SizerInfo)
		SizerInfo.SetSizeHints(PanelInfo)
		# on mets le panel de fichier dans le sizer de la frame
		SizerInfoAnova.Add(PanelInfo,0,wx.EXPAND)
		self.PanelInfoAnova.SetSizer(SizerInfoAnova)
		FrameSizer.Add(self.PanelInfoAnova,0,wx.EXPAND)
		FrameSizer.AddSpacer(10)
		#############
		# Panel Post-Hoc
		PanelPostHoc = wx.Panel(self,-1)
		SizerPostHoc=wx.BoxSizer(wx.VERTICAL)
		self.PostHocCheckBox=wx.CheckBox(PanelPostHoc,2,"Post hoc analysis (all possible t-test only on ANOVA not on ANCOVA)")
		SizerPostHoc.Add(self.PostHocCheckBox,0,wx.EXPAND)
		SizerPostHoc.AddSpacer(10)
		# on mets le panel de fichier dans le sizer de la frame
		FrameSizer.Add(PanelPostHoc,0,wx.EXPAND)
		# lie les sizer au panel
		PanelPostHoc.SetSizer(SizerPostHoc)
		#########
		# lie le sizer de la fenetre a la fenetre
                #####
		# Panel Info Post-Hoc
                self.PanelInfoPostHoc=wx.Panel(self,-1)
                SizerInfoPostHoc=wx.BoxSizer(wx.VERTICAL)
                # panel Param
                PanelParamAll= wx.Panel(self.PanelInfoPostHoc,-1)
		SizerParamAll = wx.BoxSizer(wx.HORIZONTAL)
                PanelParam = wx.Panel(PanelParamAll,-1)
		SizerParam = wx.BoxSizer(wx.VERTICAL)
		self.RadioParamPostHoc = wx.RadioButton(PanelParam, 2, 'Parametric Test', (-1, -1), style=wx.RB_GROUP)
		SizerParam.Add(self.RadioParamPostHoc,0,wx.EXPAND)
		SizerParam.AddSpacer(5)
		self.RadioNonParamPostHoc = wx.RadioButton(PanelParam, 2, 'Non-Parametric Test (Bootstraping)', (-1, -1))
		SizerParam.Add(self.RadioNonParamPostHoc,0,wx.EXPAND)
		# lie les sizer au panel
		PanelParam.SetSizer(SizerParam)
                SizerParamAll.Add(PanelParam,0,wx.EXPAND)
                self.PanelIterPostHoc=wx.Panel(PanelParamAll,-1)
                IterSizer = wx.BoxSizer(wx.VERTICAL)
		IterText=wx.StaticText(self.PanelIterPostHoc,-1,label = "Iteration",style=wx.ALIGN_CENTER)
		IterSizer.Add(IterText,0,wx.EXPAND)
		IterSizer.AddSpacer(5)
		self.IterInputPostHoc=wx.TextCtrl(self.PanelIterPostHoc,8,value="",style=wx.TE_CENTRE)
		IterSizer.Add(self.IterInputPostHoc,0,wx.EXPAND)
		self.PanelIterPostHoc.SetSizer(IterSizer)
		SizerParamAll.Add(self.PanelIterPostHoc,0,wx.EXPAND)
		PanelParamAll.SetSizer(SizerParamAll)
		# on mets le panel de fichier dans le sizer de la frame
		SizerInfoPostHoc.Add(PanelParamAll,0,wx.EXPAND)
                SizerInfoPostHoc.AddSpacer(10)

		#############
                PanelInfo = wx.Panel(self.PanelInfoPostHoc,-1)
		SizerInfo=wx.BoxSizer(wx.HORIZONTAL)
		
		PanelAlpha=wx.Panel(PanelInfo,-1)
		SizerAlpha=wx.BoxSizer(wx.VERTICAL)
		AlphaText=wx.StaticText(PanelAlpha,-1,label = "Alpha Value",style=wx.ALIGN_CENTER)
		SizerAlpha.Add(AlphaText,0,wx.EXPAND)
                self.AlphaInputPostHoc=wx.TextCtrl(PanelAlpha,5,value=str(self.Alpha),style=wx.TE_CENTRE)
		SizerAlpha.Add(self.AlphaInputPostHoc,0,wx.EXPAND)
		PanelAlpha.SetSizer(SizerAlpha)
		SizerInfo.Add(PanelAlpha)
		SizerInfo.AddSpacer(10)
		
		PanelPtsConseq=wx.Panel(PanelInfo,-1)
		SizerPtsConseq=wx.BoxSizer(wx.VERTICAL)
                PtsConseqText=wx.StaticText(PanelPtsConseq,-1,label = "Consecutive Time Frame",style=wx.ALIGN_CENTER)
		SizerPtsConseq.Add(PtsConseqText,0,wx.EXPAND)
                self.PtsConsequInputPostHoc=wx.TextCtrl(PanelPtsConseq,6,value=str(self.PtsConseq),style=wx.TE_CENTRE)
		SizerPtsConseq.Add(self.PtsConsequInputPostHoc,0,wx.EXPAND)
		PanelPtsConseq.SetSizer(SizerPtsConseq)
                SizerInfo.Add(PanelPtsConseq)
		SizerInfo.AddSpacer(10)
		
		self.PanelClustPostHoc=wx.Panel(PanelInfo,-1)
		SizerPtsClust=wx.BoxSizer(wx.VERTICAL)
                ClustText=wx.StaticText(self.PanelClustPostHoc,-1,label = "Cluster Size (Electrodes)",style=wx.ALIGN_CENTER)
		SizerPtsClust.Add(ClustText,0,wx.EXPAND)
		self.ClustInputPostHoc=wx.TextCtrl(self.PanelClustPostHoc,7,value=str(self.Clust),style=wx.TE_CENTRE)
		SizerPtsClust.Add(self.ClustInputPostHoc,0,wx.EXPAND)
		self.PanelClustPostHoc.SetSizer(SizerPtsClust)
		SizerInfo.Add(self.PanelClustPostHoc)
		SizerInfo.AddSpacer(10)
		self.PanelClustPostHoc.Disable()

		
                # lie les sizer au panel
		PanelInfo.SetSizer(SizerInfo)
		SizerInfo.SetSizeHints(PanelInfo)
		# on mets le panel de fichier dans le sizer de la frame
		SizerInfoPostHoc.Add(PanelInfo,0,wx.EXPAND)
		self.PanelInfoPostHoc.SetSizer(SizerInfoPostHoc)
		FrameSizer.Add(self.PanelInfoPostHoc,0,wx.EXPAND)
		FrameSizer.AddSpacer(10)
		#######
                #panel SPI (donner le ficheir SPI pour le calcul des pts conseq)
		self.PanelSpi = wx.Panel(self,-1)
		SizerSpi=wx.GridBagSizer()
                # selection Spi file
                TextSpi=wx.StaticText(self.PanelSpi,-1,label = "Select Spi File",style=wx.ALIGN_CENTER)
                SizerSpi.Add(TextSpi,(0,0),(1,5),wx.EXPAND)
		self.TextSpi=wx.TextCtrl(self.PanelSpi,-1,value="",style =wx.TE_READONLY)
		self.TextSpi.SetBackgroundColour(wx.WHITE)
		SizerSpi.Add(self.TextSpi,(1,0),(1,4),wx.EXPAND)
		ButtonSpi=wx.Button(self.PanelSpi,1,label ="Browse")
		SizerSpi.Add(ButtonSpi,(1,5),(1,1),wx.EXPAND)
		self.PanelSpi.Disable()
		# lie les sizer au panel
		self.PanelSpi.SetSizer(SizerSpi)
		SizerSpi.AddGrowableCol(0)
		# on mets le panel de fichier dans le sizer de la frame
		FrameSizer.Add(self.PanelSpi,0,wx.EXPAND)
		# lie le sizer de la fenetre a la fenetre
		self.SetSizer(FrameSizer)
		self.PanelInfoPostHoc.Disable()
		self.Show(True)
		self.PanelIter.Disable()
                self.PanelIterPostHoc.Disable()
		# param
		wx.EVT_RADIOBUTTON(self,1,self.ClickParam)
		wx.EVT_RADIOBUTTON(self,2,self.ClickParamPostHoc)
		# browse spi
		wx.EVT_BUTTON(self,1,self.SpiChoose)
		# alpha
		wx.EVT_TEXT(self,1,self.AlphaChoose)
		wx.EVT_TEXT(self,5,self.AlphaChoosePostHoc)
		# Pts Conseq
		wx.EVT_TEXT(self,2,self.PtsConseqChoose)
		wx.EVT_TEXT(self,6,self.PtsConseqChoosePostHoc)
		# Pts Conseq
		wx.EVT_TEXT(self,3,self.ClustChoose)
		wx.EVT_TEXT(self,7,self.ClustChoosePostHoc)
		# Post Hoc
		wx.EVT_CHECKBOX(self,2,self.PostHocCheck)
		wx.EVT_CHECKBOX(self,1,self.AnovaCheck)

		# iteration
		wx.EVT_TEXT(self,4,self.IterChoose)
		wx.EVT_TEXT(self,8,self.IterChoosePostHoc)

		
		
	def ClickParam(self,event):
		self.Param=self.RadioParam.GetValue()
		if self.Param:
                        self.PanelIter.Disable()       
                else:
                        self.PanelIter.Enable()
		
	def ClickParamPostHoc(self,event):
		self.PostHocParam=self.RadioParamPostHoc.GetValue()
		if self.PostHocParam:
                        self.PanelIterPostHoc.Disable()
                else:
                        Iter=self.IterInput.GetValue()
                        self.IterInputPostHoc.SetValue(str(Iter))
                        self.PanelIterPostHoc.Enable()
                        self.IterPostHoc=Iter
			
	def SpiChoose(self,event):
		wx.InitAllImageHandlers()
		dlg = wx.FileDialog(None, "select Spi file",wildcard = "*.spi",style = wx.OPEN)
		retour = dlg.ShowModal()
		chemin = dlg.GetPath()
		fichier = dlg.GetFilename()
		self.TextSpi.SetLabel(chemin)
		self.Spi=chemin
		dlg.Destroy()
		dlg.Show(True)
		
	def AlphaChoose(self,event):
		alpha=self.AlphaInput.GetValue()
		if alpha!="":
			try:
				alpha=float(alpha)
				self.Alpha=alpha
			except:
				dlg = wx.MessageDialog(self, "float number for alpha", style = wx.OK)
				retour = dlg.ShowModal()
				dlg.Destroy()
		if self.PostHocCheckBox.GetValue():
                        self.AlphaInputPostHoc.SetValue(str(alpha))
                        

	def AlphaChoosePostHoc(self,event):
		alpha=self.AlphaInputPostHoc.GetValue()
		if alpha!="":
			try:
				alpha=float(alpha)
				self.AlphaPostHoc=alpha
			except:
				dlg = wx.MessageDialog(self, "float number for alpha", style = wx.OK)
				retour = dlg.ShowModal()
				dlg.Destroy()		
		
	def PtsConseqChoose(self,event):
		pts_consec=self.PtsConsequInput.GetValue()
		if pts_consec!="":
			try:
				pts_consec=int(pts_consec)
				self.PtsConseq=pts_consec
			except:
				dlg = wx.MessageDialog(self, "Integer number for Consecutive Time Frame", style = wx.OK)
				retour = dlg.ShowModal()
				dlg.Destroy()
                if self.PostHocCheckBox.GetValue():
                        self.PtsConsequInputPostHoc.SetValue(str(pts_consec))

		
	def PtsConseqChoosePostHoc(self,event):
		pts_consec=self.PtsConsequInputPostHoc.GetValue()
		if pts_consec!="":
			try:
				pts_consec=int(pts_consec)
				self.PtsConseqPostHoc=int(pts_consec)
			except:
				dlg = wx.MessageDialog(self, "Integer number for Consecutive Time Frame", style = wx.OK)
				retour = dlg.ShowModal()
				dlg.Destroy()


	def ClustChoose(self,event):
		clust=self.ClustInput.GetValue()
		if clust!="":
			try:
				clust=int(clust)
				self.Clust=clust
				if clust == 1:
                                        self.PanelSpi.Disable()
                                else:
                                       self.PanelSpi.Enable() 
			except:
				dlg = wx.MessageDialog(self, "Integer number for Cluster size", style = wx.OK)
				retour = dlg.ShowModal()
				dlg.Destroy()
		if self.PostHocCheckBox.GetValue():
                        self.ClustInputPostHoc.SetValue(str(clust))

				
	def ClustChoosePostHoc(self,event):
		clust=self.ClustInputPostHoc.GetValue()
		if clust!="":
			try:
				clust=int(clust)
				self.ClustPostHoc=int(clust)
				if clust == 1:
                                        self.PanelSpi.Disable()
                                else:
                                       self.PanelSpi.Enable() 
			except:
				dlg = wx.MessageDialog(self, "Integer number for Cluster size", style = wx.OK)
				retour = dlg.ShowModal()
				dlg.Destroy()
				
				
        def PostHocCheck(self,event):
                self.PostHoc=self.PostHocCheckBox.GetValue()
                if self.PostHocCheckBox.GetValue():
                        self.PanelInfoPostHoc.Enable()
                        alpha=self.AlphaInput.GetValue()
                        clust=self.ClustInput.GetValue()
                        pts_consec=self.PtsConsequInput.GetValue()
                        self.PtsConsequInputPostHoc.SetValue(str(pts_consec))
                        self.AlphaInputPostHoc.SetValue(str(alpha))
                        self.ClustInputPostHoc.SetValue(str(clust))
                        self.AlphaPostHoc=float(alpha)
                        self.PtsConseqPostHoc=int(pts_consec)
                        self.ClustPostHoc=int(clust)
                        if self.PostHocParam:
                                self.PanelIterPostHoc.Disable()
                        else:
                                Iter=self.IterInput.GetValue()
                                self.IterInputPostHoc.SetValue(str(Iter))
                                self.PanelIterPostHoc.Enable()
                                self.IterPostHoc=int(Iter)
                        
                else:
                        self.PanelInfoPostHoc.Disable()
	def AnovaCheck(self,event):
                self.AnovaPerformed=self.AnovaCheckBox.GetValue()
                if self.AnovaCheckBox.GetValue():
                        self.PanelInfoAnova.Enable()
                else:
                        self.PanelInfoAnova.Disable()
        def IterChoose(self,event):
		Iter=self.IterInput.GetValue()
		if Iter!="":
			try:
				Iter=int(Iter)
				self.Iter=Iter
			except:
				dlg = wx.MessageDialog(self, "Integer number for Iteration", style = wx.OK)
				retour = dlg.ShowModal()
				dlg.Destroy()
		if self.PostHocCheckBox.GetValue():
                        self.IterInputPostHoc.SetValue(str(Iter))
                        
				
	def IterChoosePostHoc(self,event):
		Iter=self.IterInputPostHoc.GetValue()
		if Iter!="":
			try:
				Iter=int(Iter)
				self.IterPostHoc=Iter
			except:
				dlg = wx.MessageDialog(self, "Integer number for Iteration in Post-Hoc Panel", style = wx.OK)
				retour = dlg.ShowModal()
				dlg.Destroy()


		


class PanelManovaWave(wx.Panel):
	def __init__(self,conteneur):
		wx.Panel.__init__(self,parent = conteneur)
                FrameSizer = wx.BoxSizer(wx.VERTICAL)
		#definition des OutPut
		self.Param = True
		self.Analyse = None
		self.Alpha = 0.05
		self.PostHoc = False
		# on cree les panels 1 a 1
		############
		#panel pour les parma /non param
		PanelParam = wx.Panel(self,-1)
		SizerParam = wx.BoxSizer(wx.VERTICAL)
		# creation des radio button
		self.RadioParam = wx.RadioButton(PanelParam, 1, 'Parametric Test', (-1, -1), style=wx.RB_GROUP)
		SizerParam.Add(self.RadioParam,0,wx.EXPAND)
		SizerParam.AddStretchSpacer()
		self.RadioNonParam = wx.RadioButton(PanelParam, 1, 'Non-Parametric Test (Bootstraping)', (-1, -1))
		SizerParam.Add(self.RadioNonParam,0,wx.EXPAND)
		# lie les sizer au panel
		PanelParam.SetSizerAndFit(SizerParam)
		# on mets le panel de fichier dans le sizer de la frame
		FrameSizer.Add(PanelParam,0,wx.EXPAND)
		FrameSizer.AddStretchSpacer()
		################
		#panel analyse (gfp, all elelctordes ou both)
		PanelAnalyse = wx.Panel(self,-1)
		SizerAnalyse=wx.BoxSizer(wx.VERTICAL)
		#choix des facteurs
		TextAnalyse=wx.StaticText(PanelAnalyse,-1,label = "Choose your Analyse")
		text=["","All Electrodes","GFP Only","Both"]
		self.BoxAnalyse=wx.ComboBox(PanelAnalyse, 1, choices=text,style=wx.CB_READONLY)
		SizerAnalyse.Add(TextAnalyse,0,wx.EXPAND)
		SizerAnalyse.Add(self.BoxAnalyse,0,wx.EXPAND)
		# lie les sizer au panel
		PanelAnalyse.SetSizerAndFit(SizerAnalyse)
		# on mets le panel de fichier dans le sizer de la frame
		FrameSizer.Add(PanelAnalyse,0,wx.EXPAND)
		FrameSizer.AddStretchSpacer()
		#############
		# panel avec les infos Statitstique (alpha)
		PanelInfo = wx.Panel(self,-1)
		SizerInfo=wx.GridBagSizer()
		AlphaText=wx.StaticText(PanelInfo,-1,label = "Alpha Value",style=wx.ALIGN_CENTER)
		SizerInfo.Add(AlphaText,(0,0),(1,1),wx.EXPAND)
		self.AlphaInput=wx.TextCtrl(PanelInfo,1,value=str(self.Alpha))
		SizerInfo.Add(self.AlphaInput,(1,0),(1,1),wx.EXPAND)
		# lie les sizer au panel
		PanelInfo.SetSizerAndFit(SizerInfo)
		SizerInfo.SetSizeHints(PanelInfo)
		# on mets le panel de fichier dans le sizer de la frame
		FrameSizer.Add(PanelInfo,0,wx.EXPAND)
		FrameSizer.AddStretchSpacer()
		#############
		# Panel Post-Hoc
		PanelPostHoc = wx.Panel(self,-1)
		SizerPostHoc=wx.BoxSizer(wx.VERTICAL)
		self.PostHocCheckBox=wx.CheckBox(PanelPostHoc,1,"Post hoc analysis (all possible 2 by 1 MANOVA)")
		SizerPostHoc.Add(self.PostHocCheckBox,0,wx.EXPAND)
		# on mets le panel de fichier dans le sizer de la frame
		FrameSizer.Add(PanelPostHoc,0,wx.EXPAND)
		# lie les sizer au panel
		PanelPostHoc.SetSizerAndFit(SizerPostHoc)
		# lie le sizer de la fenetre a la fenetre
		#FrameSizer.AddGrowableRow(0)
		self.SetSizerAndFit(FrameSizer)
		
		self.Show(True)
		
		wx.EVT_RADIOBUTTON(self,1,self.ClickParam)
		#wx.EVT_RADIOBOX(self,2,self.ClickParam)
		wx.EVT_COMBOBOX(self,1,self.AnalyseChoose)
		# alpha
		wx.EVT_TEXT(self,1,self.AlphaChoose)
		# Pts Conseq
		wx.EVT_CHECKBOX(self,1,self.PostHocCheck)
		
	def ClickParam(self,event):
		self.Param=self.RadioParam.GetValue()
			
	def AnalyseChoose(self,event):
		self.Analyse=self.BoxAnalyse.GetValue()
	def AlphaChoose(self,event):
		alpha=self.AlphaInput.GetValue()
		if alpha!="":
			try:
				alpha=float(alpha)
				self.Alpha=alpha
			except:
				dlg = wx.MessageDialog(self, "float number for alpha", style = wx.OK)
				retour = dlg.ShowModal()
				dlg.Destroy()
			
	def PostHocCheck(self,evemt):
		self.PostHoc=self.PostHocCheckBox.GetValue()

		
class PanelManovaIS(wx.Panel):
	def __init__(self,conteneur):
		wx.Panel.__init__(self,parent = conteneur)
                FrameSizer = wx.BoxSizer(wx.VERTICAL)
		#definition des OutPut
		self.Param = True
		self.Alpha = 0.05
		self.PostHoc = False
		# on cree les panels 1 a 1
		############
		#panel pour les parma /non param
		PanelParam = wx.Panel(self,-1)
		SizerParam = wx.BoxSizer(wx.VERTICAL)
		# creation des radio button
		self.RadioParam = wx.RadioButton(PanelParam, 1, 'Parametric Test', (-1, -1), style=wx.RB_GROUP)
		SizerParam.Add(self.RadioParam,0,wx.EXPAND)
		SizerParam.AddStretchSpacer()
		self.RadioNonParam = wx.RadioButton(PanelParam, 1, 'Non-Parametric Test (Bootstraping)', (-1, -1))
		SizerParam.Add(self.RadioNonParam,0,wx.EXPAND)
		# lie les sizer au panel
		PanelParam.SetSizerAndFit(SizerParam)
		# on mets le panel de fichier dans le sizer de la frame
		FrameSizer.Add(PanelParam,0,wx.EXPAND)
		FrameSizer.AddStretchSpacer()
		#############
		# panel avec les infos Statitstique (alpha)
		PanelInfo = wx.Panel(self,-1)
		SizerInfo=wx.GridBagSizer()
		AlphaText=wx.StaticText(PanelInfo,-1,label = "Alpha Value",style=wx.ALIGN_CENTER)
		SizerInfo.Add(AlphaText,(0,0),(1,1),wx.EXPAND)
		self.AlphaInput=wx.TextCtrl(PanelInfo,1,value=str(self.Alpha))
		SizerInfo.Add(self.AlphaInput,(1,0),(1,1),wx.EXPAND)
		# lie les sizer au panel
		PanelInfo.SetSizerAndFit(SizerInfo)
		SizerInfo.SetSizeHints(PanelInfo)
		# on mets le panel de fichier dans le sizer de la frame
		FrameSizer.Add(PanelInfo,0,wx.EXPAND)
		FrameSizer.AddStretchSpacer()
		#############
		# Panel Post-Hoc
		PanelPostHoc = wx.Panel(self,-1)
		SizerPostHoc=wx.BoxSizer(wx.VERTICAL)
		self.PostHocCheckBox=wx.CheckBox(PanelPostHoc,1,"Post hoc analysis (all possible 2 by 1 MANOVA)")
		SizerPostHoc.Add(self.PostHocCheckBox,0,wx.EXPAND)
		# on mets le panel de fichier dans le sizer de la frame
		FrameSizer.Add(PanelPostHoc,0,wx.EXPAND)
		# lie les sizer au panel
		PanelPostHoc.SetSizerAndFit(SizerPostHoc)
		# lie le sizer de la fenetre a la fenetre
		#FrameSizer.AddGrowableRow(0)
		self.SetSizerAndFit(FrameSizer)
		
		self.Show(True)
		
		wx.EVT_RADIOBUTTON(self,1,self.ClickParam)
		# alpha
		wx.EVT_TEXT(self,1,self.AlphaChoose)
		# Pts Conseq
		wx.EVT_CHECKBOX(self,1,self.PostHocCheck)
		
	def ClickParam(self,event):
		self.Param=self.RadioParam.GetValue()
	def AlphaChoose(self,event):
		alpha=self.AlphaInput.GetValue()
		if alpha!="":
			try:
				alpha=float(alpha)
				self.Alpha=alpha
			except:
				dlg = wx.MessageDialog(self, "float number for alpha", style = wx.OK)
				retour = dlg.ShowModal()
				dlg.Destroy()
			
	def PostHocCheck(self,evemt):
		self.PostHoc=self.PostHocCheckBox.GetValue()
