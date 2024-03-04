import requests, os, sys, time, re
# This script requires an ISTEX token, see below on line 5

istexpApiAccess = "https://api.istex.fr/"
token = "your_ISTEX_token_here"

# prepare part of a query corresponding to a block of at most 20 publications 
# to send to ISTEX
def publicationBlockToString(publicationBlock):
   #print(publicationBlock)
   publicationBlockString = "%22"
   nb = 0
   for pub in publicationBlock:
      if nb>0:
         publicationBlockString += "%22%20OR%20%22"
      publicationBlockString += pub
      nb += 1
   return publicationBlockString + "%22"


def getIstexUrls(publicationBlock):
   #   Create http header using the generated token.
   headers = {'Authorization': 'Bearer ' + token}

   #   Execute DSL query.
   urlquery = istexpApiAccess+'document/?q=(doi%3A'+publicationBlockToString(publicationBlock)+')&facet=corpusName[*]&size=20&rankBy=qualityOverRelevance&output=*&stats'
   #print(urlquery)

   resp = requests.get(
       urlquery,
       headers=headers)

   publications = resp.json()
   #print(publications["hits"])
   return publications["hits"]


allPublications = [
"10.9794/jspccs.32.199",
"10.9797/tsiss.2014.10.2.032",
"10.9798/kosham.2020.20.4.51"
]

folder = os.path.abspath(os.path.dirname(sys.argv[0]))

# Create output file
allCitingPapersNoDuplicate = open(os.path.join(folder,"allCitingPapersNoDuplicates.txt"),"w",encoding="utf-8")

allCitingPapers = open(os.path.join(folder,"citingPapers.tsv"),"r",encoding="utf-8")

citingPapers = {}

# Extract information from file citingPapers.tsv
for line in allCitingPapers:
   res = re.search("[^	]*	([^	]*)	[^	]*	[^	]*",line)
   if res:
      if res.group(1) not in citingPapers:
         citingPapers[res.group(1)] = 1
allCitingPapers.close()

allPublications = []
for publication in citingPapers:
   allCitingPapersNoDuplicate.writelines(publication+"\n")
   allPublications.append(publication)
allCitingPapersNoDuplicate.close()

# Build blocks of 20 publications to send them to ISTEX in only one query
print("Building publication blocks of 20 publications...")
publicationBlocks = []
publicationBlock = []
pubNb = 0
for publication in allPublications:
   if pubNb % 20 == 19: 
      publicationBlock.append(publication)
      publicationBlocks.append(publicationBlock)
      publicationBlock = []
   else:
      publicationBlock.append(publication)   
   pubNb += 1

if len(publicationBlock) > 0:
   publicationBlocks.append(publicationBlock)

print(str(len(publicationBlocks))+" publication blocks built!")

# prepare the output file of all papers found on ISTEX
# !!! sometimes ISTEX provides papers which do not correspond to the input DOIs !!!
# !!! the list needs to be filtered afterwards !!!
filepath = os.path.join(folder,"citingPapersOnIstex.tsv")

outputFile = open(filepath,"w",encoding="utf-8")
outputFile.writelines("citing paper DOI\tciting paper Istex\n")

blockNb = 1

# For each publication block get the ISTEX URL of the found papers
for publicationBlock in publicationBlocks:
   print("Getting publication block #"+str(blockNb))
   blockNb += 1
   cited = ""
   # Call the ISTEX API on the current publication block to get the URL of the found papers
   publications = getIstexUrls(publicationBlock)
   # List all results found by ISTEX
   for publication in publications:
      for url in publication["fulltext"]:
         if url["extension"]=="tei":
            # Save the URL found in ISTEX
            outputFile.writelines(publication["doi"][0]+"\t"+url["uri"]+"\n")
            print(publication["doi"][0]+"\t"+url["uri"]+"\n")
   time.sleep(2)
outputFile.close()
