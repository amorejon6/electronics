import xml.etree.ElementTree as ET
import json

def get_text(root, path, ns):
    el = root.find('.//' + path, ns)
    return el.text.strip() if el is not None and el.text else None

def get_attrib(root, path, attrib, ns):
    el = root.find('.//' + path, ns)
    return el.attrib.get(attrib, None) if el is not None and attrib in el.attrib else None

def get_lang(attrib):
    if attrib == "Español":
        return 'https://id.loc.gov/vocabulary/iso639-1/es.html'
    elif attrib == "English":
        return 'https://id.loc.gov/vocabulary/iso639-1/en.html'

def extract_metadata(filename):

    tree = ET.parse(filename)
    root = tree.getroot()

    ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
    dcat = {
        "dcterms:title": get_text(root, 'tei:titleStmt/tei:title', ns),
        "dcterms:creator": get_text(root, 'tei:titleStmt/tei:author', ns),
        "dcterms:publisher": get_text(root, 'tei:publicationStmt/tei:publisher', ns),
        "dcterms:license": get_text(root, 'tei:publicationStmt/tei:availability', ns),
        "dcterms:identifier": get_attrib(root, 'tei:publicationStmt/tei:ref[@type="doi"]', 'target', ns)
    }

    language = get_text(root, 'tei:langUsage/tei:language', ns)
    dcat["dcterms:language"] = get_lang(language)

    distributor = root.find('.//tei:publicationStmt/tei:distributor', ns)
    if distributor is not None:
        dcat["prov:qualifiedAttribution"] = {
            "prov:agent": get_attrib(root, 'tei:publicationStmt/tei:distributor', 'ref', ns),
            "dcat:hadRole": "distributor"
        }

    dcat = {k: v for k, v in dcat.items() if v is not None}

    # print(json.dumps(dcat, ensure_ascii=False, indent=2))
    return dcat


if __name__ == "__main__":
    print(extract_metadata("SPA1001_GilYCarrasco_ElSenyorDeBembibre.xml"))