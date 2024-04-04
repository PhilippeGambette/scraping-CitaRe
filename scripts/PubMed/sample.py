# -*- coding: utf-8 -*-
import csv, glob, os, re, requests, sys, time
from xml.dom import minidom

# pip3 install selenium
# install "geckodriver" from https://github.com/mozilla/geckodriver/releases
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile

# Please run this script outside peak hours for PubMed 
# (Monday to Friday, 5:00 AM to 9:00 PM, U.S. Eastern time)
# See https://www.ncbi.nlm.nih.gov/pmc/tools/oai/.

# Choice to activate or deactivate several steps of this script
"""
downloadFile = True
downloadPubmedFiles = True
saveCitedArticles = True
saveCitedArticlesHopefullyNotRetracted = True
"""

allCitedPapersFileName = "PubMed_retracted_publication_CitingPapers_citedPapersHopefullyNotRetracted.txt"
inputCsvFile = open(allCitedPapersFileName+".contexts.csv", "r", encoding="utf-8")
outputCsvFile = open(allCitedPapersFileName+".sample.tsv", "w", encoding="utf-8")
lineNb = 0
for line in inputCsvFile:
   lineNb += 1
   if lineNb % 400 == 0:
      outputCsvFile.writelines(line+"\n")
outputCsvFile.close()