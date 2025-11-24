import logging
import time

import polars as pl
from lxml import etree

import config

# Ensure data directory exists
config.DATA_DIR.mkdir(parents=True, exist_ok=True)

# Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s: %(levelname)s:%(name)s: %(message)s")
file_handler = logging.FileHandler(config.LOG_FILE)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Define the chunk size (number of rows to process at a time)
BATCH_SIZE = config.BATCH_SIZE

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
            data.append("; ".join(result))  # Join xpath with multiple values
        else:
            data.append(None)  # Append None if XPath does not exist

    return data


def data_to_csv(xpath_list, data, output_csv) -> None:
    csv_headers = [xpath[1] for xpath in xpath_list]
    df = pl.DataFrame(data, schema=csv_headers, orient="row")
    df = df.with_columns(pl.col("ecatid").cast(pl.Int64))
    df = df.sort("ecatid", descending=True)
    # df.limit(1000).write_csv(output_csv, include_header=True)
    df.write_csv(output_csv, include_header=True)


def main() -> None:
    try:
        start = time.perf_counter()
        logger.info(f"Start processing {INPUT_FILE}...")

        data_full = []
        df_in = pl.read_csv(
            INPUT_FILE, batch_size=BATCH_SIZE, low_memory=True, encoding="utf-8"
        )
        filtered_df = df_in.filter(pl.col("istemplate") == "n")
        for metadata in filtered_df.iter_rows(named=True):
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
                logger.exception(f"Error processing metadata_id {metadata['id']}: {e}")

        data_to_csv(
            xpath_list=config.XPATH_LIST, data=data_full, output_csv=OUTPUT_FILE
        )

        logger.info(
            f"Completed {filtered_df.shape[0]} rows in {time.perf_counter() - start:0.2f} seconds."
        )
    except Exception as e:
        logger.exception(f"Error processing {INPUT_FILE}: {e}")


if __name__ == "__main__":
    main()
