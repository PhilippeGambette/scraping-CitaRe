# scraping-CitaRe

These scripts were built in a collaboration between Frédérique Bordignon and Philippe Gambette for the Cita&Re project (study of critical citations received by retracted papers) supervised by Frédérique Bordignon and Marianne Noël at LISIS.

This work has been initially funded by the French government under the management of the Agence Nationale de la Recherche (ANR-16-IDEX-0003-ISITE FUTURE) and then by the Horizon 2020 Framework Programme of the European Union (H2020-ERC-2020-SyG - Grant Agreement No. 951393).

## scripts

### 01-getDimensionsIds.py

`01-getDimensionsIds.py` retrieves identifiers from the Dimensions database (https://www.dimensions.ai/) from a list of DOI identifiers

To use this Python3 script, put your Dimensions API key on line 11, update the DOI list starting on line 54 and execute the script, which will generate a TSV file named `DOI-dimensionsId.tsv` in the same folder, with DOI identifiers in the first column and Dimensions identifiers in the second one.

### 02-getCitingPapers.py

`02-getCitingPapers.py` retrieves citing papers from the Dimensions database (https://www.dimensions.ai/) from a list of Dimensions identifiers.

To use this Python3 script, put your Dimensions API key on line 11, update the DOI list starting on line 53 and execute the script, which will generate a TSV file named `citingPapersNb.tsv` in the same folder, with Dimensions identifiers in the first column and the number of citing papers according to the Dimensions database in the second column, as well as another TSV file named `citingPapers.tsv` in the same folder, with Dimensions identifiers in the first column, and in the next columns, DOI identifiers of citing papers (if they exist), Dimensions identifiers of citing papers and publication year of citing papers.

### 03-getIstexIds.py

`03-getIstexIds.py` retrieves identifiers from the ISTEX database (https://www.istex.fr/) from a list of DOI identifiers.

To use this Python3 script, put your ISTEX token on line 5, update the DOI list starting on line 39 and execute the script, which will generate a TSV file named `citingPapersOnIstex.tsv` in the same folder, with DOI identifiers in the first column and the URL of the corresponding XML-TEI file on ISTEX in the second column.

Caution! This list must be checked because ISTEX may provide information about papers which do not correspond to the input DOI identifiers.

### PubMed/getPubmedCorpus.py

`getPubmedCorpus.py` retrieves the XML file of publications on PubMed and extracts contexts of citations from these files, containing at least 50 characters, citing no article known to be retracted, citing at least one article with a PubMed Id, not known to be retracted and found in the reference list in the end of the article.

A few variables are used to activate some functionalities, around line 20 of the script:
* if `downloadFile` is set to true, `PubMed_retracted_publication_CitCntxt_withYR.tsv` is automatically downloaded from https://databank.illinois.edu/datafiles/kacny/download (see Hsiao, Tzu-Kun; Schneider, Jodi (2021): Dataset for "Continued use of retracted papers: Temporal trends in citations and (lack of) awareness of retractions shown in citation contexts in biomedicine". University of Illinois at Urbana-Champaign. https://doi.org/10.13012/B2IDB-8255619_V1)
* if `downloadPubmedFiles` is set to true, `PubMed_retracted_publication_CitCntxt_withYR.tsv` is parsed to extract PMID identifiers of cited retracted articles and citing articles and to download the citing articles, in the XML format, to the `pubmedCorpus` folder
* if `saveCitedArticlesHopefullyNotRetracted` is set to true, all files in the `pubmedCorpus` folder are downloaded


## Use of this script

Part of the dataset available at https://zenodo.org/records/10694465  was obtained from the script PubMed/getPubmedCorpus.py using the process described below:
* download the file `PubMed_retracted_publication_CitCntxt_withYR_v3.tsv` from https://databank.illinois.edu/datafiles/kacny/download (see Hsiao, Tzu-Kun; Schneider, Jodi (2021): Dataset for "Continued use of retracted papers: Temporal trends in citations and (lack of) awareness of retractions shown in citation contexts in biomedicine". University of Illinois at Urbana-Champaign. https://doi.org/10.13012/B2IDB-8255619_V1) or let the script `getPubmedCorpus.py` automatically download it with option `downloadFile` set to true
* 28057 XML files of articles citing retracted articles, according to the file above, are downloaded from PubMedCentral (using the script `getPubmedCorpus.py` with option `downloadPubmedFiles` set to true)
  * for all these 28057 articles, [this spreadsheet file](https://docs.google.com/spreadsheets/d/1urEq8TDnvO9jmbzGvnsKI12z7N7y7sm4MmUiNa_gxEw/edit?usp=sharing) shows how many retracted articles (column B) and how many articles with PumMed ID, which are not known to be retracted (column C) they cite: 1 733 747 in total
  * in these 28057 articles, we list all contexts of citations containing at least 50 characters, citing no article known to be retracted, citing at least one article with a PubMed Id, not known to be retracted and found in the reference list: 1 278 602 contexts are listed: the CSV file contained in the file [PubMed_retracted_publication_CitingPapers_citedPapersHopefullyNotRetracted.txt.contexts.zip](https://github.com/PhilippeGambette/scraping-CitaRe/blob/87f971db57655cc56532db434c801b8e04efaaad/scripts/PubMed/PubMed_retracted_publication_CitingPapers_citedPapersHopefullyNotRetracted.txt.contexts.zip)
  * extraction, with the script called `sample.py`, of 1 line over 400 in this file: this provides a file with 3196 contexts of citations of articles, not known to be retracted, cited in articles which also cite retracted articles: the file `PubMed_retracted_publication_CitingPapers_citedPapersHopefullyNotRetracted.txt.sample.tsv`