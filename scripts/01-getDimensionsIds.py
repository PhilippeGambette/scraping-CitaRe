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

# Transform a list of DOIs into a string where DOIs
# are put inside double quotes and separated by a comma
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

# Send the query to get an object containing the Dimension Ids
def getDimensionsIds(publicationBlock): 
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
   query = 'search publications where doi in ['+ publicationBlockToString(publicationBlock) +'] return publications[doi+type+id]'
   #print(query)
   resp = requests.post(
       f'https://{ENDPOINT}/api/dsl.json',
       data=query.encode(),
       headers=headers)

   publications = resp.json()["publications"]
   return publications


allPublications = [
"10.1007/s13277-013-1022-6",
"10.1007/s13277-014-1849-5",
"10.1007/s13277-014-2410-2",
"10.1038/nature12873",
"10.1038/nature13498",
"10.1038/nature14512",
"10.1038/nature14619",
"10.1126/science.1250770",
"10.1126/science.1251277",
"10.1126/science.1257521",
"10.1126/science.349.6245.250",
"10.1126/science.aad5937",
"10.1126/science.aag3161",
"10.1007/s13277-014-2578-5",
"10.1007/s13277-014-2802-3",
"10.1007/s13277-015-3212-x",
"10.1038/519S14a",
"10.1038/nature11957",
"10.1038/nature13032",
"10.1038/nature14039",
"10.1038/nature14144",
"10.1126/science.1251560",
"10.1126/science.aad6359",
"10.17660/ActaHortic.2015.1089.62",
"10.2174/138955710791384054",
"10.1002/(SICI)1097-0045(199602)28:2<117::AID-PROS7>3.0.CO;2-D",
"10.1002/(SICI)1097-0045(19990901)40:4<256::AID-PROS7>3.0.CO;2-I",
"10.1002/(SICI)1097-0142(19970801)80:3<372::AID-CNCR4>3.0.CO;2-U",
"10.1002/(SICI)1097-4652(199611)169:2<269::AID-JCP6>3.0.CO;2-M",
"10.1002/(SICI)1521-3951(200105)225:1<209::AID-PSSB209>3.0.CO;2-T",
"10.1002/(SICI)1521-396X(199902)171:2<511::AID-PSSA511>3.0.CO;2-B",
"10.1002/(SICI)1521-396X(199912)176:2<1009::AID-PSSA1009>3.0.CO;2-H",
"10.1002/1097-0142(19920915)70:4+<1765::AID-CNCR2820701618>3.0.CO;2-C",
"10.1002/1097-0142(19940115)73:2<344::AID-CNCR2820730218>3.0.CO;2-Y",
"10.1002/1439-7641(20010316)2:3<167::AID-CPHC167>3.0.CO;2-F",
"10.1002/1521-3773(20010504)40:9<1732::AID-ANIE17320>3.0.CO;2-7",
"10.1002/1521-3951(200009)221:1<R4::AID-PSSB99994>3.0.CO;2-R",
"10.1002/1521-3951(200103)224:2<R7::AID-PSSB99997>3.0.CO;2-I",
"10.1002/1521-3951(200108)226:2<257::AID-PSSB257>3.0.CO;2-C",
"10.1002/1521-396X(199705)161:1<301::AID-PSSA301>3.0.CO;2-Q",
"10.1002/1521-396X(200004)178:2<805::AID-PSSA805>3.0.CO;2-K",
"10.1002/1521-396X(200009)181:1<185::AID-PSSA185>3.0.CO;2-G",
"10.1002/1521-4095(200010)12:20<1539::AID-ADMA1539>3.0.CO;2-S",
"10.1002/adhm.201200070",
"10.1002/adhm.201200088",
"10.1002/adhm.201200098",
"10.1002/adhm.201200099",
"10.1002/adhm.201200105",
"10.1002/adhm.201200112",
"10.1002/adhm.201200119",
"10.1002/adhm.201200125",
"10.1002/adhm.201200140",
"10.1002/adhm.201200142",
"10.1002/adhm.201200149",
"10.1002/adhm.201200152",
"10.1002/adhm.201200154",
"10.1002/adhm.201200159",
"10.1002/adhm.201200164",
"10.1002/adhm.201200176",
"10.1002/adhm.201200177",
"10.1002/adhm.201200178",
"10.1002/adhm.201200181",
"10.1002/adhm.201200183",
"10.1002/adhm.201200189",
"10.1002/adhm.201200193",
"10.1002/adhm.201200200",
"10.1002/adhm.201200205",
"10.1002/adhm.201200210",
"10.1002/adhm.201200215",
"10.1002/adhm.201200220",
"10.1002/adhm.201200227",
"10.1002/adhm.201200233",
"10.1002/adhm.201200234",
"10.1002/adhm.201200238",
"10.1002/adhm.201200248",
"10.1002/adhm.201200262",
"10.1002/adhm.201200269",
"10.1002/adhm.201200278",
"10.1002/adhm.201200280",
"10.1002/adhm.201200281",
"10.1002/adhm.201200285",
"10.1002/adhm.201200287",
"10.1002/adhm.201200294",
"10.1002/adhm.201200296",
"10.1002/adhm.201200299",
"10.1002/adhm.201200302",
"10.1002/adhm.201200303",
"10.1002/adhm.201200318",
"10.1002/adhm.201200326",
"10.1002/adhm.201200332",
"10.1002/adhm.201200333",
"10.1002/adhm.201200335",
"10.1002/adhm.201200338",
"10.1002/adhm.201200340",
"10.1002/adhm.201200343",
"10.1002/adhm.201200347",
"10.1002/adhm.201200350",
"10.1002/adhm.201200353",
"10.1002/adhm.201200356",
"10.1002/adhm.201200357",
"10.1002/adhm.201200358",
]








print("Building publication blocks of 20 publications...")

# Create a list, publicationBlocks, of lists of 20 DOIs
publicationBlocks = []
publicationBlock = []
pubNb = 0
for publication in allPublications:
   if pubNb % 20 == 19:
      # if 20 publications have been added in publicationBlock
      # add it to publicationBlocks and empty it
      publicationBlock.append(publication)
      publicationBlocks.append(publicationBlock)
      publicationBlock = []
   else:
      # add the publication to publicationBlock
      publicationBlock.append(publication)
   pubNb += 1

if len(publicationBlock) > 0:
   publicationBlocks.append(publicationBlock)

print(str(len(publicationBlocks))+" publication blocks built!")

# Create the output file in the same folder
folder = os.path.abspath(os.path.dirname(sys.argv[0]))
filepath = os.path.join(folder, "DOI-dimensionsId.tsv")
outputFile = open(filepath, "w", encoding="utf-8")

# Get the Dimension Ids of each publication block
blockNb = 1
for publicationBlock in publicationBlocks:
   print("Getting publication block #"+str(blockNb))
   blockNb += 1
   publications = getDimensionsIds(publicationBlock)
   for publication in publications:
      # add a new line to the TSV output file for each found publication
      #print(publication["doi"]+";"+publication["id"])
      outputFile.writelines(publication["doi"]+"\t"+publication["id"]+"\n")
   # wait before sending the query for the next publication block, to avoid sending more than 30 queries per minute
   time.sleep(2.1)

# Close the output file
outputFile.close()