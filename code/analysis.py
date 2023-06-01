import numpy as np 
import pandas as pd
import sys
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression as LR
from sklearn.preprocessing import scale
from scipy.stats import pearsonr
from scipy.stats import zscore
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from urllib.request import urlopen
import json
from collections import defaultdict
import pingouin as pg
import argparse

# Code for conducting PCA and linreg analysis of data
# Takes 1 argument: 
#       task ('PCA-tract', 'PCA-county', 'linreg', 'rural-south', or 'hispanic-PC1')
# Example commandline: python3 analysis.py PCA-tract


def getData(f):
    # Retrieve data created from getRegionData.py 
    data = pd.read_csv(f+".tsv", sep='\t')
    data = data.dropna().reset_index()
    # Get ID codes for each region
    fips = [str(x) for x in data["region"]]
    for i in range(len(fips)):
        if (f == "tract" and len(fips[i]) == 10) or (f == "county" and len(fips[i]) == 4):
            fips[i] = "0" + fips[i]
    # Separate linguistic data 
    if f == "tract":
        ling_data = data.drop(["region","latitude","longitude","ruca","median age",
            "AA pop","white pop","Hispanic pop","Mexican pop","PR pop",
            "median household income","county AA pop","county white pop",
            "county Hispanic pop","county historical AA pop"], axis=1)
        data = data.drop(["zero poss","overt poss","zero copula","overt copula","gone", 
            "habitual be","resultant done", "be done", "steady", "finna", "neg concord", 
            "single neg", "neg auxiliary inversion", "ain't", "zero 3rd sing pres -s", 
            "is/was generalization", "double object", "wh-question", "region"], axis=1)
    else:
        ling_data = data.drop(["region"], axis=1)
    ling_data = ling_data.apply(zscore)
    return ling_data, data, fips


def getPCAData(ling_data, verbose=False):
    # Retrieves first PC for PCA-transformed linguistic data
    pca = PCA(n_components=4, svd_solver='full')
    pca_data = pca.fit_transform(ling_data)
    pc1 = np.array(pca_data[:,0])   
    if verbose:
        loadings = pd.DataFrame(pca.components_.T * np.sqrt(pca.explained_variance_), columns=['PC1','PC2','PC3','PC4'], index=ling_data.columns)    # correlation form of loadings
        print("Feature loadings for each principal component:")
        print(loadings)
        print("\nExplained variance ratio for each principal component:")
        print(pca.explained_variance_ratio_)
    return pc1


def linReg(data, pc1, verbose=False):
    data = data.apply(zscore)
    # Print correlations between demographic variables and PC1
    demovars = ["AA pop","county AA pop","county historical AA pop","Hispanic pop",
        "county Hispanic pop","Mexican pop","PR pop","latitude","longitude",
        "ruca","median household income","median age"]
    print("Pearson's r between PC1 and demographic variables (r, p-value):")
    for d in demovars:
        print(d + " + PC1:\t"+str(pearsonr(np.array(data[d]), pc1)))
    if verbose: 
        print("\n\nPartial correlation b/n Hispanic and white pop. when conditioned on AA pop.:") 
        print(pg.partial_corr(data=data, x="Hispanic pop", y="white pop", covar="AA pop"))
    # Linear regression, where PC1 is outcome variable
    if verbose:
        vif = pd.DataFrame()
        data = data.drop(["white pop", "county white pop"], axis=1)
        vif["features"] = data.columns
        vif["vif_Factor"] = [variance_inflation_factor(data.values, i) for i in range(data.shape[1])]
        print("\n\nVIF factors: \n" + str(vif))
    print("\n\nLinear regression results: ")
    yvalues = pc1
    xvalues = [[        # Can comment out any variables you don't want to include
        data["AA pop"][i], 
        data["county AA pop"][i], 
        data["county historical AA pop"][i], 
        data["Hispanic pop"][i],
        data["Mexican pop"][i],
        data["PR pop"][i],
        data["county Hispanic pop"][i], 
        data["ruca"][i], 
        data["latitude"][i], 
        data["longitude"][i], 
        data["median household income"][i], 
        data["median age"][i]
        ] for i in range(len(yvalues))]
    xvalues = sm.add_constant(xvalues)
    model = sm.OLS(yvalues, xvalues)
    model = model.fit()
    print(model.summary())


