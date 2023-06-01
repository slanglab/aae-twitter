## Dataset contents

### aae-twitter/county.tsv
- 3050 items
- Each item represents a U.S. county
- For each item, there is a county ID (column denoted as 'region') and continuous variables representing the relative incidences of 18 linguistic features. Example utterances and descriptions for each linguistic feature can be found in the paper. The following are mappings of column names to the linguistic features:
	1. zero poss: Zero possessive -*'s*
	1. overt poss: Overt possessive -*'s*
	1. zero copula: Zero copula
	1. overt copula: Overt copula
	1. gone: Future *gone*
	1. habitual be: Habitual *be*
	1. resultant done: Resultant *done*
	1. be done: *be done*
	1. steady: *steady*
	1. finna: *finna*
	1. neg concord: Negative concord
	1. single neg: Single negative
	1. neg auxiliary inversion: Negative axuiliary inversion
	1. ain't: Preverbal negator *ain't*
	1. zero 3rd sing pres -s: Zero 3rd p sg present tense -*s*
	1. is/was generalization: *is/was*-generalization
	1. double object: Double-object construction
	1. wh-question: *Wh*-question

### aae-twitter/tract.zip
- Compressed tsv file
- 69865 items
- Each item represents a U.S. Census tract
- For each item, there is a tract ID (column denoted as 'region') and continuous variables representing the relative incidences of the same 18 linguistic features as aae-twitter/county.tsv
- For each item, there are also columns representing demographic data for each tract. More details on the data and where it was sourced from can be found in the Methods section of the paper. The following are mappings of column names to the demographic data:
	1. latitude: Latitude
	1. longitude: Longitude
	1. ruca: Rural-Urban Commuting Area
	1. median age: Median age
	1. AA pop: Relative African American population (tract-level)
	1. white pop: Relative white population (tract-level)
	1. Hispanic pop: Relative Hispanic and/or Latino population (tract-level)
	1. Mexican pop: Relative Mexican population (tract-level)
	1. PR pop: Relative Puerto Rican population (tract-level)
	1. median household income: Median household income
	1. county AA pop: Relative African American population (county-level)
	1. county white pop: Relative white population (county-level)
	1. county Hispanic pop: Relative Hispanic and/or Latino population (county-level)
	1. county historical AA pop: Relative African population in 1860 (county-level)
