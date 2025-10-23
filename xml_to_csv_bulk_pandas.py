import logging
import time

import pandas as pd
from lxml import etree
import config

# Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s: %(levelname)s:%(name)s: %(message)s")
file_handler = logging.FileHandler("./downloads/xml_to_csv_bulk_pandas.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Define the chunk size (number of rows to process at a time)
CHUNKSIZE = 10000

INPUT_FILE = config.INPUT_FILE
OUTPUT_FILE = config.OUTPUT_FILE


def xml_to_data(input_xml, namespaces, xpath_list) -> list:
    """
    Convert an XML string into a list of strings or None values using XPath expressions.

    Args:
        input_xml (str): The XML string to be parsed.
        namespaces (dict): A dictionary mapping namespace prefixes to URIs.
        xpath_list (list): A list of tuples, where each tuple contains an XPath expression and a field name.

    Returns:
        list: A list of strings or None values, where each string represents the value(s) extracted from the XML document using the provided XPath expressions.
    """
    xml_tree = etree.fromstring(input_xml)
    data = []
    for xpath, field in xpath_list:
        result = xml_tree.xpath(xpath, namespaces=namespaces)
        if result:
            data.append(", ".join(result))  # Join xpath with multiple values
        else:
            data.append(None)  # Append None if XPath does not exist

    return data


def data_to_csv(xpath_list, data, output_csv) -> None:
    csv_headers = [xpath[1] for xpath in xpath_list]
    df = pd.DataFrame(data, columns=csv_headers)
    df.to_csv(output_csv, index=False, encoding="utf-8")


def main() -> None:
    try:
        start = time.perf_counter()
        logger.info(f"Start processing {INPUT_FILE}...")

        data_full = []
        for chunk in pd.read_csv(INPUT_FILE, chunksize=CHUNKSIZE, low_memory=False):
            for index, metadata in chunk.iterrows():
                logger.info(f"Processing metadata_id: {metadata["id"]}")
                try:
                    data = xml_to_data(
                        input_xml=metadata["data"],
                        namespaces=config.NAMESPACES,
                        xpath_list=config.XPATH_LIST,
                    )
                    data_full.append(data)
                    logger.info(f"Completed processing metadata_id: {metadata["id"]}")
                except Exception as e:
                    logger.exception(f"Error processing metadata_id {metadata["id"]}")

        data_to_csv(
            xpath_list=config.XPATH_LIST, data=data_full, output_csv=OUTPUT_FILE
        )

        logger.info(
            f"Completed {index+1} rows in {time.perf_counter() - start:0.2f} seconds."
        )
    except Exception as e:
        logger.exception(f"Error processing {INPUT_FILE}: {e}")


if __name__ == "__main__":
    main()
