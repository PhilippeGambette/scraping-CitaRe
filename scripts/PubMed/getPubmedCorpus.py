import csv, requests, os, sys, time

# Please run this script outside peak hours for PubMed 
# (Monday to Friday, 5:00 AM to 9:00 PM, U.S. Eastern time)
# See https://www.ncbi.nlm.nih.gov/pmc/tools/oai/.

# Choice to activate or deactivate several steps of this script
"""
downloadFile = True
"""
downloadFile = False

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
with open(os.path.join(folder, fileName), newline='', encoding="ANSI") as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if "pmcid" in row:
            if not(row["pmcid"] in citingArticles):
                citingArticles[row["pmcid"]] = "1"
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