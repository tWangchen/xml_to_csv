import csv
import logging
import sys
import time

from lxml import etree

# Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s: %(levelname)s:%(name)s: %(message)s")
file_handler = logging.FileHandler("./downloads/xml_to_csv_bulk.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

INPUT_FILE = f"./downloads/metadata-dump-input.csv"
OUTPUT_FILE = f"./downloads/metadata-converted-output.csv"

NAMESPACES = {
    "cit": "http://standards.iso.org/iso/19115/-3/cit/1.0",
    "gco": "http://standards.iso.org/iso/19115/-3/gco/1.0",
    "gex": "http://standards.iso.org/iso/19115/-3/gex/1.0",
    "mcc": "http://standards.iso.org/iso/19115/-3/mcc/1.0",
    "mco": "http://standards.iso.org/iso/19115/-3/mco/1.0",
    "mdb": "http://standards.iso.org/iso/19115/-3/mdb/1.0",
    "mrd": "http://standards.iso.org/iso/19115/-3/mrd/1.0",
    "mri": "http://standards.iso.org/iso/19115/-3/mri/1.0",
    "mrl": "http://standards.iso.org/iso/19115/-3/mrl/1.0",
    "mmi": "http://standards.iso.org/iso/19115/-3/mmi/1.0",
    "srv": "http://standards.iso.org/iso/19115/-3/srv/2.0",
}

XPATH_LIST = [
    (
        "//mdb:MD_Metadata/mdb:alternativeMetadataReference/cit:CI_Citation/cit:identifier/mcc:MD_Identifier/mcc:code/gco:CharacterString/text()",
        "ecatid",
    ),
    (
        "//mdb:MD_Metadata/mdb:identificationInfo/*/mri:citation/cit:CI_Citation/cit:title/gco:CharacterString/text()",
        "title",
    ),
    (
        "//mdb:MD_Metadata/mdb:metadataScope[1]/mdb:MD_MetadataScope[1]/mdb:resourceScope[1]/mcc:MD_ScopeCode[1]/@codeListValue",
        "metadatascopecode",
    ),
    (
        "/mdb:MD_Metadata/mdb:identificationInfo[1]/mri:MD_DataIdentification[1]/mri:resourceFormat[1]/mrd:MD_Format[1]/mrd:formatSpecificationCitation[1]/cit:CI_Citation[1]/cit:onlineResource[1]/cit:CI_OnlineResource[1]/cit:linkage[1]/gco:CharacterString[1]/text()",
        "datastoragelink",
    ),
    (
        "//mdb:MD_Metadata/mdb:identificationInfo[1]/*/mri:descriptiveKeywords/mri:MD_Keywords[1]/mri:keyword[1]/gco:CharacterString[1]/text()",
        "keywords",
    ),
    (
        "//mdb:MD_Metadata/mdb:distributionInfo[1]/mrd:MD_Distribution[1]/mrd:distributor[1]/mrd:MD_Distributor[1]/mrd:distributorTransferOptions/mrd:MD_DigitalTransferOptions[1]/mrd:onLine[1]/cit:CI_OnlineResource[1]/cit:linkage[1]/gco:CharacterString[1]/text()",
        "distributionlink",
    ),
    (
        "/mdb:MD_Metadata/mdb:metadataScope[1]/mdb:MD_MetadataScope[1]/mdb:name[1]/gco:CharacterString[1]/text()",
        "scopecodename",
    ),
    (
        "//mdb:MD_Metadata/mdb:identificationInfo[1]/mri:MD_DataIdentification[1]/mri:citation[1]/cit:CI_Citation[1]/cit:citedResponsibleParty/cit:CI_Responsibility[1]/cit:role[1]/cit:CI_RoleCode[1]/@codeListValue",
        "rolecodes_citation_role",
    ),
    (
        "//mdb:MD_Metadata/mdb:identificationInfo[1]/mri:MD_DataIdentification[1]/mri:citation[1]/cit:CI_Citation[1]/cit:citedResponsibleParty/cit:CI_Responsibility[1]/cit:party[1]/cit:CI_Individual[1]/cit:name[1]/gco:CharacterString[1]/text()",
        "rolecodes_citation_name",
    ),
    (
        "//mdb:MD_Metadata/mdb:identificationInfo[1]/mri:MD_DataIdentification[1]/mri:pointOfContact[2]/cit:CI_Responsibility[1]/cit:party[1]/cit:CI_Individual[1]/cit:name[1]/gco:CharacterString[1]/text()",
        "pointofcontact_name",
    ),
    (
        "//mdb:MD_Metadata/mdb:identificationInfo[1]/*/mri:pointOfContact/cit:CI_Responsibility[1]/cit:role[1]/cit:CI_RoleCode[1]/@codeListValue",
        "pointofcontact_role",
    ),
    (
        "//mdb:MD_Metadata/mdb:identificationInfo[1]/*/mri:pointOfContact[3]/cit:CI_Responsibility[1]/cit:party[1]/cit:CI_Individual[1]/cit:name[1]/gco:CharacterString[1]/text()",
        "pointofcontact_value",
    ),
    (
        "//mdb:MD_Metadata/mdb:contact/cit:CI_Responsibility[1]/cit:role[1]/cit:CI_RoleCode[1]/@codeListValue",
        "metadata_contact_role",
    ),
    (
        "//mdb:MD_Metadata/mdb:contact/cit:CI_Responsibility[1]/cit:party[1]/cit:CI_Individual[1]/cit:name[1]/gco:CharacterString[1]/text()",
        "metadata_contact_value",
    ),
    (
        "//mdb:MD_Metadata/mdb:identificationInfo[1]/mri:MD_DataIdentification[1]/mri:citation[1]/cit:CI_Citation[1]/cit:identifier[1]/mcc:MD_Identifier[1]/mcc:code[1]/gco:CharacterString[1]/text()",
        "pid",
    ),
    (
        "//mdb:MD_Metadata/mdb:identificationInfo[1]/mri:MD_DataIdentification[1]/mri:pointOfContact[3]/cit:CI_Responsibility[1]/cit:role[1]/cit:CI_RoleCode[1]/@codeListValue",
        "resource_provider",
    ),
    (
        "//mdb:MD_Metadata/mdb:identificationInfo[1]/mri:MD_DataIdentification[1]/mri:citation[1]/cit:CI_Citation[1]/cit:identifier[2]/mcc:MD_Identifier[1]/mcc:code[1]/gco:CharacterString[1]/text()",
        "doi",
    ),
    # ("//mdb:MD_Metadata/mdb:identificationInfo[1]/mri:MD_DataIdentification[1]/mri:abstract[1]/gco:CharacterString[1]/text()", "abstract"),
    (
        "//mdb:MD_Metadata/mdb:identificationInfo[1]/mri:MD_DataIdentification[1]/mri:resourceConstraints[1]/mco:MD_LegalConstraints[1]/mco:otherConstraints[1]/gco:CharacterString[1]/text()",
        "copyright_statement",
    ),
    (
        "//mdb:MD_Metadata/mdb:identificationInfo[1]/mri:MD_DataIdentification[1]/mri:resourceConstraints[1]/mco:MD_LegalConstraints[1]/mco:useConstraints[1]/mco:MD_RestrictionCode[1]/@codeListValue",
        "copyright_use_constraints",
    ),
    (
        "//mdb:MD_Metadata/mdb:identificationInfo[1]/mri:MD_DataIdentification[1]/mri:status[1]/mcc:MD_ProgressCode[1]/@codeListValue",
        "purpose",
    ),
    (
        "//mdb:MD_Metadata/mdb:identificationInfo[1]/mri:MD_DataIdentification[1]/mri:status[1]/mcc:MD_ProgressCode[1]/@codeListValue",
        "status",
    ),
    # ("//mdb:MD_Metadata/mdb:resourceLineage[1]/mrl:LI_Lineage[1]/mrl:statement[1]/gco:CharacterString[1]/text()", "lineage"),
    (
        "//mdb:MD_Metadata/mdb:identificationInfo[1]/mri:MD_DataIdentification[1]/mri:extent[1]/gex:EX_Extent[1]/gex:geographicElement[1]/gex:EX_GeographicBoundingBox[1]/gex:westBoundLongitude[1]/gco:Decimal[1]/text()",
        "geographicalextent_west",
    ),
    (
        "//mdb:MD_Metadata/mdb:identificationInfo[1]/mri:MD_DataIdentification[1]/mri:extent[1]/gex:EX_Extent[1]/gex:geographicElement[1]/gex:EX_GeographicBoundingBox[1]/gex:eastBoundLongitude[1]/gco:Decimal[1]/text()",
        "geographicalextent_east",
    ),
    (
        "//mdb:MD_Metadata/mdb:identificationInfo[1]/mri:MD_DataIdentification[1]/mri:extent[1]/gex:EX_Extent[1]/gex:geographicElement[1]/gex:EX_GeographicBoundingBox[1]/gex:southBoundLatitude[1]/gco:Decimal[1]/text()",
        "geographicalextent_south",
    ),
    (
        "//mdb:MD_Metadata/mdb:identificationInfo[1]/mri:MD_DataIdentification[1]/mri:extent[1]/gex:EX_Extent[1]/gex:geographicElement[1]/gex:EX_GeographicBoundingBox[1]/gex:northBoundLatitude[1]/gco:Decimal[1]/text()",
        "geographicalextent_north",
    ),
    (
        "//mdb:MD_Metadata/mdb:identificationInfo[1]/mri:MD_DataIdentification[1]/mri:resourceConstraints[1]/mco:MD_LegalConstraints[1]/mco:reference[1]/cit:CI_Citation[1]/cit:title[1]/gco:CharacterString[1]/text()",
        "license_title",
    ),
    (
        "//mdb:MD_Metadata/mdb:identificationInfo[1]/mri:MD_DataIdentification[1]/mri:resourceConstraints[1]/mco:MD_LegalConstraints[1]/mco:reference[1]/cit:CI_Citation[1]/cit:alternateTitle[1]/gco:CharacterString[1]/text()",
        "license_alternatetitle",
    ),
    (
        "//mdb:MD_Metadata/mdb:identificationInfo[1]/mri:MD_DataIdentification[1]/mri:resourceConstraints[1]/mco:MD_LegalConstraints[1]/mco:reference[1]/cit:CI_Citation[1]/cit:edition[1]/gco:CharacterString[1]/text()",
        "license_edition",
    ),
    (
        "//mdb:MD_Metadata/mdb:identificationInfo[1]/mri:MD_DataIdentification[1]/mri:resourceConstraints[1]/mco:MD_LegalConstraints[1]/mco:reference[1]/cit:CI_Citation[1]/cit:onlineResource[1]/cit:CI_OnlineResource[1]/cit:linkage[1]/gco:CharacterString[1]/text()",
        "license_onlineurl",
    ),
    (
        "//mdb:MD_Metadata/mdb:distributionInfo[1]/mrd:MD_Distribution[1]/mrd:distributor[1]/mrd:MD_Distributor[1]/mrd:distributorTransferOptions/mrd:MD_DigitalTransferOptions[1]/mrd:onLine[1]/cit:CI_OnlineResource[1]/cit:name[1]/gco:CharacterString[1]/text()",
        "distribution_name",
    ),
    (
        "//mdb:MD_Metadata/mdb:distributionInfo[1]/mrd:MD_Distribution[1]/mrd:distributor[1]/mrd:MD_Distributor[1]/mrd:distributorTransferOptions/mrd:MD_DigitalTransferOptions[1]/mrd:onLine[1]/cit:CI_OnlineResource[1]/cit:linkage[1]/gco:CharacterString[1]/text()",
        "distribution_url",
    ),
    (
        "//mdb:MD_Metadata/mdb:distributionInfo[1]/mrd:MD_Distribution[1]/mrd:distributor[1]/mrd:MD_Distributor[1]/mrd:distributorTransferOptions/mrd:MD_DigitalTransferOptions[1]/mrd:distributionFormat[1]/mrd:MD_Format[1]/mrd:formatSpecificationCitation[1]/cit:CI_Citation[1]/cit:title[1]/gco:CharacterString[1]/text()",
        "distribution_format",
    ),
    (
        "//mdb:MD_Metadata/mdb:identificationInfo[1]/*/mri:associatedResource/mri:MD_AssociatedResource[1]/mri:associationType[1]/mri:DS_AssociationTypeCode[1]/@codeListValue",
        "associatedresources_type",
    ),
    (
        "//mdb:MD_Metadata/mdb:identificationInfo[1]/*/mri:associatedResource/mri:MD_AssociatedResource[1]/mri:metadataReference[1]/cit:CI_Citation[1]/cit:identifier[1]/mcc:MD_Identifier[1]/mcc:code[1]/gco:CharacterString[1]/text()",
        "associatedresources_ecatid",
    ),
    (
        "//mdb:MD_Metadata/mdb:identificationInfo[1]/*/mri:associatedResource/mri:MD_AssociatedResource[1]/mri:metadataReference[1]/cit:CI_Citation[1]/cit:title[1]/gco:CharacterString[1]/text()",
        "associatedresources_ecat_title",
    ),
    (
        "//mdb:MD_Metadata/mdb:identificationInfo[1]/*/mri:resourceMaintenance[1]/mmi:MD_MaintenanceInformation[1]/mmi:maintenanceAndUpdateFrequency[1]/mmi:MD_MaintenanceFrequencyCode[1]/@codeListValue",
        "maintenance_frequency",
    ),
    (
        "//mdb:MD_Metadata/mdb:identificationInfo[1]/mri:MD_DataIdentification[1]/mri:citation[1]/cit:CI_Citation[1]/cit:date[2]/cit:CI_Date[1]/cit:date[1]/gco:DateTime[1]/text()",
        "publication_date",
    ),
    (
        "//mdb:MD_Metadata/mdb:identificationInfo[1]/mri:MD_DataIdentification[1]/mri:citation[1]/cit:CI_Citation[1]/cit:date[2]/cit:CI_Date[1]/cit:dateType[1]/cit:CI_DateTypeCode[1]/@codeListValue",
        "publication_typecode",
    ),
    (
        "//mdb:MD_Metadata/mdb:identificationInfo[1]/mri:MD_DataIdentification[1]/mri:citation[1]/cit:CI_Citation[1]/cit:date[1]/cit:CI_Date[1]/cit:date[1]/gco:DateTime[1]/text()",
        "creation_date",
    ),
    (
        "//mdb:MD_Metadata/mdb:identificationInfo[1]/mri:MD_DataIdentification[1]/mri:citation[1]/cit:CI_Citation[1]/cit:date[1]/cit:CI_Date[1]/cit:dateType[1]/cit:CI_DateTypeCode[1]/@codeListValue",
        "creation_typecode",
    ),
    (
        "//mdb:MD_Metadata/mdb:distributionInfo[1]/mrd:MD_Distribution[1]/mrd:distributor[1]/mrd:MD_Distributor[1]/mrd:distributorTransferOptions[2]/mrd:MD_DigitalTransferOptions[1]/mrd:onLine[1]/cit:CI_OnlineResource[1]/cit:description[1]/gco:CharacterString[1]/text()",
        "label_description",
    ),
]


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
                        namespaces=NAMESPACES,
                        xpath_list=XPATH_LIST,
                    )
                    data_full.append(data)
                    logger.info(f"Completed processing metadata_id: {metadata['id']}")
                except Exception as e:
                    logger.exception(f"Error processing metadata_id {metadata['id']}")

        data_to_csv(xpath_list=XPATH_LIST, data=data_full, output_csv=OUTPUT_FILE)

        logger.info(
            f"Completed {index+1} rows in {time.perf_counter() - start:0.2f} seconds."
        )
    except Exception as e:
        logger.exception(f"Error processing {INPUT_FILE}: {e}")


if __name__ == "__main__":
    main()
