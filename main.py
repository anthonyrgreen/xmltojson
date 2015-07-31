import lxml.etree as ET
import json as JS

class treeParser:
  def __init__(self, filename, parserFunction):
    xmlFile = open(filename, "rb")
    self.parserFunction = parserFunction
    tree = ET.iterparse(filename, events=("start", "end"))
    self.tree = iter(tree)
    _, self.root = self.tree.next()
  def __iter__(self):
    return self.iterator()
  def iterator(self):
    for event, elem in self.tree:
      if event == "end" and elem.tag == "ClinVarSet":
        yield self.parserFunction(elem)
        self.root.clear()

def toJson(element):

  def singleAttrFromPath(path, attrType, attrName="", modFunc = lambda x: x):
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

  def allAttrsFromPath(path, attrType, attrName="",
                       predicateFunc=lambda _: True, modFunc=lambda x: x):
    nodes = [node for node in element.findall(path) if predicateFunc(node)]
    # in the case of an attribute
    if attrType == "attr":
      attrs = [node.get(attrName, "Undefined") for node in nodes if predicateFunc(node)]
      return map(modFunc, attrs)
    # in the case of text
    else:
      return [modFunc(node.text) for node in nodes]

  # modification functions
  noMod       = lambda x: x.encode("utf-8")
  rsIdMod     = lambda x: "rs" + x.encode("utf-8")
  # predicate functions
  noPredicate = lambda _: True
  hvgsPred    = lambda x: "HVGS" in x.get("DB", default="Undefined")
  rsIdPred    = lambda x: x.get("DB", default="Undefined") == "dbSNP"
  entrezPred  = lambda x: x.get("DB", default="Undefined") == "Gene"
  # path constants
  base        = "ReferenceClinVarAssertion/"
  measureBase = base + "MeasureSet/Measure/"
  # FIELDS
  # (name, path, text/attr, attr_name, type_func, mod_func)
  singleProperties = \
    [("rcvaccession",          base + "ClinVarAccession",                 "attr", "Acc",     str, noMod)
    ,("rcvaccession_version",  base + "ClinVarAccession",                 "attr", "Version", int, noMod)
    ,("type",                  base + "MeasureSet/Measure",               "attr", "Type",    str, noMod)
    ,("clinical_significance", base + "ClinicalSignificance/Description", "text", "",        str, noMod)
    ,("title",                 "Title",                                   "text", "",        str, noMod)
    ,("preferred_name",        measureBase + "Name/ElementValue",         "text", "",        str, noMod)]
  # (name, path, text/attr, attr_name, type_func, mod_func, pred_func)
  multipleProperties = \
    [("hgvs",           measureBase + "AttributeSet/Attribute",   "text", "",   str, noMod,   hvgsPred)
    ,("entrez_gene_id", measureBase + "MeasureRelationship/XRef", "attr", "ID", str, noMod,   entrezPred)
    ,("rs_id",          measureBase + "XRef",                     "attr", "ID", str, rsIdMod, rsIdPred)]

  result = {}
  for prop in singleProperties:
    result[prop[0]] = prop[4](singleAttrFromPath(prop[1], prop[2],
                              attrName=prop[3], modFunc=prop[5]))
  for prop in multipleProperties:
    result[prop[0]] = prop[4](allAttrsFromPath(prop[1], prop[2],
                              attrName=prop[3], modFunc=prop[5], predicateFunc=prop[6]))
  result["rcvaccession_full"] = result["rcvaccession"] + "." + str(result["rcvaccession_version"])
  result["uuid"] = 5

  return JS.dumps(result)

tree = treeParser("ClinVarFullRelease_2014-08.xml", toJson)
