import sys
import os
from collections import defaultdict
from urllib.request import urlopen
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import statistics
import numpy as np
import csv
import geopandas as gpd

# Creates tsv file with # detected features + demographic info per region
# Input is tweetfiles after being scored by feature detectors + demographic data
# Example commandline: python3 getRegionData.py tract 

granularity = sys.argv[1]

if granularity == 'state': state = 1
elif granularity == 'county': state = 2
elif granularity == 'tract': state = 3

features_list = [
        "zero-poss","ov-poss","zero-copula","ov-copula","gone",
        "be-construction","stress-BIN","resultant-done","be-done",
        "BIN-done","steady","finna","double-modal","neg-conc",
        "single-neg","nai","n-inv-neg-concord","aint","zero-3sg-pres-s",
        "narrative-s","is-was-gen","zero-pl-s","double-object","wh-qu" ]
thresholds = [0.95,0.5,0.85,0.35,0.1,0.7,0.999,0.45,0.8,0.999,0.7,
        0.95,0.999,0.99,0.3,0.999,0.999,0.5,0.95,0.75,0.999,0.9,0.999,0.85 ]
states = {'02':'AK', '01':'AL', '05':'AR', '04':'AZ', '06':'CA', '08':'CO',
        '09':'CT', '10':'DE', '11':'DC', '12':'FL', '13':'GA', '15':'HI', '19':'IA',
        '16':'ID', '17':'IL', '18':'IN', '20':'KS', '21':'KY', '22':'LA', '25':'MA',
        '24':'MD', '23':'ME', '26':'MI', '27':'MN', '29':'MO', '28':'MS', '30':'MT',
        '37':'NC', '38':'ND', '31':'NE', '33':'NH', '34':'NJ', '35':'NM', '32':'NV',
        '36':'NY', '39':'OH', '40':'OK', '41':'OR', '42':'PA', '72':'PR', '44':'RI',
        '45':'SC', '46':'SD', '47':'TN', '48':'TX', '49':'UT', '51':'VA', '50':'VT',
        '53':'WA', '55':'WI', '54':'WV', '56':'WY' }

# Get feature counts per region
geoidcounts = defaultdict(lambda: defaultdict(lambda: 0)) # per-region counts per feature
geoidtotal = defaultdict(lambda: 0.0) # total tweets per region
with os.scandir("../scores/") as d: 
    for test_file in d:
        twid2geoid = dict()     # map twitter id to blockgroup id
        with open("/work/pi_brenocon_umass_edu/dataset/geoids/geoid"+test_file.name[-10:]) as r:
            for line in r:
                ls = line.split("\t")
                geoid = ls[1][-12:]     # geoid is blockgroup id
                twid2geoid[ls[0].strip()] = geoid 

        with open(test_file) as r:
            for line in r:
                lineSplit = line.split("\t")
                if lineSplit[0] in twid2geoid:
                    geoid = twid2geoid[lineSplit[0]]    # geoid is blockgroup id
                    if geoid[:2] == "72": 
                        continue    # not including Puerto Rico in our data
                    if state == 1: gi = states[geoid[:2]]    # gi is state
                    elif state == 2: gi = geoid[:5]            # gi is fips/county id
                    else:       gi = geoid[:11]         # gi is tract id
                    geoidtotal[gi] += 1
                for feat_i in range(len(features_list)):
                    if feat_i in [6,9,12,16,19,21]:   
                        continue    # not including these due to noisy detectors
                    if float(lineSplit[feat_i+2]) >= thresholds[feat_i]:
                        geoidcounts[features_list[feat_i]][gi] += 1

