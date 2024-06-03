# Python xml xpaths to csv.

## xml_to_csv.py:  
Simple Python script that uses lxml library to parse XML file using XPath and write the result to CSV file.  
This script assumes that you have a list of XPath expressions that you want to extract from the XML file.  

## xml_to_csv_bulk.py:  
Simple Python script that uses lxml library to parse bulk XML files using XPath and write the result to CSV file.  
This script assumes that you have a list of XPath expressions that you want to extract from the XML file.  
#### Performance of built in csv on my local machine:    
> Completed 71030 rows in 107.52 seconds.

## xml_to_csv_bulk_pandas.py:  
Simple Python script that uses lxml library to parse bulk XMLs file using XPath and write the result to CSV file.  
This script assumes that you have a list of XPath expressions that you want to extract from the XML file.  
For pandas requirements please refer [requirements-pandas.txt](./requirements-pandas.txt)
#### Performance of pandas on my local machine:    
> Completed 71030 rows in 121.82 seconds.

## Note  
The two bulk options provides same functionality. I have written them separately so we have options for AWS Lambda or AWS ECS Task, etc.   
This is purpose built side project; only maintained as required.  