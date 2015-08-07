import lxml.etree as ET
import json as JS
import uuid

class treeParser:
  def __init__(self, filename, tagname, parserFunction):
    xmlFile = open(filename, "rb")
    self.tagname = tagname
    self.parserFunction = parserFunction
    tree = ET.iterparse(filename, events=("start", "end"))
    self.tree = iter(tree)
    _, self.root = self.tree.next()
  def __iter__(self):
    return self.iterator()
  def iterator(self):
    for event, elem in self.tree:
      if event == "end" and elem.tag == self.tagname:
        yield self.parserFunction(elem)
        self.root.clear()

def toJsonSchema(element):

  noMod       = lambda x: x.encode("utf-8")
  noPredicate = lambda _: True

  def getAttr(path, attrType, attrName="", modFunc=noMod):
    # in the case of an attribute
    if attrType == "attr":
      node = element.find(path)
      if node == None:
        return "Undefined"
      else:
        return modFunc(node.get(attrName, "Undefined"))
    # get the text
    else:
      return modFunc(element.findtext(path, default="Undefined"))

  def getAttrs(path, attrType, attrName="", predicateFunc=noPredicate, modFunc=noMod):
    nodes = [node for node in element.findall(path) if predicateFunc(node)]
    # in the case of an attribute
    if attrType == "attr":
      return [modFunc(node.get(attrName, "Undefined"))
              for node in nodes if predicateFunc(node)]
    # in the case of text
    else:
      return [modFunc(node.text) for node in nodes]

  result = {}
  # path constants
  base        = "ReferenceClinVarAssertion/"
  measureBase = base + "MeasureSet/Measure/"
  # single-valued attributes
  result["rcvaccession_version"]  = int(getAttr(base + "ClinVarAccession",
                                                "attr", "Version"))
  result["rcvaccession"]          = getAttr(base + "ClinVarAccession",
                                            "attr", "Acc")
  result["type"]                  = getAttr(base + "MeasureSet/Measure",
                                            "attr", "Type")
  result["clinical_significance"] = getAttr(base + "ClinicalSignificance/Description",
                                            "text")
  result["title"]                 = getAttr("Title",
                                            "text")
  result["preferred_name"]        = getAttr(measureBase + "Name/ElementValue",
                                            "text")
  # multiple-valued attributes
  # predicate and modification functions
  hvgsPred    = lambda x: "HVGS" in x.get("DB", default="Undefined")
  rsIdPred    = lambda x: x.get("DB", default="Undefined") == "dbSNP"
  entrezPred  = lambda x: x.get("DB", default="Undefined") == "Gene"
  rsIdMod     = lambda x: "rs" + x.encode("utf-8")

  result["hgvs"]           = getAttrs(measureBase + "AttributeSet/Attribute",
                                      "text",
                                      predicateFunc=hvgsPred)
  result["entrez_gene_id"] = getAttrs(measureBase + "MeasureRelationship/XRef",
                                      "attr", "ID",
                                      predicateFunc=entrezPred)
  result["rs_id"]          = getAttrs(measureBase + "XRef",
                                      "attr", "ID",
                                      modFunc=rsIdMod,
                                      predicateFunc=rsIdPred)
  # extra attributes
  result["rcvaccession_full"] = result["rcvaccession"] + "." + \
                                str(result["rcvaccession_version"])
  result["uuid"] = uuid.uuid4().hex

  return JS.JSONEncoder().encode(result)
