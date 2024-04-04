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
downloadFile = False
downloadPubmedFiles = False
saveCitedArticles = False
saveCitedArticlesHopefullyNotRetracted = True

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
print(str(len(citingArticles)) + " citing articles found.")
print(str(len(retractedCitedArticles)) + " retracted cited articles found.")

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
            print("Article " + article + " already downloaded.")
        previousArticle = article
        articleNb += 1
    downloadArticle(previousArticle)
    
# get the text inside the XML node
def displayNodeText(node, forbiddenTags, valueTags, parentTag):
   if node.childNodes.length == 0:
      data = ""
      try:
         data = node.data
      except:
         pass
      if parentTag in valueTags:
            return ", " + data
      else:
         return ""
   else:
      text = ""
      for child in node.childNodes:
         if child.nodeName.lower() not in forbiddenTags:
            text += displayNodeText(child, forbiddenTags, valueTags, node.nodeName.lower())
      return text
    
# get the PubMedId inside the XML node
def getPmid(node):
   id = ""
   if node.childNodes.length > 0:
      for child in node.childNodes:
         if child.nodeName.lower() == "pub-id" and child.getAttribute("pub-id-type") == "pmid":
            id += child.childNodes[0].data
         else:
            id += getPmid(child)
   return id


# get the references of the article
def getReferences(node):
   if node.childNodes.length > 0:
      references = {}
      for child in node.childNodes:
         if child.nodeName.lower() == "ref":
            if child.hasAttribute("id"):
               referenceLabel = displayNodeText(child, [], ["article-title", "source", "year"], node.nodeName.lower()).replace("\n"," ").replace("  "," ").replace("  "," ").replace("  "," ").replace("  "," ").replace("  "," ").replace("  "," ")
               pubmedId = getPmid(child)
               references[child.getAttribute("id")] = {"label": referenceLabel[2:len(referenceLabel)], "pmid": pubmedId}
         else:
            childReferences = getReferences(child)
            if len(childReferences) > 0:
               for ref in childReferences:
                  references[ref] = childReferences[ref]
      return references
   else:
      return {}


# update foundPTagd with the text contained in p tags 
# where xref tags are replaced by cite tags using their rid attribute as id
def getPTags(node, foundPTags):
   result = ""
   if node.childNodes.length > 0:
      for child in node.childNodes:
         if child.nodeName.lower() == "p":
            pTag = getPTags(child, foundPTags)
            res = re.search("<cite", pTag)
            if res:
               foundPTags.append(pTag)
         if child.nodeName.lower() == "xref" and child.getAttribute("ref-type") == "bibr":
            # virer ce qui n'est pas une citation
            # virer ce qui est une citation d'article rétracté ou corrigé
            result += '<cite id="' + child.getAttribute("rid") + '">' + getPTags(child, foundPTags) + "</cite>"
         else:
            result += getPTags(child, foundPTags)
   else:
      try:
         result = node.data
      except:
         pass
   return result.replace("\n"," ")

# get the contexts of the article
def getContexts(node):
   contexts = []
   if node.childNodes.length > 0:
      for child in node.childNodes:
         childContexts = []
         if child.nodeName.lower() == "p":
            childContexts.append(displayNodeText(child, [], ["p", "xref"], node.nodeName.lower()))
         else:
            childContexts = getContexts(child)
         contexts += childContexts
         
   return contexts


