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
"""
downloadFile = False
downloadPubmedFiles = False
saveCitedArticles = False

# Get the current folder
folder = os.path.abspath(os.path.dirname(sys.argv[0]))


# Download the context dataset from the dataset available at https://doi.org/10.13012/B2IDB-8255619_V1
# Dataset for "Continued use of retracted papers: Temporal trends in citations and (lack of) awareness of retractions shown in citation contexts in biomedicine"
datasetUrl = "https://databank.illinois.edu/datafiles/kacny/download"

# Name to save the downloaded file
fileName = "PubMed_retracted_publication_CitCntxt_withYR.tsv"

if downloadFile:
    # Download the file
    response = requests.get(datasetUrl)
    # Save the file
    open(os.path.join(folder, fileName), 'wb').write(response.content)

# Open the context dataset file and build a list of all pubmed id
# of articles containing these citation contexts (citing retracted papers)
citingArticles = {}
retractedCitedArticles = {}
with open(os.path.join(folder, fileName), newline='', encoding="ANSI") as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if "pmcid" in row:
            if not(row["pmcid"] in citingArticles):
                citingArticles[row["pmcid"]] = "1"
                retractedCitedArticles[row["intxt_pmid"]] = "1"
        else:
            print("no pmcid!")
print(str(len(citingArticles)) + " citing articles found!")

# Create corpus folder
if not os.path.exists(os.path.join(folder, "pubmedCorpus")):
    os.makedirs(os.path.join(folder, "pubmedCorpus"))

def downloadArticle(pubmedId):
    response = requests.get(articleUrlBegin + pubmedId + articleUrlEnd)
    # Save the previous article
    open(os.path.join(os.path.join(folder, "pubmedCorpus"), pubmedId + ".xml"), 'wb').write(response.content)
    print("Article " + pubmedId + ".xml downloaded")
    time.sleep(5)

articleUrlBegin = "https://www.ncbi.nlm.nih.gov/pmc/oai/oai.cgi?verb=GetRecord&identifier=oai:pubmedcentral.nih.gov:"
articleUrlEnd = "&metadataPrefix=pmc"

if downloadPubmedFiles:
    # Download all citing articles from PubMed
    previousArticle = ""
    articleNb = 0
    for article in citingArticles:
        if not os.path.exists(os.path.join(os.path.join(folder, "pubmedCorpus"), article + ".xml")):
            # In case the article is not found, download the previous article
            downloadArticle(previousArticle)
            # (that article may have not have been fully saved to the disk)
        else:
            print("Article " + article + " already downloaded!")
        previousArticle = article
        articleNb += 1
    downloadArticle(previousArticle)
    
# get the text inside the XML node
def displayNodeText(node, forbiddenTags, valueTags, parentTag, idType):
   if node.childNodes.length == 0:
      data = ""
      try:
         data = node.data
      except:
         pass
      if parentTag in valueTags:
         if idType == "":
            return ", " + data
         else:
            return "," + idType + "¤" + data
      else:
         return ""
   else:
      text = ""
      for child in node.childNodes:
         if child.nodeName.lower() not in forbiddenTags:
            # restrict to pmid id only:
            if child.nodeName.lower() == "pub-id" and child.getAttribute("pub-id-type") != "pmcid":
               child.nodeName = "pub"
            # get all reference ids
            #if child.nodeName.lower() == "pub-id":
            #   idType = child.getAttribute("pub-id-type")
            text += displayNodeText(child, forbiddenTags, valueTags, node.nodeName.lower(), idType)
      return text

# get the references of the article
def getReferences(node):
   if node.childNodes.length > 0:
      references = {}
      for child in node.childNodes:
         if child.nodeName.lower() == "ref":
            if child.hasAttribute("id"):
               referenceLabel = displayNodeText(child, [], ["article-title", "source", "year"], node.nodeName.lower(), "").replace("\n"," ").replace("  "," ").replace("  "," ").replace("  "," ").replace("  "," ").replace("  "," ").replace("  "," ")
               pubmedId = displayNodeText(child, [], ["pub-id"], node.nodeName.lower(), "")
               references[child.getAttribute("id")] = {"label": referenceLabel[2:len(referenceLabel)], "id": pubmedId[1:len(pubmedId)]}
         else:
            childReferences = getReferences(child)
            if len(childReferences) > 0:
               references = childReferences
      return references
   else:
      return {}

# get the contexts of the article
def getContexts(node):
   contexts = []
   if node.childNodes.length > 0:
      for child in node.childNodes:
         childContexts = []
         if child.nodeName.lower() == "p":
            childContexts.append(displayNodeText(child, [], ["p", "xref"], node.nodeName.lower(), ""))
         else:
            childContexts = getContexts(child)
         contexts += childContexts
         
   return contexts


# Build a list of pubmed ids of all articles cited 
# in this corpus of articles citing retracted articles
allCitedPapersFileName = "PubMed_retracted_publication_CitingPapers_citedPapers.txt"
if saveCitedArticles == True:
    outputFile = open(allCitedPapersFileName, "w", encoding="utf-8")
    articleNb = 0
    citedArticles = {}
    for file in glob.glob(os.path.join(os.path.join(folder, "pubmedCorpus"), "*.xml")):
        articleNb += 1
        if articleNb % 1000 == 0:
           print("Treating article #" + str(articleNb))
        # Open and parse the XML file
        article = minidom.parse(file)
        # Extract references from the article
        references = getReferences(article)
        if articleNb % 1000 == 0:
           print(str(len(citedArticles)) + " distinct cited articles found with a pubmed Id so far")
        #   print(references)
        for ref in references:
           if references[ref]["id"] in citedArticles:
              citedArticles[references[ref]["id"]] += 1
           else:
              citedArticles[references[ref]["id"]] = 1
              if saveCitedArticles == True:
                 outputFile.writelines(references[ref]["id"] + "\n")
        # Extract contexts from the article
        #contexts = getContexts(article)
        #print(contexts)
    #print(citedArticles)
    outputFile.close()


# Load a profile to automatically accept CSV downloads
profile = FirefoxProfile()
profile.set_preference("browser.download.panel.shown", False)
profile.set_preference("browser.helperApps.neverAsk.openFile","text/csv")
profile.set_preference("browser.download.folderList", 2);
# Download files in the corpus folder
profile.set_preference("browser.download.dir", os.path.join(folder,"corpus"))
try:
   # May not work for MacOS but required to automatically download Wikisource files on Windows
   driver = webdriver.Firefox(firefox_profile=profile)
except:
   # Should work for MacOS
   driver = webdriver.Firefox()
   pass
# Specify a 15 second timeout to avoid getting stuck after each download
driver.set_page_load_timeout(15)
driver.get("https://www.ncbi.nlm.nih.gov/pmc/pmctopmid/")
time.sleep(2)
textArea = driver.find_element_by_css_selector("#Ids")

# Save all pubmed id of cited papers in a file
# indicating whether they were retracted or not
inputFile = open(allCitedPapersFileName, "r", encoding="utf-8")
allCitedPapersFileName = "PubMed_retracted_publication_CitingPapers_citedPapers_RetractedOrNot.tsv"
outputCsvFile = open(allCitedPapersFileName, "w", encoding="utf-8")
articlesToTest = 1
for line in inputFile:
    res = re.search("[ ]*([0-9]*)[\r\n]*$", line)
    if res:
        if res.group(1) in retractedCitedArticles:
            outputCsvFile.writelines(res.group(1)+"\tr\n")
        else:
            outputCsvFile.writelines(res.group(1)+"\t?\n")
    if articlesToTest > 50200:
        textArea.send_keys(res.group(1) + "\n")        
    if articlesToTest % 100 == 0 and articlesToTest > 50200:
        driver.find_element_by_css_selector('#format_csv_rb').click()
        driver.find_element_by_css_selector('#convert-button').click()
        time.sleep(1)
        driver.find_element_by_css_selector('#clear-button').click()
        print("Downloaded information about the first " + str(articlesToTest) + " first ids.")
        textArea = driver.find_element_by_css_selector("#Ids")


    articlesToTest += 1
outputCsvFile.close()
print(str(articlesToTest) + " articles to test to know whether they were retracted")


