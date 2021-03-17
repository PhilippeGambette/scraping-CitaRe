import requests, os, sys, time
# This script requires a Dimensions API key, see below on line 11

ENDPOINT = "app.dimensions.ai"

#   The credentials to be used
login = {
    #'username': USERNAME,
    #'password': PASSWORD,
    # NOTE if you have a USERNAME and PASSWORD, uncomment the two lines above and uncomment the next one:
    'key': "your_API_key_here"
}


def publicationBlockToString(publicationBlock):
   #print(publicationBlock)
   publicationBlockString = "\""
   nb = 0
   for pub in publicationBlock:
      if nb>0:
         publicationBlockString += "\",\""
      publicationBlockString += pub
      nb += 1
   return publicationBlockString+"\""


def getCitingPapers(publicationBlock): 
   #   Send credentials to login url to retrieve token. Raise
   #   an error, if the return code indicates a problem.
   #   Please use the URL of the system you'd like to access the API
   #   in the example below.
   resp = requests.post(f'https://{ENDPOINT}/api/auth.json', json=login)
   resp.raise_for_status()

   #   Create http header using the generated token.
   headers = {
       'Authorization': "JWT " + resp.json()['token']
   }

   #   Execute DSL query.
   query = 'search publications where reference_ids in ['+ publicationBlockToString(publicationBlock) +'] return publications[id+doi+title+year+reference_ids] limit 1000'
   #print(query)
   resp = requests.post(
       f'https://{ENDPOINT}/api/dsl.json',
       data=query.encode(),
       headers=headers)

   publications = resp.json()["publications"]
   return publications


allPublications = [
"pub.1062668377",
"pub.1021525470",
"pub.1062616798",
"pub.1009856991",
"pub.1043622590",
"pub.1010153867",
"pub.1010773188",
"pub.1046925820",
"pub.1003999565",
"pub.1026351693",
"pub.1052378140",
"pub.1039560253",
"pub.1013926946",
"pub.1031653078",
"pub.1037465370",
"pub.1062469822",
"pub.1038347164",
"pub.1043116196",
"pub.1016013426",
"pub.1018766106",
"pub.1005691701",
"pub.1068435179",
"pub.1046580900",
"pub.1051200782",
"pub.1069183162",
"pub.1000280708",
"pub.1041467060",
"pub.1026951142",
"pub.1030135001",
]





publicationBlocks = []
publicationBlock = []
pubNb = 0
# Create one block for each publication
for publication in allPublications:
   publicationBlocks.append([publication])

print(str(len(publicationBlocks))+" publication blocks built!")

folder = os.path.abspath(os.path.dirname(sys.argv[0]))
filepath = os.path.join(folder,"citingPapers.tsv")
filepath2 = os.path.join(folder,"citingPapersNb.tsv")

# Prepare the output files containing the citing papers
outputFile = open(filepath,"w",encoding="utf-8")
outputFile.writelines("cited paper\tciting paper DOI\tciting paper Dimensions Id\tyear\n")
outputFile2 = open(filepath2,"w",encoding="utf-8")
outputFile2.writelines("cited paper\tciting paper nb\n")

# List all publication blocks (that is, all publications) to find the citing papers
blockNb = 1
for publicationBlock in publicationBlocks:
   print("Getting publication block #"+str(blockNb))
   blockNb += 1
   cited = ""
   for publication in publicationBlock:
      cited = publication
   # Retrieve all citing papers using the API
   publications = getCitingPapers(publicationBlock)
   print(str(len(publications))+" citing papers")
   # Add the number of citing papers to the second output file
   outputFile2.writelines(cited+"\t"+str(len(publications))+"\n")
   # Save information in the first output file
   for publication in publications:
      # Save year if the data is known
      year = ""
      if "year" in publication:
         year = str(publication["year"])
      # Save all info, including the DOI if it is known
      if "doi" in publication:
         outputFile.writelines(cited+"\t"+publication["doi"]+"\t"+publication["id"]+"\t"+year+"\n")
      else:
         outputFile.writelines(cited+"\t\t"+publication["id"]+"\t"+year+"\n")
   time.sleep(2)
outputFile.close()
outputFile2.close()