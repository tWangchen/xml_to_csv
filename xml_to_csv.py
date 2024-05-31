import csv
import logging

from lxml import etree

# Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s: %(levelname)s:%(name)s: %(message)s")
file_handler = logging.FileHandler("xml_to_csv.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

INPUT_XML = "ecat_145182.input.xml"
OUTPUT_CSV = "ecat_145182.output.csv"

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
    "//mdb:MD_Metadata/mdb:alternativeMetadataReference/cit:CI_Citation/cit:identifier/mcc:MD_Identifier/mcc:code/gco:CharacterString/text()",
    "//mdb:MD_Metadata/mdb:identificationInfo/*/mri:citation/cit:CI_Citation/cit:title/gco:CharacterString/text()",
    "//mdb:MD_Metadata/mdb:metadataScope[1]/mdb:MD_MetadataScope[1]/mdb:resourceScope[1]/mcc:MD_ScopeCode[1]/@codeListValue",
    "/mdb:MD_Metadata/mdb:identificationInfo[1]/mri:MD_DataIdentification[1]/mri:resourceFormat[1]/mrd:MD_Format[1]/mrd:formatSpecificationCitation[1]/cit:CI_Citation[1]/cit:onlineResource[1]/cit:CI_OnlineResource[1]/cit:linkage[1]/gco:CharacterString[1]/text()",
    "//mdb:MD_Metadata/mdb:identificationInfo[1]/*/mri:descriptiveKeywords/mri:MD_Keywords[1]/mri:keyword[1]/gco:CharacterString[1]/text()",
    "//mdb:MD_Metadata/mdb:distributionInfo[1]/mrd:MD_Distribution[1]/mrd:distributor[1]/mrd:MD_Distributor[1]/mrd:distributorTransferOptions/mrd:MD_DigitalTransferOptions[1]/mrd:onLine[1]/cit:CI_OnlineResource[1]/cit:linkage[1]/gco:CharacterString[1]/text()",
    "/mdb:MD_Metadata/mdb:metadataScope[1]/mdb:MD_MetadataScope[1]/mdb:name[1]/gco:CharacterString[1]/text()",
    "//mdb:MD_Metadata/mdb:identificationInfo[1]/mri:MD_DataIdentification[1]/mri:citation[1]/cit:CI_Citation[1]/cit:citedResponsibleParty/cit:CI_Responsibility[1]/cit:role[1]/cit:CI_RoleCode[1]/@codeListValue",
    "//mdb:MD_Metadata/mdb:identificationInfo[1]/mri:MD_DataIdentification[1]/mri:citation[1]/cit:CI_Citation[1]/cit:citedResponsibleParty/cit:CI_Responsibility[1]/cit:party[1]/cit:CI_Individual[1]/cit:name[1]/gco:CharacterString[1]/text()",
    "//mdb:MD_Metadata/mdb:identificationInfo[1]/mri:MD_DataIdentification[1]/mri:pointOfContact[2]/cit:CI_Responsibility[1]/cit:party[1]/cit:CI_Individual[1]/cit:name[1]/gco:CharacterString[1]/text()",
    "//mdb:MD_Metadata/mdb:identificationInfo[1]/*/mri:pointOfContact/cit:CI_Responsibility[1]/cit:role[1]/cit:CI_RoleCode[1]/@codeListValue",
    "//mdb:MD_Metadata/mdb:identificationInfo[1]/*/mri:pointOfContact[3]/cit:CI_Responsibility[1]/cit:party[1]/cit:CI_Individual[1]/cit:name[1]/gco:CharacterString[1]/text()",
    "//mdb:MD_Metadata/mdb:contact/cit:CI_Responsibility[1]/cit:role[1]/cit:CI_RoleCode[1]/@codeListValue",
    "//mdb:MD_Metadata/mdb:contact/cit:CI_Responsibility[1]/cit:party[1]/cit:CI_Individual[1]/cit:name[1]/gco:CharacterString[1]/text()",
    "//mdb:MD_Metadata/mdb:identificationInfo[1]/mri:MD_DataIdentification[1]/mri:citation[1]/cit:CI_Citation[1]/cit:identifier[1]/mcc:MD_Identifier[1]/mcc:code[1]/gco:CharacterString[1]/text()",
    "//mdb:MD_Metadata/mdb:identificationInfo[1]/mri:MD_DataIdentification[1]/mri:pointOfContact[3]/cit:CI_Responsibility[1]/cit:role[1]/cit:CI_RoleCode[1]/@codeListValue",
    "//mdb:MD_Metadata/mdb:identificationInfo[1]/mri:MD_DataIdentification[1]/mri:citation[1]/cit:CI_Citation[1]/cit:identifier[2]/mcc:MD_Identifier[1]/mcc:code[1]/gco:CharacterString[1]/text()",
    # "//mdb:MD_Metadata/mdb:identificationInfo[1]/mri:MD_DataIdentification[1]/mri:abstract[1]/gco:CharacterString[1]/text()",
    "//mdb:MD_Metadata/mdb:identificationInfo[1]/mri:MD_DataIdentification[1]/mri:resourceConstraints[1]/mco:MD_LegalConstraints[1]/mco:otherConstraints[1]/gco:CharacterString[1]/text()",
    "//mdb:MD_Metadata/mdb:identificationInfo[1]/mri:MD_DataIdentification[1]/mri:resourceConstraints[1]/mco:MD_LegalConstraints[1]/mco:useConstraints[1]/mco:MD_RestrictionCode[1]/@codeListValue",
    "//mdb:MD_Metadata/mdb:identificationInfo[1]/mri:MD_DataIdentification[1]/mri:status[1]/mcc:MD_ProgressCode[1]/@codeListValue",
    "//mdb:MD_Metadata/mdb:identificationInfo[1]/mri:MD_DataIdentification[1]/mri:status[1]/mcc:MD_ProgressCode[1]/@codeListValue",
    # "//mdb:MD_Metadata/mdb:resourceLineage[1]/mrl:LI_Lineage[1]/mrl:statement[1]/gco:CharacterString[1]/text()",
    "//mdb:MD_Metadata/mdb:identificationInfo[1]/mri:MD_DataIdentification[1]/mri:extent[1]/gex:EX_Extent[1]/gex:geographicElement[1]/gex:EX_GeographicBoundingBox[1]/gex:westBoundLongitude[1]/gco:Decimal[1]/text()",
    "//mdb:MD_Metadata/mdb:identificationInfo[1]/mri:MD_DataIdentification[1]/mri:extent[1]/gex:EX_Extent[1]/gex:geographicElement[1]/gex:EX_GeographicBoundingBox[1]/gex:eastBoundLongitude[1]/gco:Decimal[1]/text()",
    "//mdb:MD_Metadata/mdb:identificationInfo[1]/mri:MD_DataIdentification[1]/mri:extent[1]/gex:EX_Extent[1]/gex:geographicElement[1]/gex:EX_GeographicBoundingBox[1]/gex:southBoundLatitude[1]/gco:Decimal[1]/text()",
    "//mdb:MD_Metadata/mdb:identificationInfo[1]/mri:MD_DataIdentification[1]/mri:extent[1]/gex:EX_Extent[1]/gex:geographicElement[1]/gex:EX_GeographicBoundingBox[1]/gex:northBoundLatitude[1]/gco:Decimal[1]/text()",
    "//mdb:MD_Metadata/mdb:identificationInfo[1]/mri:MD_DataIdentification[1]/mri:resourceConstraints[1]/mco:MD_LegalConstraints[1]/mco:reference[1]/cit:CI_Citation[1]/cit:title[1]/gco:CharacterString[1]/text()",
    "//mdb:MD_Metadata/mdb:identificationInfo[1]/mri:MD_DataIdentification[1]/mri:resourceConstraints[1]/mco:MD_LegalConstraints[1]/mco:reference[1]/cit:CI_Citation[1]/cit:alternateTitle[1]/gco:CharacterString[1]/text()",
    "//mdb:MD_Metadata/mdb:identificationInfo[1]/mri:MD_DataIdentification[1]/mri:resourceConstraints[1]/mco:MD_LegalConstraints[1]/mco:reference[1]/cit:CI_Citation[1]/cit:edition[1]/gco:CharacterString[1]/text()",
    "//mdb:MD_Metadata/mdb:identificationInfo[1]/mri:MD_DataIdentification[1]/mri:resourceConstraints[1]/mco:MD_LegalConstraints[1]/mco:reference[1]/cit:CI_Citation[1]/cit:onlineResource[1]/cit:CI_OnlineResource[1]/cit:linkage[1]/gco:CharacterString[1]/text()",
    "//mdb:MD_Metadata/mdb:distributionInfo[1]/mrd:MD_Distribution[1]/mrd:distributor[1]/mrd:MD_Distributor[1]/mrd:distributorTransferOptions/mrd:MD_DigitalTransferOptions[1]/mrd:onLine[1]/cit:CI_OnlineResource[1]/cit:name[1]/gco:CharacterString[1]/text()",
    "//mdb:MD_Metadata/mdb:distributionInfo[1]/mrd:MD_Distribution[1]/mrd:distributor[1]/mrd:MD_Distributor[1]/mrd:distributorTransferOptions/mrd:MD_DigitalTransferOptions[1]/mrd:onLine[1]/cit:CI_OnlineResource[1]/cit:linkage[1]/gco:CharacterString[1]/text()",
    "//mdb:MD_Metadata/mdb:distributionInfo[1]/mrd:MD_Distribution[1]/mrd:distributor[1]/mrd:MD_Distributor[1]/mrd:distributorTransferOptions/mrd:MD_DigitalTransferOptions[1]/mrd:distributionFormat[1]/mrd:MD_Format[1]/mrd:formatSpecificationCitation[1]/cit:CI_Citation[1]/cit:title[1]/gco:CharacterString[1]/text()",
    "//mdb:MD_Metadata/mdb:identificationInfo[1]/*/mri:associatedResource/mri:MD_AssociatedResource[1]/mri:associationType[1]/mri:DS_AssociationTypeCode[1]/@codeListValue",
    "//mdb:MD_Metadata/mdb:identificationInfo[1]/*/mri:associatedResource/mri:MD_AssociatedResource[1]/mri:metadataReference[1]/cit:CI_Citation[1]/cit:identifier[1]/mcc:MD_Identifier[1]/mcc:code[1]/gco:CharacterString[1]/text()",
    "//mdb:MD_Metadata/mdb:identificationInfo[1]/*/mri:associatedResource/mri:MD_AssociatedResource[1]/mri:metadataReference[1]/cit:CI_Citation[1]/cit:title[1]/gco:CharacterString[1]/text()",
    "//mdb:MD_Metadata/mdb:identificationInfo[1]/*/mri:resourceMaintenance[1]/mmi:MD_MaintenanceInformation[1]/mmi:maintenanceAndUpdateFrequency[1]/mmi:MD_MaintenanceFrequencyCode[1]/@codeListValue",
    "//mdb:MD_Metadata/mdb:identificationInfo[1]/mri:MD_DataIdentification[1]/mri:citation[1]/cit:CI_Citation[1]/cit:date[2]/cit:CI_Date[1]/cit:date[1]/gco:DateTime[1]/text()",
    "//mdb:MD_Metadata/mdb:identificationInfo[1]/mri:MD_DataIdentification[1]/mri:citation[1]/cit:CI_Citation[1]/cit:date[2]/cit:CI_Date[1]/cit:dateType[1]/cit:CI_DateTypeCode[1]/@codeListValue",
    "//mdb:MD_Metadata/mdb:identificationInfo[1]/mri:MD_DataIdentification[1]/mri:citation[1]/cit:CI_Citation[1]/cit:date[1]/cit:CI_Date[1]/cit:date[1]/gco:DateTime[1]/text()",
    "//mdb:MD_Metadata/mdb:identificationInfo[1]/mri:MD_DataIdentification[1]/mri:citation[1]/cit:CI_Citation[1]/cit:date[1]/cit:CI_Date[1]/cit:dateType[1]/cit:CI_DateTypeCode[1]/@codeListValue",
    "//mdb:MD_Metadata/mdb:distributionInfo[1]/mrd:MD_Distribution[1]/mrd:distributor[1]/mrd:MD_Distributor[1]/mrd:distributorTransferOptions[2]/mrd:MD_DigitalTransferOptions[1]/mrd:onLine[1]/cit:CI_OnlineResource[1]/cit:description[1]/gco:CharacterString[1]/text()",
]
CSV_HEADER = [
    "ecatid",
    "title",
    "metadatascopecode",
    "datastoragelink",
    "keywords",
    "distributionlink",
    "scopecodename",
    "rolecodes_citation_role",
    "rolecodes_citation_name",
    "pointofcontact_name",
    "pointofcontact_role",
    "pointofcontact_value",
    "metadata_contact_role",
    "metadata_contact_value",
    "pid",
    "resource_provider",
    "doi",
    # "abstract",
    "copyright_statement",
    "copyright_use_constraints",
    "purpose",
    "status",
    # "lineage",
    "geographicalextent_west",
    "geographicalextent_east",
    "geographicalextent_south",
    "geographicalextent_north",
    "license_title",
    "license_alternatetitle",
    "license_edition",
    "license_onlineurl",
    "distribution_name",
    "distribution_url",
    "distribution_format",
    "associatedresources_type",
    "associatedresources_ecatid",
    "associatedresources_ecat_title",
    "maintenance_frequency",
    "publication_date",
    "publication_typecode",
    "creation_date",
    "creation_typecode",
    "label_description",
]


def xml_to_csv(input_xml, output_csv, namespaces, xpath_list, csv_header) -> None:
    tree = etree.parse(input_xml)
    data = []
    logger.info("Start populating data..")
    for xpath in xpath_list:
        result = tree.xpath(xpath, namespaces=namespaces)
        if result:
            data.append(", ".join(result))  # Join xpath with multiple values
        else:
            data.append(None)  # Append None if XPath does not exist
    logger.info("Completed populating data.")

    logger.info("Start writing to data to csv ...")
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(csv_header)
        writer.writerow(data)
    logger.info("Completed writing data to csv.")


def main() -> None:
    try:
        xml_to_csv(
            input_xml=INPUT_XML,
            output_csv=OUTPUT_CSV,
            namespaces=NAMESPACES,
            xpath_list=XPATH_LIST,
            csv_header=CSV_HEADER,
        )
    except Exception as e:
        logger.exception(f"Exception from main: {e}")


if __name__ == "__main__":
    main()