# get contexts for citations of papers with PubMed 
# which are not already known as retracted
id = 0
allCitedPapersFileName = "PubMed_retracted_publication_CitingPapers_citedPapersHopefullyNotRetracted.txt"
hopefullyNotRetractedReferences = {}
if saveCitedArticlesHopefullyNotRetracted == True:
    outputFile = open(allCitedPapersFileName, "w", encoding="utf-8")
    outputCsvFile = open(allCitedPapersFileName+".csv", "w", encoding="utf-8")
    outputContextFile = open(allCitedPapersFileName+".contexts.csv", "w", encoding="utf-8")
    outputRetractedContextFile = open(allCitedPapersFileName+".retracted.contexts.csv", "w", encoding="utf-8")
    articleNb = 0
    citedArticlesHopefullyNotRetracted = {}
    for file in glob.glob(os.path.join(os.path.join(folder, "pubmedCorpus"), "*.xml")):
      #if len(file.replace("6468971.xml","")) < len(file):      
      if 1==1:
        articleNb += 1
        """
        print("Treating article " + file)
        """
        if articleNb % 100 == 0:
           print("Treating article #" + str(articleNb))
        # Open and parse the XML file
        article = minidom.parse(file)
        # Extract references from the article
        references = getReferences(article)
        refIds = references.keys()
        #print(references)
        # Count the number of retracted articles among the references
        retractedReferences = 0
        referencesWithPmidHopefullyNotRetracted = []
        referencesToPick = 0
        pickedReferences = 0
        for ref in references:
           if references[ref]["pmid"]!= "":
              if references[ref]["pmid"] in retractedCitedArticles:
                 retractedReferences += 1
                 referencesToPick += 1
              else:
                 referencesWithPmidHopefullyNotRetracted.append(references[ref]["pmid"])
                 #if referencesToPick > 0:
                 if 1==1:
                    if references[ref]["pmid"] in hopefullyNotRetractedReferences:
                       hopefullyNotRetractedReferences[references[ref]["pmid"]] += 1
                    else:
                       hopefullyNotRetractedReferences[references[ref]["pmid"]] = 1
                       outputFile.writelines(references[ref]["pmid"] + "\n")
                    referencesToPick -= 1
                    pickedReferences += 1
        # If there are still other references to pick:
        if referencesToPick > 0:
           stillPicking = True
           for ref in references:
              if references[ref]["pmid"]!= "":
                 if references[ref]["pmid"] in retractedCitedArticles:
                    stillPicking = False
                 else:
                    if stillPicking and referencesToPick > 0:
                       if references[ref]["pmid"] in hopefullyNotRetractedReferences:
                          hopefullyNotRetractedReferences[references[ref]["pmid"]] += 1
                       else:
                          hopefullyNotRetractedReferences[references[ref]["pmid"]] = 1
                          outputFile.writelines(references[ref]["pmid"] + "\n")
                       referencesToPick -= 1
                       pickedReferences += 1
        """
        print(str(retractedReferences) + " retracted cited articles")
        print(str(len(referencesWithPmidHopefullyNotRetracted)) + " hopefully not retracted cited articles")
        print(str(pickedReferences) + " picked articles among those")
        """
        outputCsvFile.writelines(str(articleNb)+"\t"+str(retractedReferences)+"\t"+str(len(referencesWithPmidHopefullyNotRetracted))+"\t"+str(pickedReferences)+"\t"+file+"\n")
        # Extract contexts from the article
        #contexts = getContexts(article)
        pTags = []
        contexts = getPTags(article, pTags)
        res = re.search("[^0-9]([0-9]+.xml)", file)
        if res:
            shortFileName = res.group(1)
        for tag in pTags:
            sentences = []
            regex = "^([^.;!?]+)([.;!?])(.*)$"
            tag = tag.replace(" et al.","et al")
            res = re.search(regex, tag)
            toAdd = ""
            while res:
                toAdd += res.group(1) + res.group(2)
                if len(res.group(3))==0 or res.group(3)[0] == " ":
                    sentences.append(toAdd)
                    toAdd = ""
                tag = res.group(3)
                res = re.search(regex, tag)
            for sentence in sentences:
                # Reformat citations in a simpler way (id put between pipes instead of cite tag)
                res = re.search('<cite id=.([^"]+)["]', sentence)
                if res:
                   #print(sentence)
                   #print(" ")
                   cleanedSentence = sentence.replace("</cite>","¤¤@@")
                   citedInSentence = []
                   res2 = re.search('^(.*)<cite id=.([^"]+)["]>[^¤]*¤¤@@(.*)', cleanedSentence)
                   while res2:
                      citedInSentence.append(res2.group(2))
                      cleanedSentence = res2.group(1) + "|" + res2.group(2) + "|" + res2.group(3)
                      res2 = re.search('^(.*)<cite id=.([^"]+)["]>[^¤]*¤¤@@(.*)', cleanedSentence)
                   #print(citedInSentence)
                   #print("Cleaned sentence: " + cleanedSentence)
                   
                   # keep the context if it contains more than 50 characters
                   # if it does not cite a retracted article
                   # and if it cites at least one article not known to be retracted and appearing in the list of references in the end of the article
                   if len(cleanedSentence) > 50:
                      retracted = 0
                      notRetracted = 0
                      source = ""
                      for ref in citedInSentence:
                         #print("pmid of " + ref + ": "+references[ref]["pmid"])
                         if ref in references and references[ref]["pmid"] in retractedCitedArticles:
                            #print(ref + " retracted!!!!!!!!!!!!!!!!!!!!!")
                            retracted += 1
                         else:
                            if ref in references and references[ref]["pmid"] in hopefullyNotRetractedReferences:
                               #print(ref + " probably not retracted :) :) :) :) :)")
                               source += references[ref]["pmid"] + "¤"
                               notRetracted += 1
                            #else:
                            #   #print("Problem here, the reference was not found")
                      if notRetracted > 0 and retracted == 0:
                         id += 1
                         outputContextFile.writelines(str(id) + "\t" + str(articleNb) + "\t" + shortFileName + "\t" + res.group(1) + "\t" + cleanedSentence + "\t" + source + "\n")
                      else:
                         if retracted > 0:
                            outputRetractedContextFile.writelines(str(id) + "\t" + str(articleNb) + "\t" + shortFileName + "\t" + res.group(1) + "\t" + cleanedSentence + "\t" + source + "\n")
    #print(citedArticles)
    outputFile.close()
    outputCsvFile.close()
    outputContextFile.close()
    outputRetractedContextFile.close()
