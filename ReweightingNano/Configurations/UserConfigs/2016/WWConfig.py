import ROOT
import os
import json

from Configurations.ConfigDefinition import ReweightConfiguration
from Configurations.Weights.CrossSectionWeightingModule.CrossSectionWeight import crossSectionWeight as crossSectionWeight
from Configurations.Weights.b2gAnalysisWeights.pileupWeightingModule.pileupWeight import pileupWeight_2016


WWConfig = ReweightConfiguration()
WWConfig.name = 'WW'
#WWConfig.jsonSampleFile = os.environ['CMSSW_BASE']+'/src/bbtautauAnalysisScripts/analysisCore/config/samples/2016_Samples.json'
WWConfig.jsonSampleFile = os.environ['CMSSW_BASE']+'/src/PhysicsTools/NanoAODTools/Samples/2016_Samples.json'

with open(WWConfig.jsonSampleFile,'r') as jsonFile:
    jsonInfo = json.load(jsonFile)
theFile = ROOT.TFile(jsonInfo[WWConfig.name]['file'])
totalNumberOfEvents = theFile.cutflow.GetBinContent(1)
theFile.Close()

WWConfig.inputFile = jsonInfo[WWConfig.name]['file']

crossSectionWeight.XS = jsonInfo[WWConfig.name]['XS'] * 1e-12 #XS in pb
crossSectionWeight.timePeriod = '2016'
crossSectionWeight.totalNumberOfEvents = totalNumberOfEvents
try:
    crossSectionWeight.forcedGenWeight = jsonInfo[WWConfig.name]['forcedGenWeight']
except KeyError:
    crossSectionWeight.forcedGenWeight = None


WWConfig.listOfWeights = [
    crossSectionWeight,
    pileupWeight_2016,
]
