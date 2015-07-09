import wx
import RightPanel
import LeftPanel
import Stat
import tables
import PostStat
import os
import time
import shutil
""" Fonction principale lançant STEN composer de 4 Modules
1) LeftPanel information de gauche dans la fenetre principale de sten (entree des donnes, H5,...)
2) Right Panle information de droite dans léa fenetre principale (Entree des aparmetre anova oui/non, alpha, ...
3) Stat module de calcul des statistiques (ANOVA Ttest) parametric ou non
4)PostStat module de correction pour les test multiple (morphologie mathematique), ecriture des résultats
"""
class principale(wx.Frame):
		#####################################################################################################
		#Initialisation de l'interface lancement des modules LeftPanel, RightPanel, creation du bouton start
		#####################################################################################################
        def __init__(self):
                wx.Frame.__init__(self, None, -1, title = "STEN 1.0", size = (1000,500))
                FrameSizer=wx.BoxSizer(wx.VERTICAL)
                PanelData=wx.Panel(self,-1)
                DataSizer=wx.BoxSizer(wx.HORIZONTAL)
                ### Left Panel
                self.LeftPanel=LeftPanel.info(PanelData,self)
                # self.H5 = file contenant toutes les données
                DataSizer.Add(self.LeftPanel,0,wx.EXPAND)
                ### Right panel
                self.Tab = wx.Notebook(PanelData,1, style=wx.NB_TOP)
                self.AnovaWave = RightPanel.PanelAnovaWave(self.Tab)
                self.AnovaIS = RightPanel.PanelAnovaIS(self.Tab)
                #self.ManovaWave = RightPanel.PanelManovaWave(self.Tab)
                #self.ManovaIS = RightPanel.PanelManovaIS(self.Tab) 
                self.Tab.AddPage(self.AnovaWave, 'ANOVA on Wave/GFP')
                self.Tab.AddPage(self.AnovaIS, 'ANOVA  on Brain Space')
                #self.Tab.AddPage(self.ManovaWave, 'MANOVA on Wave/GFP')
                #self.Tab.AddPage(self.ManovaIS, 'MANOVA  on Brain Space')
                self.AnovaWave.SetFocus()
                DataSizer.Add(self.Tab,0,wx.EXPAND)
                PanelData.SetSizer(DataSizer)
                FrameSizer.Add(PanelData,0,wx.EXPAND)
                # start button
                PanelStart=wx.Panel(self,-1)
                StartSizer=wx.BoxSizer(wx.HORIZONTAL)
                self.StartButton=wx.Button(PanelStart,1,label ="Start Calculation")
                StartSizer.Add(self.StartButton,1,wx.EXPAND)
                PanelStart.SetSizer(StartSizer)
                FrameSizer.Add(PanelStart,0,wx.EXPAND)
                self.SetSizerAndFit(FrameSizer)
                #sizer.SetSizeHints(self)
                self.Show(True)
                ####
                wx.EVT_BUTTON(self,1,self.Start)
                self.Bind(wx.EVT_CLOSE,self.OnClose)
                #####################################################################
                # function quand on ferme, demande si ok de fermer, puis detruit tout
                #####################################################################
        def OnClose(self,event):	
                dlg = wx.MessageDialog(self,"Do you really want to close this application?","Confirm Exit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
                result = dlg.ShowModal()
                dlg.Destroy()
                if result == wx.ID_OK:
                        self.Destroy()
                        quit()
        #################################################################################################################
        # Lancement de l'interface
        # 1) Test si toute les parametres sont ok
        # 2) Test si dans le H5 il y a deja des resultats si oui on demande si faut faire 3 ou on passe directement a 4
        # 3) Calcul de l'ANOVA
        # 4) Post Traitement correction test multiple (mathematiical morphologie) + ecriture des résultats
        #################################################################################################################
        
        def Start(self,event):
                """ lancement de l'interface, 1) test des variables 2) calcul anova 3) post treatment 4) ecriture vrb, reuslt """
				
                self.Cancel=False
                self.StartButton.Disable()
                ProgressTxt=['Calculation Step :']
                self.mark=0
                self.InputTest()

                
                #####################################################################################
                # test si tout est entree correctement
                ####################################################################################
                if self.InputError!=[]:
                        dlg = wx.MessageDialog(self,"\n".join(self.InputError), style = wx.OK)
                        retour = dlg.ShowModal()
                        dlg.Destroy()
                        self.StartButton.Enable()
                else:
                        ###########################################################################
                        # si Anova est coche on regarde si il y a des resultats Anova dans le H5
                        ##########################################################################
                        if self.AnovaCheck:
                                # test sur le fichier
                                file=tables.openFile(self.H5,'r+')
                                try:
                                        Param=file.getNode('/Info/Param')
                                        Param=Param.read()
                                        file.removeNode('/Info/Param')
                                        file.createArray('/Info','Param',self.AnovaParam)
                                except:
                                        file.createArray('/Info','Param',self.AnovaParam)
                                        Param=self.AnovaParam
                                        
                                
                                GFPDataTest=file.listNodes('/Result/Anova/GFP')
                                AllDataTest=file.listNodes('/Result/Anova/All')
                                TextDataRecording=['Results are fund in H5 file for Anova :\n\n']
                                if GFPDataTest!=[]:# il y des resultats GFP
                                        if self.AnovaParam and Param:
                                                TextDataRecording=['Results are fund in H5 file for Parametric Anova :\n\n']    
                                        elif self.AnovaParam==False and Param==False:
                                                TextDataRecording=['Results are fund in H5 file for Non-Parametric Anova :\n\n']    
                                        if "".join(TextDataRecording)!='Results are fund in H5 file for Anova :\n\n':
                                                GFPTime=file.getNode('/Result/Anova/GFP/ElapsedTime')
                                                GFPTime=GFPTime.read()
                                                shape=file.getNode('/Info/ShapeGFP')
                                                shape=shape.read()
                                                TextDataRecording.append(' - GFP on (')
                                                TextDataRecording.append(str(shape[0]))
                                                TextDataRecording.append(' Time Frame)\n')
                                                TextDataRecording.append('Estimated Caculation time : ')
                                                TextDataRecording.append(GFPTime)
                                if AllDataTest!=[]:# il y des resultats All
                                        if self.AnovaParam and Param:
                                                TextDataRecording=['Results are fund in H5 file for Parametric Anova :\n\n']    
                                        elif self.AnovaParam==False and Param==False:
                                                TextDataRecording=['Results are fund in H5 file for Non-Parametric Anova :\n\n']    
                                        if "".join(TextDataRecording)!='Results are fund in H5 file for Anova :\n\n':
                                                AllTime=file.getNode('/Result/Anova/All/ElapsedTime')
                                                AllTime=AllTime.read()
                                                shape=file.getNode('/Info/Shape')
                                                shape=shape.read()
                                                if shape[1]<500: #waveform
                                                        TextDataRecording.append('- WaveForm on (')
                                                        TextDataRecording.append(str(shape[0]))
                                                        TextDataRecording.append(' Time Frame, ')
                                                        TextDataRecording.append(str(shape[1]))
                                                        TextDataRecording.append(' Electrodes)\n')
                                                        TextDataRecording.append('Estimated Caculation time : ')
                                                        TextDataRecording.append(AllTime)
                                                else:
                                                        TextDataRecording.append('- Inverse Space on (')
                                                        TextDataRecording.append(str(shape[0]))
                                                        TextDataRecording.append(' Time Frame, ')
                                                        TextDataRecording.append(str(shape[1]))
                                                        TextDataRecording.append(' Voxels)\n')
                                                        TextDataRecording.append('Estimated Caculation time : ')
                                                        TextDataRecording.append(AllTime)
                               

                                if  "".join(TextDataRecording)!='Results are fund in H5 file for Anova :\n\n':
                                        TextDataRecording.append('\n Do you want to recalculate the ANOVA (YES) or just applying correction on results (NO)?')
                                        dlg = wx.MessageDialog(None,"".join(TextDataRecording),"Analyse Data", wx.YES_NO|wx.YES_DEFAULT|wx.ICON_QUESTION)
                                        dlg.SetSize((800,800))
                                        response = dlg.ShowModal()
                                        if response==wx.ID_YES:
                                                CalculAnova=True
                                                if GFPDataTest!=[]:
                                                        file.removeNode('/Result/Anova/GFP',recursive=True) # rm all data
                                                        file.createGroup('/Result/Anova','GFP')
                                                if AllDataTest!=[]:
                                                        file.removeNode('/Result/Anova/All',recursive=True) # rm all data
                                                        file.createGroup('/Result/Anova','All')
                                        else:
                                                CalculAnova=False
                                        dlg.Destroy()
                                                
                                else:
                                        CalculAnova=True
                                        if GFPDataTest!=[]:
                                                file.removeNode('/Result/Anova/GFP',recursive=True) # rm all data
                                                file.createGroup('/Result/Anova','GFP')
                                        if AllDataTest!=[]:
                                                file.removeNode('/Result/Anova/All',recursive=True) # rm all data
                                                file.createGroup('/Result/Anova','All')
                                file.close()
                                
                        ############################################################################
                        #si postHoc est coche on regarde si il y a des resultats postHoc dans le H5
                        ############################################################################
                        
                        if self.PostHoc:
                                # test sur le fichier POSTHOC
                                file=tables.openFile(self.H5,'r+')
                                GFPDataTest=file.listNodes('/Result/PostHoc/GFP')
                                AllDataTest=file.listNodes('/Result/PostHoc/All')
                                TextDataRecording=['Results are fund in H5 file for PostHoc :\n\n']
                                if GFPDataTest!=[]:# il y des resultats GFP
                                        GFPTime=file.getNode('/Result/PostHoc/GFP/ElapsedTime')
                                        GFPTime=GFPTime.read()
                                        shape=file.getNode('/Info/ShapeGFP')
                                        shape=shape.read()
                                        TextDataRecording.append(' - GFP on (')
                                        TextDataRecording.append(str(shape[0]))
                                        TextDataRecording.append(' Time Frame)\n')
                                        TextDataRecording.append('Estimated Caculation time : ')
                                        TextDataRecording.append(GFPTime)
                                if AllDataTest!=[]:# il y des resultats All
                                        AllTime=file.getNode('/Result/PostHoc/All/ElapsedTime')
                                        AllTime=AllTime.read()
                                        shape=file.getNode('/Info/Shape')
                                        shape=shape.read()
                                        if shape[1]<500: #waveform
                                                TextDataRecording.append('- WaveForm on (')
                                                TextDataRecording.append(str(shape[0]))
                                                TextDataRecording.append(' Time Frame, ')
                                                TextDataRecording.append(str(shape[1]))
                                                TextDataRecording.append(' Electrodes)\n')
                                                TextDataRecording.append('Estimated Caculation time : ')
                                                TextDataRecording.append(AllTime)
                                        else:
                                                TextDataRecording.append('- Inverse Space on (')
                                                TextDataRecording.append(str(shape[0]))
                                                TextDataRecording.append(' Time Frame, ')
                                                TextDataRecording.append(str(shape[1]))
                                                TextDataRecording.append(' Voxels)\n')
                                                TextDataRecording.append('Estimated Caculation time : ')
                                                TextDataRecording.append(AllTime)

                                if  "".join(TextDataRecording)!='Results are fund in H5 file PostHoc :\n\n':
                                        TextDataRecording.append('\n Do you want to recalculate the PostHoc (YES) or just applying correction on results (NO)?')
                                        dlg = wx.MessageDialog(None,"".join(TextDataRecording),"Analyse Data", wx.YES_NO|wx.YES_DEFAULT|wx.ICON_QUESTION)
                                        dlg.SetSize((800,800))
                                        response = dlg.ShowModal()
                                        if response==wx.ID_YES:
                                                CalculPostHoc=True
                                                if GFPDataTest!=[]:
                                                        file.removeNode('/Result/PostHoc/GFP',recursive=True) # rm all data
                                                        file.createGroup('/Result/PostHoc','GFP')
                                                if AllDataTest!=[]:
                                                        file.removeNode('/Result/PostHoc/All',recursive=True) # rm all data
                                                        file.createGroup('/Result/PostHoc','All')
                                        else:
                                                CalculPostHoc=False
                                        dlg.Destroy()
                                                
                                else:
                                        CalculPostHoc=True
                                
                                file.close()
                        ########################################################################################    
                        #creation Result Folder named STEN, within estimator and Anova and POstHoc 
                        #######################################################################################
                        ResultName='STEN'
                        PathResult=[self.PathResult,ResultName]
                        PathResult=os.path.abspath("/".join(PathResult))
                        try:
                                os.mkdir(PathResult)
                        except:
                                os.chdir('c:/')
                                shutil.rmtree(PathResult)
                                os.mkdir(PathResult)        
                        ################################
                        ######## Calcul NOVA et Post-hoc
                        ################################
                        
                        #################################################      
                        # calcul Anova sur wave et/ou GFP et inversement
                        #################################################
                        
                        if self.AnalyseType=='ANOVA on Wave/GFP':
                                
                                if self.AnovaCheck:# Anova est selectione
                                        if CalculAnova:# l'utilisatuer a demande de faire le cacule au poitn ci-dessus
                                                self.Wave=Stat.Anova(self.H5,self)
                                                if self.AnovaParam:# parametric
                                                        if self.Type=="Both":
                                                                start=time.clock()
                                                                self.Wave.Param()
                                                                end=time.clock()
                                                                elapsed=end-start
                                                                self.ExtractTime(elapsed)
                                                                ProgressTxt.append("".join(['Parametric Anova Elapsed Time (All Electrodes) : ',self.TimeTxt]))
                                                                AllTime=self.Wave.file.createArray('/Result/Anova/All','ElapsedTime',self.TimeTxt)
                                                                start=time.clock()
                                                                self.Wave.Param(DataGFP=True)
                                                                end=time.clock()
                                                                elapsed=end-start
                                                                self.ExtractTime(elapsed)
                                                                ProgressTxt.append("".join(['Parametric Anova Elapsed Time (GFP) : ',self.TimeTxt]))
                                                                GFPTime=self.Wave.file.createArray('/Result/Anova/GFP','ElapsedTime',self.TimeTxt)
                                                        elif self.Type=="GFP Only":
                                                                start=time.clock()
                                                                self.Wave.Param(DataGFP=True,)
                                                                end=time.clock()
                                                                elapsed=end-start
                                                                self.ExtractTime(elapsed)
                                                                ProgressTxt.append("".join(['Parametric Anova Elapsed Time (GFP) : ',self.TimeTxt]))
                                                                GFPTime=self.Wave.file.createArray('/Result/Anova/GFP','ElapsedTime',self.TimeTxt)
                                                        elif self.Type=="All Electrodes":
                                                                start=time.clock()
                                                                self.Wave.Param()
                                                                end=time.clock()
                                                                elapsed=end-start
                                                                self.ExtractTime(elapsed)
                                                                ProgressTxt.append("".join(['Parametric Anova Elapsed Time (All Electrodes) : ',self.TimeTxt]))
                                                                AllTime=self.Wave.file.createArray('/Result/Anova/All','ElapsedTime',self.TimeTxt)
                                                        
                                                       
                                                        
                                                
                                                else: # Non param
                                                        if self.Type=="Both":
                                                                start=time.clock()
                                                                self.Wave.NonParam(self.AnovaIteration)
                                                                end=time.clock()
                                                                elapsed=end-start
                                                                self.ExtractTime(elapsed)
                                                                ProgressTxt.append("".join(['Non-Parametric Anova Elapsed Time (All Electrodes) : ',self.TimeTxt]))
                                                                AllTime=self.Wave.file.createArray('/Result/Anova/All','ElapsedTime',self.TimeTxt)

                                                                start=time.clock()
                                                                self.Wave.NonParam(self.AnovaIteration,DataGFP=True)
                                                                end=time.clock()
                                                                elapsed=end-start
                                                                self.ExtractTime(elapsed)
                                                                ProgressTxt.append("".join(['Parametric Anova Elapsed Time (GFP) : ',self.TimeTxt]))
                                                                AllTime=self.Wave.file.createArray('/Result/Anova/GFP','ElapsedTime',self.TimeTxt)
                                                                
                                                                
                                                        elif self.Type=="GFP Only":
                                                                start=time.clock()
                                                                self.Wave.NonParam(self.AnovaIteration,DataGFP=True)
                                                                end=time.clock()
                                                                elapsed=end-start
                                                                self.ExtractTime(elapsed)
                                                                ProgressTxt.append("".join(['Non-Parametric Anova Elapsed Time (GFP) : ',self.TimeTxt]))
                                                                AllTime=self.Wave.file.createArray('/Result/Anova/GFP','ElapsedTime',self.TimeTxt)
                                                        elif self.Type=="All Electrodes":
                                                                start=time.clock()
                                                                self.Wave.NonParam(self.AnovaIteration)
                                                                end=time.clock()
                                                                elapsed=end-start
                                                                self.ExtractTime(elapsed)
                                                                ProgressTxt.append("".join(['Non-Parametric Anova Elapsed Time (All Electrodes) : ',self.TimeTxt]))
                                                                AllTime=self.Wave.file.createArray('/Result/Anova/All','ElapsedTime',self.TimeTxt)
                                                                
                                                self.Wave.file.close()
                                                self.Cancel= self.Wave.Cancel

                                        ##############################################################
                                        # Post Stat (PostHoc) i.e Mathematical Morphology, write Data
                                        ##############################################################
                                        
                                        if self.Cancel==False:
                                                ResultName='Anova'
                                                PathResultAnova=os.path.abspath("/".join([PathResult,ResultName]))
                                                try:
                                                        os.mkdir(PathResultAnova)
                                                except:
                                                        pass
                                                if self.Type=="Both":
                                                        start=time.clock()
                                                        self.WavePostStat=PostStat.Data(self.H5,self,Anova=True,DataGFP=False, Param=self.AnovaParam)
                                                        self.WavePostStat.MathematicalMorphology(self.AnovaAlpha,TF=self.AnovaPtsConsec,SpaceCriteria=self.AnovaClust,SpaceFile=self.SpaceFile)
                                                        end=time.clock()
                                                        elapsed=end-start
                                                        self.ExtractTime(elapsed)
                                                        ProgressTxt.append("".join(['Multiple Test Correction Elapsed Time (All electrodes): ',self.TimeTxt]))

                                                        start=time.clock()
                                                        self.WavePostStat.WriteData(PathResultAnova)
                                                        end=time.clock()
                                                        elapsed=end-start
                                                        self.ExtractTime(elapsed)
                                                        ProgressTxt.append("".join(['Writing EPH Results Elapsed Time : ',self.TimeTxt]))

                                                        start=time.clock()
                                                        self.WavePostStat.WriteIntermediateResult(PathResult)
                                                        end=time.clock()
                                                        elapsed=end-start
                                                        self.ExtractTime(elapsed)
                                                        ProgressTxt.append("".join(['Writing intermediater EPH Results Elapsed Time : ',self.TimeTxt]))

                                                        self.WavePostStat.file.close()
                                                        start=time.clock()
                                                        self.WavePostStat=PostStat.Data(self.H5,self,Anova=True,DataGFP=True, Param=self.AnovaParam)
                                                        self.WavePostStat.MathematicalMorphology(self.AnovaAlpha,TF=self.AnovaPtsConsec,SpaceCriteria=1,SpaceFile=None)
                                                        end=time.clock()
                                                        elapsed=end-start
                                                        self.ExtractTime(elapsed)
                                                        ProgressTxt.append("".join(['Multiple Test Correction Elapsed Time (GFP): ',self.TimeTxt]))

                                                        start=time.clock()
                                                        self.WavePostStat.WriteData(PathResultAnova)
                                                        end=time.clock()
                                                        elapsed=end-start
                                                        self.ExtractTime(elapsed)
                                                        ProgressTxt.append("".join(['Writing EPH Results Elapsed Time : ',self.TimeTxt]))
                                                        
                                                        start=time.clock()
                                                        self.WavePostStat.WriteIntermediateResult(PathResult,DataGFP=True)
                                                        end=time.clock()
                                                        elapsed=end-start
                                                        self.ExtractTime(elapsed)
                                                        ProgressTxt.append("".join(['Writing intermediater EPH Results Elapsed Time : ',self.TimeTxt]))
                                                        self.WavePostStat.file.close()
                                                       
                                                elif self.Type=="GFP Only":
                                                        start=time.clock()
                                                        self.WavePostStat=PostStat.Data(self.H5,self,Anova=True,DataGFP=True, Param=self.AnovaParam)
                                                        self.WavePostStat.MathematicalMorphology(self.AnovaAlpha,TF=self.AnovaPtsConsec,SpaceCriteria=1,SpaceFile=None)
                                                        end=time.clock()
                                                        elapsed=end-start
                                                        self.ExtractTime(elapsed)
                                                        ProgressTxt.append("".join(['Multiple Test Correction Elapsed Time (GFP): ',self.TimeTxt]))

                                                        start=time.clock()
                                                        self.WavePostStat.WriteData(PathResultAnova)
                                                        end=time.clock()
                                                        elapsed=end-start
                                                        self.ExtractTime(elapsed)
                                                        ProgressTxt.append("".join(['Writing EPH Results Elapsed Time : ',self.TimeTxt]))

                                                        start=time.clock()
                                                        self.WavePostStat.WriteIntermediateResult(PathResult,DataGFP=True)
                                                        end=time.clock()
                                                        elapsed=end-start
                                                        self.ExtractTime(elapsed)
                                                        ProgressTxt.append("".join(['Writing intermediater EPH Results Elapsed Time : ',self.TimeTxt]))
                                                        self.WavePostStat.file.close()
                                                elif self.Type=="All Electrodes":
                                                        start=time.clock()
                                                        self.WavePostStat=PostStat.Data(self.H5,self,Anova=True,DataGFP=False, Param=self.AnovaParam)
                                                        self.WavePostStat.MathematicalMorphology(self.AnovaAlpha,TF=self.AnovaPtsConsec,SpaceCriteria=self.AnovaClust,SpaceFile=self.SpaceFile)
                                                        end=time.clock()
                                                        elapsed=end-start
                                                        self.ExtractTime(elapsed)
                                                        ProgressTxt.append("".join(['Multiple Test Correction Elapsed Time (All electrodes): ',self.TimeTxt]))

                                                        start=time.clock()
                                                        self.WavePostStat.WriteData(PathResultAnova)
                                                        end=time.clock()
                                                        elapsed=end-start
                                                        self.ExtractTime(elapsed)
                                                        ProgressTxt.append("".join(['Writing EPH Results Elapsed Time : ',self.TimeTxt]))

                                                        start=time.clock()
                                                        self.WavePostStat.WriteIntermediateResult(PathResult)
                                                        end=time.clock()
                                                        elapsed=end-start
                                                        self.ExtractTime(elapsed)
                                                        ProgressTxt.append("".join(['Writing intermediater EPH Results Elapsed Time : ',self.TimeTxt]))
                                                        self.WavePostStat.file.close()
                                                
                                        
                                        
                                ####################################       
                                # calcul PostHoc on wave and/or GFP
                                ####################################
                                if self.PostHoc :
                                        if CalculPostHoc:
                                                self.WavePostHoc=Stat.PostHoc(self.H5,self)
                                                if self.PostHocParam:# parametric
                                                        if self.Type=="Both":
                                                                start=time.clock()
                                                                self.WavePostHoc.Param()
                                                                end=time.clock()
                                                                elapsed=end-start
                                                                self.ExtractTime(elapsed)
                                                                ProgressTxt.append("".join(['Parametric PostHoc Elapsed Time (All Electrodes) : ',self.TimeTxt]))
                                                                AllTime=self.WavePostHoc.file.createArray('/Result/PostHoc/All','ElapsedTime',self.TimeTxt)
                                                                
                                                                start=time.clock()
                                                                self.WavePostHoc.Param(DataGFP=True)
                                                                end=time.clock()
                                                                elapsed=end-start
                                                                self.ExtractTime(elapsed)
                                                                ProgressTxt.append("".join(['Parametric PostHoc Elapsed Time (GFP) : ',self.TimeTxt]))
                                                                GFPTime=self.WavePostHoc.file.createArray('/Result/PostHoc/GFP','ElapsedTime',self.TimeTxt)
                                                                
                                                        elif self.Type=="GFP Only":
                                                                
                                                                start=time.clock()
                                                                self.WavePostHoc.Param(DataGFP=True)
                                                                end=time.clock()
                                                                elapsed=end-start
                                                                self.ExtractTime(elapsed)
                                                                ProgressTxt.append("".join(['Parametric PostHoc Elapsed Time (GFP) : ',self.TimeTxt]))
                                                                GFPTime=self.WavePostHoc.file.createArray('/Result/PostHoc/GFP','ElapsedTime',self.TimeTxt)

                                                        elif self.Type=="All Electrodes":
                                                                
                                                                start=time.clock()
                                                                self.WavePostHoc.Param()
                                                                end=time.clock()
                                                                elapsed=end-start
                                                                self.ExtractTime(elapsed)
                                                                ProgressTxt.append("".join(['Parametric PostHoc Elapsed Time (All Electrodes) : ',self.TimeTxt]))
                                                                AllTime=self.WavePostHoc.file.createArray('/Result/PostHoc/All','ElapsedTime',self.TimeTxt)
                                                
                                                else:# Non param
                                                        if self.Type=="Both":
                                                                start=time.clock()
                                                                self.WavePostHoc.NonParam(self.PostHocIteration)
                                                                end=time.clock()
                                                                elapsed=end-start
                                                                self.ExtractTime(elapsed)
                                                                ProgressTxt.append("".join(['Parametric PostHoc Elapsed Time (All Electrodes) : ',self.TimeTxt]))
                                                                AllTime=self.WavePostHoc.file.createArray('/Result/PostHoc/All','ElapsedTime',self.TimeTxt)
                                                                
                                                                start=time.clock()
                                                                self.WavePostHoc.NonParam(self.PostHocIteration,DataGFP=True)
                                                                end=time.clock()
                                                                elapsed=end-start
                                                                self.ExtractTime(elapsed)
                                                                ProgressTxt.append("".join(['Parametric Anova Elapsed Time (GFP) : ',self.TimeTxt]))
                                                                GFPTime=self.WavePostHoc.file.createArray('/Result/PostHoc/GFP','ElapsedTime',self.TimeTxt)
                                                                
                                                                

                                                        elif self.Type=="GFP Only":
                                                                start=time.clock()
                                                                self.WavePostHoc.NonParam(self.PostHocIteration,DataGFP=True)
                                                                end=time.clock()
                                                                elapsed=end-start
                                                                self.ExtractTime(elapsed)
                                                                ProgressTxt.append("".join(['Parametric Anova Elapsed Time (GFP) : ',self.TimeTxt]))
                                                                GFPTime=self.WavePostHoc.file.createArray('/Result/PostHoc/GFP','ElapsedTime',self.TimeTxt)

                                                        elif self.Type=="All Electrodes":
                                                                start=time.clock()
                                                                self.WavePostHoc.NonParam(self.PostHocIteration)
                                                                end=time.clock()
                                                                elapsed=end-start
                                                                self.ExtractTime(elapsed)
                                                                ProgressTxt.append("".join(['Parametric PostHoc Elapsed Time (All Electrodes) : ',self.TimeTxt]))
                                                                AllTime=self.WavePostHoc.file.createArray('/Result/PostHoc/All','ElapsedTime',self.TimeTxt)
                                                self.WavePostHoc.file.close()
                                                self.Cancel= self.WavePostHoc.Cancel
                                        
                                        #############################################################
                                        # Post Stat (PostHoc) i.e Mathematical Morphology, write Data
                                        #############################################################
  
                                        if self.Cancel==False:
                                                ResultName='PostHoc'
                                                PathResultPostHoc=os.path.abspath("/".join([PathResult,ResultName]))
                                                try:
                                                        os.mkdir(PathResultPostHoc)
                                                except:
                                                        pass
                                                if self.Type=="Both":

                                                        start=time.clock()                
                                                        self.WavePostStat=PostStat.Data(self.H5,self,Anova=False,DataGFP=False, Param=self.PostHocParam)
                                                        self.WavePostStat.MathematicalMorphology(self.PostHocAlpha,TF=self.PostHocPtsConsec,SpaceCriteria=self.PostHocClust,SpaceFile=self.SpaceFile)
                                                        end=time.clock()
                                                        elapsed=end-start
                                                        self.ExtractTime(elapsed)
                                                        ProgressTxt.append("".join(['Multiple Test Correction Elapsed Time on PostHoc (All electrodes): ',self.TimeTxt]))

                                                        start=time.clock()
                                                        self.WavePostStat.WriteData(PathResultPostHoc)
                                                        end=time.clock()
                                                        elapsed=end-start
                                                        self.ExtractTime(elapsed)
                                                        ProgressTxt.append("".join(['Writing EPH Results Elapsed Time on PostHoc(All electrodes) : ',self.TimeTxt]))
                                                        self.WavePostStat.file.close()

                                                        start=time.clock()
                                                        self.WavePostStat=PostStat.Data(self.H5,self,Anova=False,DataGFP=True, Param=self.PostHocParam)
                                                        self.WavePostStat.MathematicalMorphology(self.PostHocAlpha,TF=self.PostHocPtsConsec,SpaceCriteria=self.PostHocClust,SpaceFile=self.SpaceFile)
                                                        end=time.clock()
                                                        elapsed=end-start
                                                        self.ExtractTime(elapsed)
                                                        ProgressTxt.append("".join(['Multiple Test Correction Elapsed Time on PostHoc (GFP): ',self.TimeTxt]))

                                                        start=time.clock()
                                                        self.WavePostStat.WriteData(PathResultPostHoc)
                                                        end=time.clock()
                                                        elapsed=end-start
                                                        self.ExtractTime(elapsed)
                                                        ProgressTxt.append("".join(['Writing EPH Results Elapsed Time on PostHoc(GFP) : ',self.TimeTxt]))
                                                        self.WavePostStat.file.close()
                                                        
                                                elif self.Type=="GFP Only":
                                                        
                                                        start=time.clock()
                                                        self.WavePostStat=PostStat.Data(self.H5,self,Anova=False,DataGFP=True, Param=self.PostHocParam)
                                                        self.WavePostStat.MathematicalMorphology(self.PostHocAlpha,TF=self.PostHocPtsConsec,SpaceCriteria=self.PostHocClust,SpaceFile=self.SpaceFile)
                                                        end=time.clock()
                                                        elapsed=end-start
                                                        self.ExtractTime(elapsed)
                                                        ProgressTxt.append("".join(['Multiple Test Correction Elapsed Time on PostHoc (GFP): ',self.TimeTxt]))

                                                        start=time.clock()
                                                        self.WavePostStat.WriteData(PathResultPostHoc)
                                                        end=time.clock()
                                                        elapsed=end-start
                                                        self.ExtractTime(elapsed)
                                                        ProgressTxt.append("".join(['Writing EPH Results Elapsed Time on PostHoc(GFP) : ',self.TimeTxt]))
                                                        self.WavePostStat.file.close()
                                                        
                                                elif self.Type=="All Electrodes":
                                                        
                                                        start=time.clock()
                                                        self.WavePostStat=PostStat.Data(self.H5,self,Anova=False,DataGFP=False, Param=self.PostHocParam)
                                                        self.WavePostStat.MathematicalMorphology(self.PostHocAlpha,TF=self.PostHocPtsConsec,SpaceCriteria=self.PostHocClust,SpaceFile=self.SpaceFile)
                                                        end=time.clock()
                                                        elapsed=end-start
                                                        self.ExtractTime(elapsed)
                                                        ProgressTxt.append("".join(['Multiple Test Correction Elapsed Time on PostHoc (All electrodes): ',self.TimeTxt]))

                                                        start=time.clock()
                                                        self.WavePostStat.WriteData(PathResultPostHoc)
                                                        end=time.clock()
                                                        elapsed=end-start
                                                        self.ExtractTime(elapsed)
                                                        ProgressTxt.append("".join(['Writing EPH Results Elapsed Time on PostHoc : ',self.TimeTxt]))
                                                        self.WavePostStat.file.close()

                        #####################################################################################       
                        # calcul Anova on Inverse space
                        #####################################################################################   
                        elif self.AnalyseType=='ANOVA  on Brain Space':
                                
                                if self.AnovaCheck:
                                        if CalculAnova:
                                                self.IS=Stat.Anova(self.H5,self)
                                                if self.AnovaParam:# parametric
                                                        start=time.clock()
                                                        self.IS.Param()
                                                        end=time.clock()
                                                        elapsed=end-start
                                                        self.ExtractTime(elapsed)
                                                        ProgressTxt.append("".join(['Parametric Anova Elapsed Time : ',self.TimeTxt]))
                                                        AllTime=self.IS.file.createArray('/Result/Anova/All','ElapsedTime',self.TimeTxt)
                                                
                                                else:# non param
                                                        start=time.clock()
                                                        self.IS.NonParam(self.AnovaIteration)
                                                        end=time.clock()
                                                        elapsed=end-start
                                                        self.ExtractTime(elapsed)
                                                        ProgressTxt.append("".join(['Non-Parametric Anova Elapsed Time  : ',self.TimeTxt]))
                                                        AllTime=self.IS.file.createArray('/Result/Anova/All','ElapsedTime',self.TimeTxt)
                                                        
                                                self.Cancel=self.IS.Cancel
                                                self.IS.file.close()
                                        #############################################################
                                        # Post Stat (ANOVA) i.e Mathematical Morphology, write Data
                                        #############################################################
                                        if self.Cancel==False:
                                                ResultName='Anova'
                                                PathResultAnova=os.path.abspath("/".join([PathResult,ResultName]))
                                                os.mkdir(PathResultAnova)
                                                start=time.clock()
                                                self.ISPostStat=PostStat.Data(self.H5,self,Anova=True,DataGFP=False, Param=self.AnovaParam)
                                                self.ISPostStat.MathematicalMorphology(self.AnovaAlpha,TF=self.AnovaPtsConsec,SpaceCriteria=self.AnovaClust,SpaceFile=self.SpaceFile)
                                                end=time.clock()
                                                elapsed=end-start
                                                self.ExtractTime(elapsed)
                                                ProgressTxt.append("".join(['Multiple Test Correction Elapsed Time : ',self.TimeTxt]))

                                                start=time.clock()
                                                self.ISPostStat.WriteData(PathResultAnova)
                                                end=time.clock()
                                                elapsed=end-start
                                                self.ExtractTime(elapsed)
                                                ProgressTxt.append("".join(['Writing EPH Results Elapsed Time : ',self.TimeTxt]))
                                                
                                                start=time.clock()
                                                self.ISPostStat.WriteIntermediateResult(PathResult)
                                                end=time.clock()
                                                elapsed=end-start
                                                self.ExtractTime(elapsed)
                                                ProgressTxt.append("".join(['Writing intermediater EPH Results Elapsed Time : ',self.TimeTxt]))
                                                
                                                self.ISPostStat.file.close()
                                ##########################      
                                # PostHoc on inverse space
                                ##########################
                          
                                if self.PostHoc:
                                        if CalculPostHoc:
                                                self.ISPostHoc=Stat.PostHoc(self.H5,self)
                                                if self.PostHocParam:# parametric
                                                        start=time.clock()
                                                        self.ISPostHoc.Param()
                                                        end=time.clock()
                                                        elapsed=end-start
                                                        self.ExtractTime(elapsed)
                                                        ProgressTxt.append("".join(['Parametric PostHoc Elapsed Time  : ',self.TimeTxt]))
                                                        AllTime=self.ISPostHoc.file.createArray('/Result/PostHoc/All','ElapsedTime',self.TimeTxt)
                                                else:# Non param
                                                        start=time.clock()
                                                        self.ISPostHoc.NonParam(self.PostHocIteration)
                                                        end=time.clock()
                                                        elapsed=end-start
                                                        self.ExtractTime(elapsed)
                                                        ProgressTxt.append("".join(['Parametric PostHoc Elapsed Time (All Electrodes) : ',self.TimeTxt]))
                                                        AllTime=self.ISPostHoc.file.createArray('/Result/PostHoc/All','ElapsedTime',self.TimeTxt)
                                                self.Cancel=self.ISPostHoc.Cancel
                                                self.ISPostStat.file.close()
                                                
                                        if self.Cancel==False:
                                                ResultName='PostHoc'
                                                PathResultPostHoc=os.path.abspath("/".join([PathResult,ResultName]))
                                                try:
                                                        os.mkdir(PathResultPostHoc)
                                                except:
                                                        pass
                                                
                                                start=time.clock()              
                                                self.ISPostStat=PostStat.Data(self.H5,self,Anova=False,DataGFP=False, Param=self.PostHocParam)
                                                self.ISPostStat.MathematicalMorphology(self.PostHocAlpha,TF=self.PostHocPtsConsec,SpaceCriteria=self.PostHocClust,SpaceFile=self.SpaceFile)
                                                end=time.clock()
                                                elapsed=end-start
                                                self.ExtractTime(elapsed)
                                                ProgressTxt.append("".join(['Multiple Test Correction Elapsed Time on PostHoc : ',self.TimeTxt]))

                                                start=time.clock()
                                                self.ISPostStat.WriteData(PathResultPostHoc)
                                                end=time.clock()
                                                elapsed=end-start
                                                self.ExtractTime(elapsed)
                                                ProgressTxt.append("".join(['Writing EPH Results Elapsed Time on PostHoc : ',self.TimeTxt]))
                                                self.ISPostStat.file.close()

                        
                        ##################      
                        # If cancel press
                        #################
                        if self.Cancel:
                                file=tables.openFile(self.H5,'r+')
                                GFPDataTest=file.listNodes('/Result/Anova/GFP')
                                AllDataTest=file.listNodes('/Result/Anova/All')
                                if GFPDataTest!=[]:
                                        file.removeNode('/Result/Anova/GFP',recursive=True)
                                        file.createGroup('/Result/Anova','GFP')
                                if AllDataTest!=[]:
                                        file.removeNode('/Result/Anova/All',recursive=True)
                                        file.createGroup('/Result/Anova','All')
                                file.close()
                                self.LeftPanel.ProgressTxt.SetLabel("Calculation Cancel by user")
                        else:
                                self.LeftPanel.ProgressTxt.SetLabel("\n".join(ProgressTxt))
                                self.WriteVrb(self.H5,PathResult)
                                dlg=wx.MessageDialog(self,'Work is done enjoy your results !!!! ;-)',style=wx.ICON_INFORMATION)
                                retour = dlg.ShowModal()
                                dlg.Destroy()
                        self.StartButton.Enable()
        # test les input
        def InputTest(self):
                """ Read user inputs put everythink on the common format and verify that everything is present"""
                # test all variable type
                # we strat with mandatory variable (leftPanel)
                text=[]   
                if  self.LeftPanel.PathResult == None:
                        error="Result folder is not selected"
                        text.append(error)
                else :
                        self.PathResult=self.LeftPanel.PathResult
                # test si le filchier data est present
                if self.H5==[]:
                        error="Model not define or H5 not present"
                        text.append(error)
                # on recuper le Panel de droite
                page=self.Tab.GetSelection()  
                self.AnalyseType=self.Tab.GetPageText(page)         
                # Anova wave GFP
                if self.AnalyseType=='ANOVA on Wave/GFP':
                        # self.AnovaParam =Anova  parmetric oui non / bool
                        # self.PostHoc = posthoc oui/non / bool
                        # self.Type = type of analysis wave, gfp, both / String
                        # self.AnovaAlpha= Anova Alpha value / Float
                        # self.AnovaPtsConsec = Pts consecutive criteria / int
                        # self.AnovaCheck = ANova perfromed oui / non /  bool
                        # self.PostHocParam= PostHoc Param oui/non bool
                        # self.AnovaClust = cluster sur xyz/ int
                        # self.spi = xyz file / string
                        
                        self.AnovaCheck=self.AnovaWave.AnovaPerformed
                        # si on a cocher anova
                        if self.AnovaCheck:
                                self.AnovaParam=self.AnovaWave.Param
                                
                                if  self.AnovaWave.Alpha < 0 and self.AnovaWave.Alpha > 1:
                                        error="Alpha for Anova must be between 0 and 1"
                                        text.append(error)
                                else :
                                        self.AnovaAlpha=self.AnovaWave.Alpha

                                if  self.AnovaWave.PtsConseq < 1:
                                        error="Consecutive Time frame, for Anova must be strictly positive" 
                                        text.append(error)
                                else :
                                        self.AnovaPtsConsec=self.AnovaWave.PtsConseq
                                        
                                if self.AnovaWave.Clust < 1:          
                                        error="Cluster size for Anova  must be strictly positive" 
                                        text.append(error)
                                else:
                                        self.AnovaClust=self.AnovaWave.Clust

                                if self.AnovaParam==False:
                                        if self.AnovaWave.Iter < 1:          
                                                error="Iteraction Value for Anova  must be strictly positive" 
                                                text.append(error)
                                        else:
                                                self.AnovaIteration=Iteration=self.AnovaWave.Iter      
                                
                                 
                                        
                        self.PostHoc=self.AnovaWave.PostHoc
                        self.PostHocClust=1
                        # si on a cocher PostHoc
                        if self.PostHoc:
                                self.PostHocParam= self.AnovaWave.PostHocParam
                                if  self.AnovaWave.AlphaInputPostHoc < 0 and self.AnovaWave.AlphaInputPostHoc > 1:
                                        error="Alpha for Post-Hoc must be between 0 and 1"
                                        text.append(error)
                                else :
                                        self.PostHocAlpha=self.AnovaWave.AlphaPostHoc
                                        
                                if  self.AnovaWave.PtsConseqPostHoc < 1:
                                        error="Consecutive Time frame for Post-Hoc must be strictly positive" 
                                        text.append(error)
                                else :
                                        self.PostHocPtsConsec=self.AnovaWave.PtsConseqPostHoc
                                        

                                if self.AnovaWave.ClustPostHoc < 1:          
                                        error="Cluster size for Post-Hoc must be strictly positive" 
                                        text.append(error)
                                else:
                                        self.PostHocClust=self.AnovaWave.ClustPostHoc
                                        
                                if self.PostHocParam==False:
                                        if self.AnovaIS.Iter < 1:          
                                                error="Iteraction Value for Post-Hoc must be strictly positive" 
                                                text.append(error)
                                        else:
                                                self.PostHocIteration=self.AnovaWave.IterPostHoc
                
                        if  self.AnovaWave.Analyse == None:
                                error="Choose an Analyse (GFP, all electrodes or both)"
                                text.append(error)
                                self.Type=None
                        else :
                                self.Type=self.AnovaWave.Analyse
                        
                        if self.Type=="GFP Only" or self.Type==None:
                                self.SpaceFile=None   
                        else:
                                if self.AnovaCheck and self.PostHoc:
                                        if self.AnovaClust >1 or self.PostHocClust > 1:
                                                if  self.AnovaWave.Spi == None:
                                                        error="Xyz file is not selected"
                                                        text.append(error)
                                                else :
                                                        self.SpaceFile=self.AnovaWave.Spi
                                        else:
                                                self.SpaceFile=None
                                elif self.AnovaCheck:
                                        if self.AnovaClust >1:
                                                if  self.AnovaWave.Spi == None:
                                                        error="Xyz file is not selected"
                                                        text.append(error)
                                                else :
                                                        self.SpaceFile=self.AnovaWave.Spi
                                        else:
                                                self.SpaceFile=None
                                elif self.PostHoc:
                                        if self.PostHocClust > 1:
                                                if  self.AnovaWave.Spi == None:
                                                        error="Xyz file is not selected"
                                                        text.append(error)
                                                else :
                                                        self.SpaceFile=self.AnovaWave.Spi
                                        else:
                                                self.SpaceFile=None
                                                
                                        

                elif self.AnalyseType=='ANOVA  on Brain Space':
                        # self.AnovaParam =parmetric ou non / bool
                        # self.PostHoc = posthoc ou/non / bool
                        # self.Spi = Spi File for IS location / Path
                        # self.Alpha= Alpha value / Float
                        # self.PtsConsec = Pts consecutive criteria / int
                        # self.Clust = Pts for Cluster / int
                        # self.AnovaCheck = ANova perfromed oui / non /  bool
                        # self.PostHocParam= PostHoc Param oui/non bool
                        self.Type=None
                        self.AnovaCheck=self.AnovaIS.AnovaPerformed
                        if self.AnovaCheck:
                                self.AnovaParam= self.AnovaIS.Param
                                if  self.AnovaIS.Alpha < 0 and self.AnovaIS.Alpha > 1:
                                        error="Alpha must be between 0 and 1"
                                        text.append(error)
                                else :
                                        self.AnovaAlpha=self.AnovaIS.Alpha

                                if  self.AnovaIS.PtsConseq < 1:
                                        error="Consecutive Time frame for Anova must be strictly positive" 
                                        text.append(error)
                                else :
                                        self.AnovaPtsConsec=self.AnovaIS.PtsConseq

                                if self.AnovaIS.Clust < 1:          
                                        error="Cluster size for Anova must be strictly positive" 
                                        text.append(error)
                                else:
                                        self.AnovaClust=self.AnovaIS.Clust
                                        
                                if self.AnovaParam==False:
                                        if self.AnovaIS.Iter < 1:          
                                                error="Iteraction Value for Anova must be strictly positive" 
                                                text.append(error)
                                        else:
                                                self.AnovaIteration=self.AnovaIS.Iter
                                                
                        self.PostHoc=self.AnovaIS.PostHoc
                        self.PostHocClust=1
                        if self.PostHoc:
                                self.PostHocParam= self.AnovaIS.PostHocParam
                                if  self.AnovaIS.AlphaPostHoc < 0 and self.AnovaIS.AlphaPostHoc > 1:
                                        error="Alpha for Post-Hoc must be between 0 and 1"
                                        text.append(error)
                                else :
                                        self.PostHocAlpha=self.AnovaIS.AlphaPostHoc

                                if  self.AnovaIS.PtsConseqPostHoc < 1:
                                        error="Consecutive Time frame for Post-Hoc must be strictly positive" 
                                        text.append(error)
                                else :
                                        self.PostHocPtsConsec=self.AnovaIS.PtsConseqPostHoc
                                        

                                if self.AnovaIS.ClustPostHoc < 1:          
                                        error="Cluster size for Post-Hoc must be strictly positive" 
                                        text.append(error)
                                else:
                                        self.PostHocClust=self.AnovaIS.ClustPostHoc

                                if self.PostHocParam==False:
                                        if self.AnovaIS.Iter < 1:          
                                                error="Iteraction Value for Post-Hoc must be strictly positive" 
                                                text.append(error)
                                        else:
                                                self.PostHocIteration=self.AnovaIS.IterPostHoc
                        
                        if  self.AnovaIS.Spi == None:
                                if self.PostHocClust >1 or self.AnovaClust >1:
                                        error="Spi file is not selected"
                                        text.append(error)
                                else:
                                        self.SpaceFile=None
                                        
                        else :
                                self.SpaceFile=self.AnovaIS.Spi

                                
                #Manova wave
                elif self.AnalyseType=='MANOVA on Wave/GFP':
                        # self.Param =parmetric ou non / bool
                        # self.PostHoc = posthoc ou/non / bool
                        # self.Type = type of analysis wave, gfp, both / String
                        # self.Alpha= Alpha value / Float

                        if self.ManovaWave.Param ==0:
                                self.Param= True
                        else:
                                self.Param=False
                        self.PostHoc=self.ManovaWave.PostHoc
                        if  self.ManovaWave.Analyse == None:
                                error="Choose an Analyse (GFP, all electrodes or both)"
                                text.append(error)
                        else :
                                self.Type=self.ManovaWave.Analyse

                        if  self.ManovaWave.Alpha < 0 and self.ManovaWave.Alpha > 1:
                                error="Alpha must be between 0 and 1"
                                text.append(error)
                        else :
                                self.Alpha=self.ManovaWave.Alpha

                                
                #Manova IS
                elif self.AnalyseType=='MANOVA  on Brain Space':
                        # self.Param =parmetric ou non / bool
                        # self.PostHoc = posthoc ou/non / bool
                        # self.Alpha= Alpha value / Float
                        if self.ManovaIS.Param ==0:
                                self.Param= True
                        else:
                                self.Param=False 
                        self.PostHoc=self.ManovaIS.PostHoc
                        if  self.ManovaIS.Alpha < 0 and self.ManovaIS.Alpha > 1:
                                error="Alpha must be between 0 and 1"
                                text.append(error)
                        else :
                                self.Alpha=self.ManovaIS.Alpha
                self.InputError=text
        def ExtractTime(self,elapsed):
                heures=int(elapsed/3600)
                minutes=int(elapsed%3600/60)
                seconde=int(elapsed%3600%60)
                if heures <10:
                        heures="".join(['0',str(heures)])
                else:
                        heures=str(heures)
                if minutes <10:
                        minutes="".join(['0',str(minutes)])
                else:
                        minutes=str(minutes)
                if seconde <10:
                        seconde="".join(['0',str(seconde)])
                else:
                        seconde=str(seconde)
                self.TimeTxt=":".join([heures,minutes,seconde])
        def WriteVrb(self,H5,ResultFolder):
                ##### ecrire le VRB
                file=tables.openFile(H5,'r')
                Title=['Analysis : \n']
                Param=['Parameter :','\n','-----------','\n']
                if self.AnovaCheck:
                    # Anova
                    Param.append('ANOVA :\n')
                    Param.append('\tAlpha = ')
                    Param.append(str(self.AnovaAlpha))
                    Param.append('\n')
                    Param.append('\tConsecutive Time Frame Criteria = ')
                    Param.append(str(self.AnovaPtsConsec))
                    Param.append('\n')
                    
                    if self.AnovaParam:
                        if self.Type=="Both":
                                Title.append('All electrodes Waveform Parametric Repeated Measure ANOVA across')
                                shape=file.getNode('/Info/Shape')
                                Title.append(str(shape.read()[0]))
                                Title.append('Time Frame and')
                                Title.append(str(shape.read()[1]))
                                Title.append('Electrodes')
                                Title.append('\n')
                                Title.append('GFP Parametric Repeated Measure ANOVA across')
                                Title.append(str(shape.read()[0]))
                                Title.append('Time Frame and')
                                
                                Param.append('\tCluster Criteria (Electrodes) = ')
                                Param.append(str(self.AnovaClust))
                                Param.append('\n')
                                Param.append('\tCluster Criteria (File) = ')
                                Param.append(str(self.SpaceFile))
                                Param.append('\n')
                                
                        elif self.Type=="GFP Only":
                                Title.append('GFP Parametric Repeated Measure ANOVA across')
                                shape=file.getNode('/Info/ShapeGFP')
                                Title.append(str(shape.read()[0]))
                                Title.append('Time Frame and') 
                        elif self.Type=="All Electrodes":
                                Title.append('All electrodes Waveform Parametric Repeated Measure ANOVA across')
                                shape=file.getNode('/Info/Shape')
                                Title.append(str(shape.read()[0]))
                                Title.append('Time Frame and')
                                Title.append(str(shape.read()[1]))
                                Title.append('Electrodes')
                                Param.append('\tCluster Criteria (Electrodes) = ')
                                
                                Param.append(str(self.AnovaClust))
                                Param.append('\n')
                                Param.append('\tCluster Criteria (File) = ')
                                Param.append(str(self.SpaceFile))
                                Param.append('\n')
                        elif self.Type==None:
                                Title.append('All electrodes Waveform Parametric Repeated Measure ANOVA across')
                                shape=file.getNode('/Info/Shape')
                                Title.append(str(shape.read()[0]))
                                Title.append('Time Frame and')
                                Title.append(str(shape.read()[1]))
                                Title.append('Voxels')
                                
                                Param.append('\tCluster Criteria (Voxels) = ')
                                Param.append(str(self.AnovaClust))
                                Param.append('\n')
                                Param.append('\tCluster Criteria (File) = ')
                                Param.append(str(self.SpaceFile))
                                Param.append('\n')
                    else:
                        if self.Type=="Both":
                                Title.append('All electrodes Waveform Non-Parametric Repeated Measure ANOVA across')
                                shape=file.getNode('/Info/Shape')
                                Title.append(str(shape.read()[0]))
                                Title.append('Time Frame and')
                                Title.append(str(shape.read()[1]))
                                Title.append('Electrodes')
                                Title.append('\n')
                                Title.append('GFP Non-Parametric Repeated Measure ANOVA across')
                                Title.append(str(shape.read()[0]))
                                Title.append('Time Frame and')

                                Param.append('\tCluster Criteria (Electrodes) = ')
                                Param.append(str(self.AnovaClust))
                                Param.append('\n')
                                Param.append('\tCluster Criteria (File) = ')
                                Param.append(str(self.SpaceFile))
                                Param.append('\n')
                        elif self.Type=="GFP Only":
                                Title.append('GFP Non-Parametric Repeated Measure ANOVA across')
                                shape=file.getNode('/Info/ShapeGFP')
                                Title.append(str(shape.read()[0]))
                                Title.append('Time Frame and') 
                        elif self.Type=="All Electrodes":
                                Title.append('All electrodes Waveform Non-Parametric Repeated Measure ANOVA across')
                                shape=file.getNode('/Info/Shape')
                                Title.append(str(shape.read()[0]))
                                Title.append('Time Frame and')
                                Title.append(str(shape.read()[1]))
                                Title.append('Electrodes')

                                Param.append('\tCluster Criteria (Electrodes) = ')
                                Param.append(str(self.AnovaClust))
                                Param.append('\n')
                                Param.append('\tCluster Criteria (File) = ')
                                Param.append(str(self.SpaceFile))
                                Param.append('\n')
                        elif self.Type==None:
                                Title.append('All electrodes Waveform Non-Parametric Repeated Measure ANOVA across')
                                shape=file.getNode('/Info/Shape')
                                Title.append(str(shape.read()[0]))
                                Title.append('Time Frame and')
                                Title.append(str(shape.read()[1]))
                                Title.append('Voxels')

                                Param.append('\tCluster Criteria (Voxels) = ')
                                Param.append(str(self.AnovaClust))
                                Param.append('\n')
                                Param.append('\tCluster Criteria (File) = ')
                                Param.append(str(self.SpaceFile))
                                Param.append('\n')
                                
                        Param.append('\tIteraction Value = ')
                        Param.append(str(self.AnovaIteration))
                        Param.append('\n')

                if self.AnovaCheck and self.PostHoc:
                        Title.append('\n')
                if self.PostHoc:
                   Param.append('Post-Hoc :\n')
                   Param.append('\tAlpha = ')
                   Param.append(str(self.PostHocAlpha))
                   Param.append('\n')
                   Param.append('\tConsecutive Time Frame Criteria = ')
                   Param.append(str(self.PostHocPtsConsec))
                   Param.append('\n')
                   if self.PostHocParam:
                        if self.Type=="Both":
                                Title.append('All electrodes Waveform Parametric POST-HOC across')
                                shape=file.getNode('/Info/Shape')
                                Title.append(str(shape.read()[0]))
                                Title.append('Time Frames and')
                                Title.append(str(shape.read()[1]))
                                Title.append('Electrodes')
                                Title.append('\n')
                                Title.append('GFP Parametric POST-HOC across')
                                Title.append(str(shape.read()[0]))
                                Title.append('Time Frames')

                                Param.append('\tCluster Criteria (Electrodes) = ')
                                Param.append(str(self.PostHocClust))
                                Param.append('\n')
                                Param.append('\tCluster Criteria (File) = ')
                                Param.append(str(self.SpaceFile))
                                Param.append('\n')

                        elif self.Type=="GFP Only":
                                Title.append('GFP Parametric POST-HOC across')
                                shape=file.getNode('/Info/ShapeGFP')
                                Title.append(str(shape.read()[0]))
                                Title.append('Time Frames') 
                        elif self.Type=="All Electrodes":
                                Title.append('All electrodes Waveform Parametric POST-HOC across')
                                shape=file.getNode('/Info/Shape')
                                Title.append(str(shape.read()[0]))
                                Title.append('Time Frame and')
                                Title.append(str(shape.read()[1]))
                                Title.append('Electrodes')

                                Param.append('\tCluster Criteria (Electrodes) = ')
                                Param.append(str(self.PostHocClust))
                                Param.append('\n')
                                Param.append('\tCluster Criteria (File) = ')
                                Param.append(str(self.SpaceFile))
                                Param.append('\n')
                        elif self.Type==None:
                                Title.append('All electrodes Waveform Parametric POST-HOC across')
                                shape=file.getNode('/Info/Shape')
                                Title.append(str(shape.read()[0]))
                                Title.append('Time Frames and ')
                                Title.append(str(shape.read()[1]))
                                Title.append('Voxels')

                                Param.append('\tCluster Criteria (Voxels) = ')
                                Param.append(str(self.PostHocClust))
                                Param.append('\n')
                                Param.append('\tCluster Criteria (File) = ')
                                Param.append(str(self.SpaceFile))
                                Param.append('\n')
                        else:
                                if self.Type=="Both":
                                        Title.append('All electrodes Waveform Non-Parametric POST-HOC across')
                                        shape=file.getNode('/Info/Shape')
                                        Title.append(str(shape.read()[0]))
                                        Title.append('Time Frames and')
                                        Title.append(str(shape.read()[1]))
                                        Title.append('Electrodes')
                                        Title.append('\n')
                                        Title.append('GFP Non-Parametric POST-HOC across')
                                        Title.append(str(shape.read()[0]))
                                        Title.append('Time Frames ')

                                        Param.append('\tCluster Criteria (Electrodes) = ')
                                        Param.append(str(self.PostHocClust))
                                        Param.append('\n')
                                        Param.append('\tCluster Criteria (File) = ')
                                        Param.append(str(self.SpaceFile))
                                        Param.append('\n')
                                elif self.Type=="GFP Only":
                                        Title.append('GFP Non-Parametric POST-HOC across')
                                        shape=file.getNode('/Info/ShapeGFP')
                                        Title.append(str(shape.read()[0]))
                                        Title.append('Time Frames') 
                                elif self.Type=="All Electrodes":
                                        Title.append('All electrodes Waveform Non-Parametric POST-HOC across')
                                        shape=file.getNode('/Info/Shape')
                                        Title.append(str(shape.read()[0]))
                                        Title.append('Time Frames and')
                                        Title.append(str(shape.read()[1]))
                                        Title.append('Electrodes')

                                        Param.append('\tCluster Criteria (Electrodes) = ')
                                        Param.append(str(self.PostHocClust))
                                        Param.append('\n')
                                        Param.append('\tCluster Criteria (File) = ')
                                        Param.append(str(self.SpaceFile))
                                        Param.append('\n')
                                elif self.Type==None:
                                        Title.append('All electrodes Waveform Non-Parametric POST-HOC across')
                                        shape=file.getNode('/Info/Shape')
                                        Title.append(str(shape.read()[0]))
                                        Title.append('Time Frames and')
                                        Title.append(str(shape.read()[1]))
                                        Title.append('Voxels')

                                        Param.append('\tCluster Criteria (Voxels) = ')
                                        Param.append(str(self.PostHocClust))
                                        Param.append('\n')
                                        Param.append('\tCluster Criteria (File) = ')
                                        Param.append(str(self.SpaceFile))
                                        Param.append('\n')

                Factor=['Factor Names and Levels :\n','-------------------------\n']
                file.close()
                StatData=Stat.Anova(H5,self)
                Sheet=StatData.file.getNode('/Sheet/Value')
                InputFile=['Input File in relation to factors :\n','-----------------------------------\n']
                Value=StatData.file.getNode('/Sheet/Value').read()
                ColWithin=StatData.file.getNode('/Info/ColWithin').read()
                ColFactor=StatData.file.getNode('/Info/ColFactor').read()
                if StatData.NameWithin != False:
                        for i,w in enumerate(StatData.NameWithin):
                                Factor.append('Within Subject Factor Name (Levels) :')
                                InputFile.append('Within subject conditions :\n')
                                if i ==0:
                                        Factor.append(w)
                                        Factor.append('(')
                                        level=str(StatData.Within[:,i].max())
                                        level=level[0:level.find('.')]
                                        Factor.append(level)
                                        Factor.append(')')
                                else:
                                        Factor.append(',')
                                        Factor.append(w)
                                        Factor.append('(')
                                        level=str(StatData.Within[:,i].max())
                                        level=level[0:level.find('.')]
                                        Factor.append(level)
                                        Factor.append(')')
                        Factor.append('\n')
                        Condition=[]
                        for f in ColFactor:
                                tmp=[]
                                n=0
                                f=f[f.find('(')+1:f.find(')')]
                                for l in f:
                                        if l.isdigit():
                                                tmp.append('-')
                                                tmp.append(StatData.NameWithin[n])
                                                tmp.append(l)
                                                n+=1
                                tmp.remove('-')
                                Condition.append("".join(tmp))
                        for i,c in enumerate(Condition):
                                InputFile.append('\t')
                                InputFile.append(c)
                                InputFile.append(' Condition Files :\n')
                                Data=Value[ColWithin[i]]
                                for f in Data:
                                        InputFile.append('\t')
                                        InputFile.append(f)
                                        InputFile.append('\n')
                                InputFile.append('\n')
                
                if StatData.NameBetween != False:
                        Factor.append('Between Subject Factor Name (Levels) :')
                        for i,b in enumerate(StatData.NameBetween):
                                if i ==0:
                                        Factor.append(b)
                                        Factor.append('(')
                                        try:
                                                level=str(StatData.Between[:,i].max())
                                        except:
                                                level=str(StatData.Between.max())
                                        level=level[0:level.find('.')]
                                        Factor.append(level)
                                        Factor.append(')')
                                else:
                                        Factor.append(',')
                                        Factor.append(b)
                                        Factor.append('(')
                                        try:
                                                level=str(StatData.Between[:,i].max())
                                        except:
                                                level=str(StatData.Between.max())
                                        level=level[0:level.find('.')]
                                        Factor.append(level)
                                        Factor.append(')')
                        Factor.append('\n')
                        InputFile.append('Between subject conditions :\n')
                        ColBetween=StatData.file.getNode('/Info/ColBetween').read()
                        Condition=[]
                        for i,c in enumerate(ColBetween):
                                Data=Value[c]
                                for j,d in enumerate(Data):
                                        text=[StatData.NameBetween[i]]
                                        text.append(d)
                                        text.append(':')
                                        text=" ".join(text)
                                        if Condition==[]:
                                                Condition.append('\t')
                                                Condition.append(text)
                                                Condition.append('\n')
                                                Index=1
                                        else:
                                                if Condition[Index]!=text:
                                                        Condition.append('\n\t')
                                                        Condition.append(text)
                                                        Condition.append('\n')
                                                        Index=len(Condition)-2
                                                        
                                        for w in ColWithin:
                                                Condition.append('\t')
                                                Condition.append(Value[w][j])
                                                Condition.append('\n')
                        InputFile.append("".join(Condition))
                        InputFile.append('\n')
                if StatData.NameCovariate != False:
                        
                        Factor.append('Covariate Name :')
                        for i,c in enumerate(StatData.NameCovariate):
                                if i ==0:
                                        Factor.append(c)  
                                else:
                                        Factor.append(',')
                                        Factor.append(c)
                        Factor.append('\n')
                        InputFile.append('Covariate Value(s) :\n')
                        ColCovariate=StatData.file.getNode('/Info/ColCovariate').read()
                        Condition=[]
                        for i,c in enumerate(ColCovariate):
                                Condition.append('\t')
                                Condition.append(StatData.NameCovariate[i])
                                Condition.append('\n')
                                Data=Value[c]
                                for d in Data:
                                        Condition.append('\t')
                                        Condition.append(d)
                                        Condition.append('\n')
                        InputFile.append("".join(Condition))
                Title=" ".join(Title)
                Title=Title.split('\n')
                MaxLength=0
                for p in Title:
                        if len(p)>MaxLength:
                                MaxLength=len(p)
                Mark=[]
                for i in range(MaxLength):
                        Mark.append('=')
                Mark.insert(0,'\t\t')
                Mark.append('\n')
                Title="\n\t\t".join(Title)
                Param="".join(Param)
                if StatData.NameCovariate !=False:
                        Title.replace('ANOVA','ANCOVA')
                        Param.replace('ANOVA','ANCOVA')
                
                        
                os.chdir(ResultFolder)
                VrbFile = open('info.vrb', "w")
                VrbFile.write("".join(Mark))
                VrbFile.write('\t\t')
                VrbFile.write(Title)
                VrbFile.write('\n')
                VrbFile.write("".join(Mark))
                VrbFile.write('\n')
                VrbFile.write(Param)
                VrbFile.write('\n')
                VrbFile.write(" ".join(Factor))
                VrbFile.write('\n')
                VrbFile.write("".join(InputFile))
                VrbFile.write('\n')
                VrbFile.close()
                file.close()
                StatData.file.close()
class MonApp(wx.App):
        def OnInit(self):
                fen = principale()
                fen.Show(True)
                self.SetTopWindow(fen)
                return True

app = MonApp()
app.MainLoop()