def ruralSouth(fips, data, ling_data, pc1):
    ne = ["09","23","25","33","44","50","34","36","42"]
    s = ["10","11","12","13","24","37","45","51","54","01","21","28","47","05","22","40","48"]
    mw = ["17","18","26","39","55","19","20","27","29","31","38","46"]
    w = ["04","08","16","30","32","35","49","56","02","06","15","41","53"]
    pc1s = defaultdict(lambda: [])
    feats = defaultdict(lambda: [])
    counts = defaultdict(lambda: 0)
    for i in range(len(fips)):
        pop = data["AA pop"][i]
        if pop >= .15 and pop < .25:    # Within 15-25% relative AA pop
            ruca = data["ruca"][i]
            x = pc1[i]
            y = np.array([ling_data[x][i] for x in ling_data.columns])
            z = fips[i][:2]
            if ruca <= 3:   name = "metro"
            else:           name = "nonm"
            if z in ne:     name = "ne-" + name
            elif z in s:    name = "s-" + name
            elif z in mw:   name = "mw-" + name
            elif z in w:    name = "w-" + name
            pc1s[name].append(x)
            feats[name].append(y)
            counts[name] += 1
    for k,v in pc1s.items():
        print("Region:\t" + k)
        print("Average PC1:\t"+str(np.mean(np.array(pc1s[k]))))
        print("Total # tracts:\t"+str(counts[k]))
        x = np.mean(np.array(feats[k]), axis=0)
        print("Average feature z-scores:")
        for i in range(len(ling_data.columns)):
            if i == 0: continue
            print(ling_data.columns[i] + "\t\t" + str(x[i]))
        print("\n\n")


def hispanicPC1(fips, data, pc1, mi, ma):
    pc1s = defaultdict(lambda: [])
    counts = defaultdict(lambda: 0)
    avgpop = defaultdict(lambda: []) 
    print("For AA pop. between " + str(mi) + " and " + str(ma) + ":\n")
    for i in range(len(fips)):
        pop = data["AA pop"][i]
        if pop >= mi and pop < ma:      # Within chosen AA pop constraints
            mexpop = data["Mexican pop"][i]
            prpop = data["PR pop"][i]
            x = pc1[i]
            if mexpop >= .25 and mexpop < .35:     name1 = "mex25-35"
            elif mexpop >= .15 and mexpop < .25:   name1 = "mex15-25"
            elif mexpop >= .05 and mexpop < .15:   name1 = "mex5-15"
            elif mexpop >= 0 and mexpop < .05:     name1 = "mex0-5"
            if name1:
                pc1s[name1].append(x)
                counts[name1] += 1
                avgpop[name1].append(pop)
            if prpop >= .25 and prpop < .35:      name2 = "pr25-35"
            elif prpop >= .15 and prpop < .25:    name2 = "pr15-25"
            elif prpop >= .05 and prpop < .15:    name2 = "pr5-15"
            elif prpop >= 0 and prpop < .05:      name2 = "pr0-5"
            if name2:
                pc1s[name2].append(x)
                counts[name2] += 1
                avgpop[name2].append(pop)
    for k,v in pc1s.items():
        print("Hispanic subpopulation:\t"+k)
        print("Average PC1:\t"+str(np.mean(np.array(pc1s[k]))))
        print("Total # tracts:\t"+str(counts[k]))
        print("Average AApop.:\t"+str(np.mean(np.array(avgpop[k])))+"\n")
    print("=====================================================\n")


def main():
    # Parse command line arguments and call all the above functions
    parser = argparse.ArgumentParser()
    parser.add_argument('task', help=u'The task to perform.',
            choices=['PCA-tract','PCA-county','linreg','rural-south','hispanic-PC1'])
    args = parser.parse_args()

    if args.task == "PCA-county":
        ling_data, data, fips = getData('county')
        pc1 = getPCAData(ling_data, verbose=True)
    else:
        ling_data, data, fips = getData('tract')
        if args.task == "PCA-tract":
            pc1 = getPCAData(ling_data, verbose=True)
        elif args.task == "linreg":
            pc1 = getPCAData(ling_data)
            linReg(data, pc1, verbose=True)
        elif args.task == "rural-south":
            pc1 = getPCAData(ling_data)
            ruralSouth(fips, data, ling_data, pc1)
        elif args.task == "hispanic-PC1":
            pc1 = getPCAData(ling_data)
            hispanicPC1(fips, data, pc1, 0, .05)
            hispanicPC1(fips, data, pc1, .05, .15)
            hispanicPC1(fips, data, pc1, .15, .25)
            hispanicPC1(fips, data, pc1, .25, .35)



if __name__ == '__main__':
    main()




