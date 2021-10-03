from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection 
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
import ROOT
import glob
from particleClass import particle
import argparse
import traceback
import multiprocessing as  np
import os

ROOT.PyConfig.IgnoreCommandLineOptions = True

class Channel(Module):
    def __init__(self,filename):
        self.writeHistFile=True
        self.filename = filename #filename passed cause we needed to count the events with zero divide errors	
        self.GenPart = particle("GenPart")
    
    def beginJob(self, histFile=None,histDirName=None):
        Module.beginJob(self,histFile,histDirName)
		#Now lets define the cutflow histograms
		#Starting to Di Tau channel selections
        self.cutflow_diTau =  ROOT.TH1F('cutflow_diTau', 'cutflow_diTau', 4, 0, 4)
        self.cutflow_diTau.GetXaxis().SetBinLabel(1,"Events_Preselected")
        self.cutflow_diTau.GetXaxis().SetBinLabel(2,"Two Higgs")
        self.cutflow_diTau.GetXaxis().SetBinLabel(3,"gJet condition")
        self.cutflow_diTau.GetXaxis().SetBinLabel(4,"diTau")
        self.cutflow_diTau.GetXaxis().SetTitle("Selections")
        self.cutflow_diTau.GetYaxis().SetTitle("Events")
        self.cutflow_diTau.SetFillColor(38)

        self.cutflow_et =  ROOT.TH1F('cutflow_et', 'cutflow_et', 4, 0, 4)
        self.cutflow_et.GetXaxis().SetBinLabel(1,"Events_Preselected")
        self.cutflow_et.GetXaxis().SetBinLabel(2,"Two Higgs")
        self.cutflow_et.GetXaxis().SetBinLabel(3,"2b2t")
        self.cutflow_et.GetXaxis().SetBinLabel(4,"et")
        self.cutflow_et.GetXaxis().SetTitle("Selections")
        self.cutflow_et.GetYaxis().SetTitle("Events")
        self.cutflow_et.SetFillColor(38)


        self.cutflow_mt =  ROOT.TH1F('cutflow_mt', 'cutflow_mt', 4, 0, 4)
        self.cutflow_mt.GetXaxis().SetBinLabel(1,"Events_Preselected")
        self.cutflow_mt.GetXaxis().SetBinLabel(2,"Twi Higgs")
        self.cutflow_mt.GetXaxis().SetBinLabel(3,"2b2t")
        self.cutflow_mt.GetXaxis().SetBinLabel(4,"mt")
        self.cutflow_mt.GetXaxis().SetTitle("Selections")
        self.cutflow_mt.GetYaxis().SetTitle("Events")
        self.cutflow_mt.SetFillColor(38)
        self.addObject(self.cutflow_diTau) #adding these objects is important cause we can accesses these afterwards!
        self.addObject(self.cutflow_mt)
        self.addObject(self.cutflow_et)


    def analyze(self, event): 
        self.cutflow_diTau.AddBinContent(1)
        self.cutflow_et.AddBinContent(1)
        self.cutflow_mt.AddBinContent(1)

        hCount = 0
        tCount = 0
        bCount = 0
        eCount = 0
        muCount = 0


        self.GenPart.setupCollection(event)

        for obj in self.GenPart.collection:
            if obj.pdgId == 25:
                hCount += 1
        
        if hCount == 2:
            self.cutflow_diTau.AddBinContent(2)
            self.cutflow_et.AddBinContent(2)
            self.cutflow_mt.AddBinContent(2)
            for i in range(len(self.GenPart.collection)):
                if abs(self.GenPart.collection[i].pdgId) == 15 and self.GenPart.collection[i].statusFlags & 2 ==2 and self.GenPart.collection[self.GenPart.collection[i].genPartIdxMother].pdgId == 25:
                    tCount += 1

                if abs(self.GenPart.collection[i].pdgId) == 5 and self.GenPart.collection[self.GenPart.collection[i].genPartIdxMother].pdgId == 25:
                    bCount += 1

        if tCount == 2 and bCount == 2:
            self.cutflow_diTau.AddBinContent(3)
            self.cutflow_et.AddBinContent(3)
            self.cutflow_mt.AddBinContent(3)
            for i in range(len(self.GenPart.collection)):
                if abs(self.GenPart.collection[i].pdgId) == 11 and abs(self.GenPart.collection[self.GenPart.collection[i].genPartIdxMother].pdgId) == 15:
                    eCount += 1
                
                if abs(self.GenPart.collection[i].pdgId) == 13 and abs(self.GenPart.collection[self.GenPart.collection[i].genPartIdxMother].pdgId) == 15:
                    muCount += 1
                
            
            if eCount == 1:
                self.cutflow_et.AddBinContent(4)
            
            elif muCount ==1:
                self.cutflow_mt.AddBinContent(4)
            
            else:
                self.cutflow_diTau.AddBinContent(4)

        return False        


def call_postpoc(files):
		letsSortChannels = lambda: Channel(filename)
		nameStrip=files.strip()
		filename = (nameStrip.split('/')[-1]).split('.')[-2]
		p = PostProcessor(outputDir,[files], cut=cuts,branchsel=None,modules=[letsSortChannels()],noOut=True,outputbranchsel=outputbranches,histFileName="Gen_"+filename+".root",histDirName="Plots")
		p.run()


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Script to Handle root file preparation to split into channels. Input should be a singular files for each dataset or data already with some basic selections applied')
	#parser.add_argument('--Channel',help="enter either tt or et or mut. For boostedTau test enter test",required=True)
	parser.add_argument('--inputFile',help="enter the path to the location of input file set",default="")
	parser.add_argument('--ncores',help ="number of cores for parallel processing", default=1)
	args = parser.parse_args()

	#Define Event Selection - all those to be connected by and
	eventSelectionAND = ["MET_pt>200",
						"PV_ndof > 4",
						"abs(PV_z) < 24",
						"sqrt(PV_x*PV_x+PV_y*PV_y) < 2",
						"Flag_goodVertices",
						"Flag_globalSuperTightHalo2016Filter", 
						"Flag_HBHENoiseIsoFilter",
						"Flag_HBHENoiseFilter",
						"Flag_EcalDeadCellTriggerPrimitiveFilter",
						"Flag_BadPFMuonFilter",
						"Flag_eeBadScFilter"]

	fnames =[args.inputFile]
	outputDir = "."
	outputbranches = "keep_and_drop.txt"
	cuts = "&&".join(eventSelectionAND)
	argList = list()
	filename =""
	for file in fnames:
		argList.append(file)

	if int(args.ncores) == 1:
		for arr in argList:
			call_postpoc(arr)
	
	else:
		pool = np.Pool(int(args.ncores))
		res=pool.map(call_postpoc, argList)

                













    
