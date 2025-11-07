# Python tool  
**Tool to convert XML to CSV** 

## Features

- Processes input XML files in chunks  
- Extracts specific data from each XML file using XPath expressions  
- Writes extracted data to a single CSV file  

## Usage

### Configure input parameters in the code:
- `INPUT_FILE`: Path to the input XML dump flat-file  
- `OUTPUT_FILE`: Path to the output CSV file  
- `NAMESPACES`: Dictionary mapping namespace prefixes to URIs  
- `XPATH_LIST`: List of tuples containing XPath expressions and field names  

### Running the Script
Run the script with UV: `uv run main.py` or Python: `python main.py`  

### Docker 
Use the following command to test it out:   
docker build: `docker build --pull --platform linux/amd64 -t xml-to-csv .`  
docker run: `docker run --platform linux/amd64 -v "Your/Local/MountPath":/app/downloads xml-to-csv`  
example: `docker run --platform linux/amd64 -v "/Users/twangchen/Documents/GitHub/xml_to_csv/downloads":/app/downloads xml-to-csv`  

## Dependencies
- Python 3.x 
- pandas
- lxml 


## Notes
Only maintained as required.  