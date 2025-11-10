from pathlib import Path

CHUNKSIZE = 10000

DATA_DIR = Path(__file__).resolve().parent / "downloads"
# Change this to your input dump flat-file(CSV) file path
INPUT_FILE = DATA_DIR / "metadata-dump-10-records.csv"
# Optionally change this to your output CSV file path
OUTPUT_FILE = DATA_DIR / "metadata-dump-transformed-output.csv"

LOG_FILE = DATA_DIR / "xml_to_csv.log"

# XPath expressions and namespaces for parsing ISO 19115-3 metadata XML files
# Note: Attempting to keep it minimal and clean, I may not have the complete namespace.
# If you add new xpaths and get namespace errors, please add to namespace dict as required.
NAMESPACES = {
    "cit": "http://standards.iso.org/iso/19115/-3/cit/2.0",
    "gco": "http://standards.iso.org/iso/19115/-3/gco/1.0",
    "gex": "http://standards.iso.org/iso/19115/-3/gex/1.0",
    "mcc": "http://standards.iso.org/iso/19115/-3/mcc/1.0",
    "mco": "http://standards.iso.org/iso/19115/-3/mco/1.0",
    "mdb": "http://standards.iso.org/iso/19115/-3/mdb/2.0",
    "mrd": "http://standards.iso.org/iso/19115/-3/mrd/1.0",
    "mri": "http://standards.iso.org/iso/19115/-3/mri/1.0",
    "mrl": "http://standards.iso.org/iso/19115/-3/mrl/2.0",
    "mmi": "http://standards.iso.org/iso/19115/-3/mmi/1.0",
    "srv": "http://standards.iso.org/iso/19115/-3/srv/2.1",
    "mrs": "http://standards.iso.org/iso/19115/-3/mrs/1.0",
    "gcx": "http://standards.iso.org/iso/19115/-3/gcx/1.0",
    "xlink": "http://www.w3.org/1999/xlink",
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
        "/mdb:MD_Metadata/mdb:identificationInfo/mri:MD_DataIdentification/mri:resourceFormat/mrd:MD_Format/mrd:formatSpecificationCitation/cit:CI_Citation/cit:onlineResource/cit:CI_OnlineResource/cit:linkage/gco:CharacterString/text()",
        "datastoragelink",
    ),
    (
        "//mdb:MD_Metadata/mdb:identificationInfo[1]/*/mri:descriptiveKeywords/mri:MD_Keywords[1]/mri:keyword[1]/gco:CharacterString[1]/text()",
        "keywords",
    ),
    (
        "/mdb:MD_Metadata/mdb:metadataScope/mdb:MD_MetadataScope/mdb:resourceScope/mcc:MD_ScopeCode[1]/@codeListValue",
        "metadatascopecode",
    ),
    (
        "/mdb:MD_Metadata/mdb:metadataScope/mdb:MD_MetadataScope/mdb:name/gco:CharacterString/text()",
        "scopecodename",
    ),
    (
        "/mdb:MD_Metadata/mdb:identificationInfo[1]/*/mri:citation[1]/cit:CI_Citation[1]/cit:identifier[1]/mcc:MD_Identifier[1]/mcc:code[1]/gco:CharacterString[1]/text()",
        "pid",
    ),
    (
        "//mdb:MD_Metadata/mdb:identificationInfo[1]/*/mri:citation[1]/cit:CI_Citation[1]/cit:identifier[2]/mcc:MD_Identifier[1]/mcc:code[1]/gco:CharacterString[1]/text()",
        "doi",
    ),
    # (
    #     "/mdb:MD_Metadata/mdb:identificationInfo/mri:MD_DataIdentification/mri:citation/cit:CI_Citation/cit:identifier/mcc:MD_Identifier/mcc:code/gcx:Anchor/text()",
    #     "doi_alternate_1",
    # ),
    # (
    #     "/mdb:MD_Metadata/mdb:identificationInfo/mri:MD_DataIdentification/mri:citation/cit:CI_Citation/cit:identifier/mcc:MD_Identifier/mcc:code/gcx:Anchor/@xlink:href",
    #     "doi_alternate_2",
    # ),
    (
        "//mdb:MD_Metadata/mdb:identificationInfo/*/mri:resourceConstraints/mco:MD_LegalConstraints/mco:otherConstraints/gco:CharacterString/text()",
        "copyright_statement",
    ),
    (
        "//mdb:MD_Metadata/mdb:identificationInfo/*/mri:resourceConstraints/mco:MD_LegalConstraints/mco:useConstraints/mco:MD_RestrictionCode/@codeListValue",
        "copyright_use_constraints",
    ),
    (
        "/mdb:MD_Metadata/mdb:identificationInfo[1]/*/mri:purpose[1]/gco:CharacterString[1]/text()",
        "purpose",
    ),
    (
        "/mdb:MD_Metadata/mdb:identificationInfo[1]/*/mri:status[1]/mcc:MD_ProgressCode[1]/@codeListValue",
        "status",
    ),
    (
        "//mdb:distributionInfo//mrd:MD_DigitalTransferOptions//cit:linkage/gco:CharacterString/text()",
        "distributionlink",
    ),
    (
        "//mdb:distributionInfo//mrd:MD_DigitalTransferOptions//gco:CharacterString/text()",
        "distribution_info",
    ),
    (
        "//mdb:MD_Metadata/mdb:identificationInfo[1]/*/mri:resourceMaintenance[1]/mmi:MD_MaintenanceInformation[1]/mmi:maintenanceAndUpdateFrequency[1]/mmi:MD_MaintenanceFrequencyCode[1]/@codeListValue",
        "maintenance_frequency",
    ),
    (
        """
        //mdb:MD_Metadata/mdb:identificationInfo/*/mri:citation/cit:CI_Citation/cit:date/cit:CI_Date/cit:date/*/text()
        |
        //mdb:MD_Metadata/mdb:identificationInfo/*/mri:citation/cit:CI_Citation/cit:date/cit:CI_Date/cit:dateType/cit:CI_DateTypeCode/@codeListValue
        """,
        "resource_dates",
    ),
    (
        "//mdb:MD_Metadata/mdb:distributionInfo[1]/mrd:MD_Distribution[1]/mrd:distributor[1]/mrd:MD_Distributor[1]/mrd:distributorTransferOptions[2]/mrd:MD_DigitalTransferOptions[1]/mrd:onLine[1]/cit:CI_OnlineResource[1]/cit:description[1]/gco:CharacterString[1]/text()",
        "label_description",
    ),
    # New XPaths added below
    (
        "//mdb:MD_Metadata/mdb:identificationInfo/mri:MD_DataIdentification/mri:pointOfContact/cit:CI_Responsibility/cit:role/cit:CI_RoleCode/@codeListValue",
        "pointofcontact_role",
    ),
    (
        "//mdb:MD_Metadata/mdb:identificationInfo/mri:MD_DataIdentification/mri:pointOfContact/cit:CI_Responsibility/cit:party/*/cit:name/gco:CharacterString/text()",
        "pointofcontact_value",
    ),
    (
        "//mdb:MD_Metadata/mdb:contact/cit:CI_Responsibility/cit:role/cit:CI_RoleCode/@codeListValue",
        "metadata_contact_role",
    ),
    (
        "//mdb:MD_Metadata/mdb:contact/cit:CI_Responsibility/cit:party/*/cit:name/gco:CharacterString/text()",
        "metadata_contact_value",
    ),
    (
        "//mdb:MD_Metadata/mdb:identificationInfo/mri:MD_DataIdentification/mri:citation/cit:CI_Citation/cit:citedResponsibleParty/cit:CI_Responsibility/cit:role/cit:CI_RoleCode/@codeListValue",
        "rolecodes_citation_role",
    ),
    (
        "//mdb:MD_Metadata/mdb:identificationInfo[1]/mri:MD_DataIdentification/mri:citation/cit:CI_Citation/cit:citedResponsibleParty/cit:CI_Responsibility/cit:party/*/cit:name/gco:CharacterString/text()",
        "rolecodes_citation_value",
    ),
    (
        "/mdb:MD_Metadata/mdb:identificationInfo/*/mri:citation/cit:CI_Citation/cit:series/cit:CI_Series/cit:name/gco:CharacterString/text()",
        "series",
    ),
    (
        "/mdb:MD_Metadata/mdb:identificationInfo/*/mri:citation/cit:CI_Citation/cit:series/cit:CI_Series/cit:issueIdentification/gco:CharacterString/text()",
        "issue_identification",
    ),
    (
        "/mdb:MD_Metadata/mdb:referenceSystemInfo/mrs:MD_ReferenceSystem/mrs:referenceSystemIdentifier/mcc:MD_Identifier/mcc:code/gco:CharacterString/text()",
        "reference_system",
    ),
    (
        "/mdb:MD_Metadata/mdb:identificationInfo/*/mri:extent/gex:EX_Extent/gex:verticalElement/gex:EX_VerticalExtent/gex:verticalCRSId/mrs:MD_ReferenceSystem/mrs:referenceSystemIdentifier/mcc:MD_Identifier/mcc:code/gco:CharacterString/text()",
        "vertical_reference_system",
    ),
    (
        "/mdb:MD_Metadata/mdb:metadataIdentifier/mcc:MD_Identifier/mcc:code/gco:CharacterString/text()",
        "uuid",
    ),
    (
        """//mdb:MD_Metadata/mdb:identificationInfo/*/mri:resourceConstraints[1]/mco:MD_LegalConstraints/mco:reference/cit:CI_Citation/*/gco:CharacterString/text() 
        |
        //mdb:MD_Metadata/mdb:identificationInfo[1]/*/mri:resourceConstraints[1]/mco:MD_LegalConstraints[1]/mco:reference[1]/cit:CI_Citation[1]/cit:onlineResource[1]/cit:CI_OnlineResource[1]/cit:linkage[1]/gco:CharacterString[1]/text()
        """,
        "license",
    ),
    (
        "/mdb:MD_Metadata/mdb:identificationInfo/*/mri:extent/gex:EX_Extent/gex:geographicElement/gex:EX_GeographicBoundingBox/*/gco:Decimal/text()",
        "geographicalextent_w_e_s_n",
    ),
    # Combined XPath for associated resources
    (
        """
        //mdb:MD_Metadata/mdb:identificationInfo/*/mri:associatedResource/mri:MD_AssociatedResource/mri:associationType/mri:DS_AssociationTypeCode/@codeListValue
        |
        //mdb:MD_Metadata/mdb:identificationInfo/*/mri:associatedResource/mri:MD_AssociatedResource/mri:metadataReference/cit:CI_Citation/cit:title/gco:CharacterString/text()
        |
        //mdb:MD_Metadata/mdb:identificationInfo/*/mri:associatedResource/mri:MD_AssociatedResource/mri:metadataReference/cit:CI_Citation/cit:identifier/mcc:MD_Identifier/mcc:code/gco:CharacterString/text()
        """,
        "associatedresources_type_title_ecatid_uuid",
    ),
    # Long text fields after this line.
    (
        "/mdb:MD_Metadata/mdb:identificationInfo/*/mri:abstract/gco:CharacterString/text()",
        "abstract",
    ),
    (
        "/mdb:MD_Metadata/mdb:resourceLineage/mrl:LI_Lineage/mrl:statement/gco:CharacterString/text()",
        "lineage",
    ),
]