# Get demographic data
if state == 3:      
    # Geography
    metrics = defaultdict(lambda: [])
    first = True
    with open("../data/2015_Gaz_tracts_national.tsv") as f:
        for line in f:
            if first:
                first = False
                continue
            ls = line.split("\t")
            metrics[ls[1]].extend([ls[6].strip(), ls[7].strip()]) # Assign to GEOID/FIPS
    first = True
    f = csv.reader(open("../data/ruca2010revised.csv", encoding='mac_roman'))
    for ls in f:
        if first:
            first = False
            continue
        if ls[4].strip() == '99': continue
        metrics[ls[3]].extend([ls[4].strip()])
    # Get info from 2011-2015 ACS 5-year tract estimates
    fn = f"../data/ACS_2015_5YR_TRACT.gdb.zip"
    # Age
    df = gpd.read_file(fn, driver="OpenFileGDB", layer="X01_AGE_AND_SEX")
    for i in range(len(df["GEOID"])):
        metrics[df["GEOID"][i][-11:]].append(str(df["B01002e1"][i]))  
    # Race
    df = gpd.read_file(fn, driver="OpenFileGDB", layer="X02_RACE")
    for i in range(len(df["GEOID"])):
        if df["B02001e1"][i] == 0: continue 
        else:   
            metrics[df["GEOID"][i][-11:]].extend([
                str(df["B02001e3"][i]/df["B02001e1"][i]),
                str(df["B02001e2"][i]/df["B02001e1"][i])])
    df = gpd.read_file(fn, driver="OpenFileGDB", layer="X03_HISPANIC_OR_LATINO_ORIGIN")
    for i in range(len(df["GEOID"])):
        if df["B03001e1"][i] == 0: continue
        else: 
            metrics[df["GEOID"][i][-11:]].append(
                str(df["B03001e3"][i]/df["B03001e1"][i]))
            metrics[df["GEOID"][i][-11:]].extend([
                str(df["B03001e4"][i]/df["B03001e1"][i]),
                str(df["B03001e5"][i]/df["B03001e1"][i]) ])
    # Socioeconomic status
    df = gpd.read_file(fn, driver="OpenFileGDB", layer="X19_INCOME")
    for i in range(len(df["GEOID"])):
        metrics[df["GEOID"][i][-11:]].append(str(df["B19013e1"][i]))
    # Get info from 2011-2015 ACS 5-year county estimates
    fn = f"../data/ACS_2015_5YR_COUNTY.gdb.zip"
    # Race
    df = gpd.read_file(fn, driver="OpenFileGDB", layer="X02_RACE")
    counties = defaultdict(lambda: [])       # dict with county to data mappings
    for i in range(len(df["GEOID"])):
        counties[df["GEOID"][i][-5:]] = [
            str(df["B02001e3"][i]/df["B02001e1"][i]),
            str(df["B02001e2"][i]/df["B02001e1"][i])]
    df = gpd.read_file(fn, driver="OpenFileGDB", layer="X03_HISPANIC_OR_LATINO_ORIGIN")
    for i in range(len(df["GEOID"])):
        counties[df["GEOID"][i][-5:]].append(str(df["B03001e3"][i]/df["B03001e1"][i]))
    # Get info from historical county data
    hist_data = pd.read_csv("../data/abs-jop-countydata.csv")
    for i in range(len(hist_data["fips"])):
        tmp = str(hist_data["fips"][i])
        if len(tmp) == 4:   tmp = "0" + tmp
        counties[tmp].append(str(hist_data["pslave1860"][i]))
    # Add county-level data to corresponding tracts
    tracts = list(metrics.keys())
    for i in range(len(tracts)):
        if len(counties[tracts[i][:5]]) == 3:
            counties[tracts[i][:5]].append('0') # for counties missing historical data, just put 0
        metrics[tracts[i]].extend(counties[tracts[i][:5]])


# Create county-level choropleth map w/feature counts 
with urlopen("https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json") as response:
    counties = json.load(response)

# Exclude sparse counties 
toolow = 250    # total tweets < 250  --  ~= 3% of counties; 250 ~= 14% of tracts

# Print arrays of relative feature frequencies per region
out_f = granularity+".tsv"
full_features = [
        "zero poss","overt poss","zero copula","overt copula","gone",
        "habitual be","resultant done","be done","steady","finna",
        "neg concord","single neg","neg auxiliary inversion","ain't",
        "zero 3rd sing pres -s","is/was generalization","double object","wh-question" ]
with open(out_f,'w') as f:
    if state == 1:
        f.write("region\t"+"\t".join(full_features)+"\n")
        for k,v in geoidtotal.items():
            toprint = [k]
            for i in range(len(features_list)):
                if i in [6,9,12,16,19,21]:   continue
                c = geoidcounts[features_list[i]][k]
                if c > 0:
                    c = float(c) / float(v) 
                toprint.append(str(c))
            f.write("\t".join(toprint)+"\n")
    elif state == 2:
        f.write("region\t"+"\t".join(full_features)+"\n")
        for each in counties["features"]:
            if geoidtotal[each["id"]] < toolow: continue
            toprint = [each["id"]]
            for i in range(len(features_list)):
                if i in [6,9,12,16,19,21]:   continue
                c = geoidcounts[features_list[i]][each["id"]]
                if c > 0:
                    c = float(c) / float(geoidtotal[each["id"]])    
                toprint.append(str(c))
            f.write("\t".join(toprint)+"\n")
    elif state == 3:
        soc = ["latitude","longitude","ruca","median age","AA pop",
            "white pop","Hispanic pop","Mexican pop","PR pop",
            "median household income","county AA pop","county white pop", 
            "county Hispanic pop","county historical AA pop"]
        f.write("region\t"+"\t".join(full_features)+"\t"+"\t".join(soc)+"\n")
        for each in metrics.keys():
            if geoidtotal[each] < toolow: continue
            if len(metrics[each]) < 14: continue  # only include tracts w/no missing data
            toprint = [each]
            for i in range(len(features_list)):
                if i in [6,9,12,16,19,21]:   continue
                c = geoidcounts[features_list[i]][each]
                if c > 0:
                    c = float(c) / float(geoidtotal[each])    
                toprint.append(str(c))
            toprint.extend(metrics[each])   
            f.write("\t".join(toprint)+"\n")





