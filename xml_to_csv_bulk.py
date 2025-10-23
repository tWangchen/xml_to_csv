import csv
import logging
import sys
import time

from lxml import etree
import config

# Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s: %(levelname)s:%(name)s: %(message)s")
file_handler = logging.FileHandler("./downloads/xml_to_csv_bulk.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

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
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(csv_headers)
        writer.writerows(data)


def main() -> None:
    try:
        start = time.perf_counter()
        logger.info(f"Start processing {INPUT_FILE}...")

        # Set the field size limit to the maximum integer value
        # csv.field_size_limit(sys.maxsize)
        # Set the field size limit to approximately 1MB
        csv.field_size_limit(1048576)

        data_full = []
        with open(INPUT_FILE, "r") as f:
            reader = csv.DictReader(f)
            for index, metadata in enumerate(reader):
                logger.info(f"Processing metadata_id: {metadata['id']}")
                try:
                    data = xml_to_data(
                        input_xml=metadata["data"],
                        namespaces=config.NAMESPACES,
                        xpath_list=config.XPATH_LIST,
                    )
                    data_full.append(data)
                    logger.info(f"Completed processing metadata_id: {metadata['id']}")
                except Exception as e:
                    logger.exception(f"Error processing metadata_id {metadata['id']}")

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