print("A total of " + str(len(hopefullyNotRetractedReferences)) + " distinct hopefully not retracted cited articles were picked.")

"""
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
"""

"""
# Load a profile to automatically accept CSV downloads
profile = FirefoxProfile()
profile.set_preference("browser.download.panel.shown", False)
profile.set_preference("browser.helperApps.neverAsk.openFile","text/csv")
profile.set_preference("browser.download.folderList", 2);
# Download files in the corpus folder
profile.set_preference("browser.download.dir", os.path.join(folder,"corpusRetractedPmidDoi"))
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
#retractedCitedPapersFileName = "PubMed_retracted_publication_CitingPapers_citedPapers_Retracted.txt"
outputCsvFile = open(allCitedPapersFileName, "w", encoding="utf-8")
#outputCsvFileRetracted = open(retractedCitedPapersFileName, "w", encoding="utf-8")
articlesToTest = 1
for line in inputFile:
    res = re.search("[ ]*([0-9]*)[\r\n]*$", line)
    if res:
        if res.group(1) in retractedCitedArticles:
            outputCsvFile.writelines(res.group(1)+"\tr\n")
            #retractedArticlesToTest += 1
            #textArea.send_keys(res.group(1) + "\n")
            #if retractedArticlesToTest % 100 == 0:
            #    driver.find_element_by_css_selector('#format_csv_rb').click()
            #    driver.find_element_by_css_selector('#convert-button').click()
            #    time.sleep(1)
            #    driver.find_element_by_css_selector('#clear-button').click()
            #    print("Downloaded information about the first " + str(articlesToTest) + " first ids of retracted papers.")
            #    textArea = driver.find_element_by_css_selector("#Ids")
        else:
            outputCsvFile.writelines(res.group(1)+"\t?\n")
    
    #textArea.send_keys(res.group(1) + "\n")        
    #if articlesToTest % 100 == 0:
    #    driver.find_element_by_css_selector('#format_csv_rb').click()
    #    driver.find_element_by_css_selector('#convert-button').click()
    #    time.sleep(1)
    #    driver.find_element_by_css_selector('#clear-button').click()
    #    print("Downloaded information about the first " + str(articlesToTest) + " first ids.")
    #    textArea = driver.find_element_by_css_selector("#Ids")
    #articlesToTest += 1
    

outputCsvFile.close()
#outputCsvFileRetracted.close()
print(str(articlesToTest) + " articles to test to know whether they were retracted")
"""


"""
# Gather all information about retracted articles
retractedArticlesTreated = 0
retractedArticlesTreatedWithNoPmid = 0
retractedCitedArticleInfos = {}
print(os.path.join(os.path.join(folder, "corpusRetractedPmidDoi"), "*.csv"))
for file in glob.glob(os.path.join(os.path.join(folder, "corpusRetractedPmidDoi"), "*.csv")):
    with open(file, newline='', encoding="ANSI") as f:
        reader = csv.DictReader(f, delimiter=',')
        for row in reader:
            if "PMID" in row :
               if row["PMID"] in retractedCitedArticles:
                  retractedCitedArticleInfos[row["PMID"]] = {"DOI":row["DOI"], "PMCID":row["PMCID"]}
               else:
                  retractedArticlesTreatedWithNoPmid += 1
               #   print("Unknown PMID: " + row["PMID"])
            else:
               print(file)
               print(row)
            retractedArticlesTreated += 1
print(str(len(retractedCitedArticleInfos)) + " retracted cited articles treated")
print(str(retractedArticlesTreatedWithNoPmid) + " articles without PMID among those")
print(str(retractedArticlesTreated) + " articles in total")

# Save all information about retracted articles
outputCsvFile = open("PubMed_retracted_publication_CitingPapers_citedPapers_Retracted.tsv", "w", encoding="utf-8")
noPMCID = 0
noDOI = 0
PMCID = 0
for retractedArticle in retractedCitedArticles:
    if str(type(retractedCitedArticleInfos[retractedArticle])) != "<class 'str'>":
        if retractedCitedArticleInfos[retractedArticle]["PMCID"] == "":
            noPMCID += 1
        else:
            PMCID += 1
        if retractedCitedArticleInfos[retractedArticle]["DOI"] == "":
            noDOI += 1
        outputCsvFile.writelines(retractedArticle + "\t" + retractedCitedArticleInfos[retractedArticle]["PMCID"] + "\t\"" + retractedCitedArticleInfos[retractedArticle]["DOI"] + "\"\n")
    else:
        print(retractedArticle + " was not found in the information files.")        
print(str(noPMCID) + " files without PMCID")
print(str(PMCID) + " files with PMCID")
print(str(noDOI) + " files without DOI")
outputCsvFile.close()
"""