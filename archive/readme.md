# Python xml xpaths to csv.

## xml_to_csv.py:  
Simple Python script that uses lxml library to parse XML file using XPath and converts it to csv format.  
This script assumes that you have a list of XPath expressions that you want to extract from the XML file.  

## xml_to_csv_bulk.py:  
Simple Python script that uses lxml library to parse bulk XML files using XPath and converts it to csv format.  
This script assumes that you have a list of XPath expressions that you want to extract from the XML file.  
#### Docker 
The Dockerfile is named [Dockerfile.bulk](./Dockerfile.bulk)  
Use the following command to test it out:   
docker build: `docker build --platform linux/amd64 -f Dockerfile.bulk -t xml-to-csv-bulk:native .`  
docker run: `docker run --platform linux/amd64 -v "Your/Local/Path":/app/downloads xml-to-csv-bulk:native`  

## xml_to_csv_bulk_pandas.py:  
Simple Python script that uses lxml and pandas libraries to parse bulk XML files using XPath and converts it to csv format.  
This script assumes that you have a list of XPath expressions that you want to extract from the XML file.  
For pandas requirements please refer [requirements-pandas.txt](./requirements-pandas.txt)
#### Docker 
The Dockerfile is named [Dockerfile.bulk.pandas](./Dockerfile.bulk.pandas)  
Use the following command to test it out:   
docker build: `docker build --platform linux/amd64 -f Dockerfile.bulk.pandas -t xml-to-csv-bulk:pandas .`  
docker run: `docker run --platform linux/amd64 -v "Your/Local/Path":/app/downloads xml-to-csv-bulk:pandas` 

## Note  
The two bulk options provides same functionality. I have written them separately using built in csv and pandas, so we have options for AWS Lambda or AWS ECS Task, etc.   
This is purpose built side project; only maintained as required.  