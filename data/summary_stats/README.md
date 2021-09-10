Files are zipped in the form year.tar.gz<br>
On unzipping them, the folder contains files in the format <b>green|yellow|fhv|fhvhv_Year_Month</b><br>
For each trip details there are 2 files with the suffix 
<ul>
  <li>describe - details of dataframe.describe()</li>
	<li>isna - details of dataframe.isnull().sum()</li>
</ul><br>
The following code can be used to read the data

``` python
import pandas as pd
data = pd.read_csv('filename.csv.describe')
print(data)
```
