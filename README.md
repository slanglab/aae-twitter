# aae-twitter/

Code and data to accompany: Masis, Eggleston, Green, Jones, Armstrong, and O'Connor. "Large-scale Twitter data reveals systematic geographic and social variation in African American English." Currently under peer-review. 

Contact: Tessa Masis (tmasis@cs.umass.edu), Brendan O'Connor (brenocon@cs.umass.edu)

See also: https://github.com/slanglab/Tw4Yr-Filters

## Contents

- `data/`
  - `documentation.md`: dataset documentation
  - `county.tsv`: tsv file with county-level linguistic feature relative incidences
  - `tract.zip`: compressed tsv file with tract-level linguistic feature relative incidences and demographic data

- `code/`
  - `getRegionData.py`: code to generate the tsv files in 'data/'
  - `analysis.py`: code to run the analyses in the paper (PCA, correlation analysis, linear regression, further explorations of the rural South and Mexican-American communities)
  - Note that these scripts require additional data (i.e. source demographic data files) or modifications in order to run on your computer


## Generating data files

Run the getRegionData.py script with the geographic granularity level ('tract' or 'county') as the first argument. For example:

    python3 getRegionData.py tract
        
This script requires files which are not included in this repo. It requires files with tweets and corresponding geoids and scores from feature detectors (where a score above a certain threshold indicates that the text data contains a given linguistic feature). If running the script at the tract-level, then the script also requires files with demographic data (we sourced this data from publicly available repositories, detailed in the Methods section of the paper). 

## Analyzing the data

The analysis script will print the results of the chosen analysis.

Run the analysis script with the chosen task as the first argument ('PCA-tract' performs PCA at the tract-level and prints the loadings for the first four principal components; 'PCA-county' does the same at the county-level; 'linreg' prints correlations between AAEScore and each demographic variable, and results from standardized linear regression analysis with all demographic variables (code can be easily modified to run linear regression analysis with any subset of demographic variables); 'rural-south' prints average AAEScores and feature z-scores for metro vs non-metro areas in each of the 4 US Census regions; 'hispanic-PC1' prints average AAEScores for different levels of Mexican, Puerto Rican, and African American populations). For example:

    python3 analysis.py PCA-tract
