# scraping-CitaRe

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