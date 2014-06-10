# -*- coding: utf-8 -*-
from lxml import etree
from datetime import datetime
from csv import DictWriter
from urlparse import urlparse
import re

from simpleslugger import make_slug

SUPPORTED_LAYOUT_VERSION = "1.0"
INCLUDE_EMAIL = False
INCLUDE_PHONE = False
INCLUDE_DESCRIPTION = True
csv_schema = [
    "id",
    "name",
    "abbreviation",
    "other_names",
    "description",
    "classification",
    "parent_id",
    "founding_date",
    "dissolution_date",
    "image",
    "url",
    "jurisdiction_code",
    "email",
    "address",
    "contact",
    "tags",
    "source_url",
]
column_map = {
    "name": "Nome",
    "abbreviation": "Sigla",
    #"id": "Codigo", # use slug instead
    "parent_id": "Codigo_Pai",
}
localnumberpattern = re.compile(r"\s*\d{4,5}\s*-?\s*\d{4}")
paragraphpattern = re.compile(r"[CP]\d{3}")
bulletpointpattern = re.compile(r"[IK]\d{3}")

class SIORGReader():
    "Reads the SIORG xml files using lxml."
    def __init__(self, parse_file=""):
        self.global_metadata = {}
        self.public_bodies = []
        self.body_by_code = {}
        if parse_file:
            self.parse(parse_file)
    def readHeader(self, elem):
        "Reads metadata from the Header element."
        self.global_metadata["layout_version"] = elem.xpath("Versao_Layout/text()")[0]
        if self.global_metadata["layout_version"] != SUPPORTED_LAYOUT_VERSION:
            print "Warning: expected layout version %s, got %s" % \
                (SUPPORTED_LAYOUT_VERSION, self.global_metadata["layout_version"])
        generated_date = elem.xpath("Data_Geracao_Arquivo/text()")[0]
        generated_time = elem.xpath("Hora_Geracao_Arquivo/text()")[0]
        generated_datetime = datetime.strptime(
            "%s %s" % (generated_date, generated_time),
            "%d/%m/%Y %H:%M:%S"
        )
        self.global_metadata["generated_at"] = generated_datetime

class SIORGDomainReader(SIORGReader):
    "Reads the SIORG xml domain file using lxml."
    def __init__(self, parse_file=""):
        self.body_types = {}
        self.legal_entity_types = {}
        SIORGReader.__init__(self, parse_file=parse_file)
    def parse(self, filename):
        "Parses a SIORG xml file."
        with open(filename)as f:
            context = etree.iterparse(f)
            for action, elem in context:
                if elem.tag == "Header":
                    self.readHeader(elem)
                elif (elem.tag == "Tipo_Orgao") and \
                   elem.xpath("Indicador_Extincao/text()")[0] == "0" :
                        self.readBodyType(elem)
                elif (elem.tag == "Natureza_Juridica") and \
                   elem.xpath("Indicador_Extincao/text()")[0] == "0" :
                        self.readLegalEntityType(elem)
    def readBodyType(self, elem):
        "Reads information on a public body type."
        code = u"".join(elem.xpath("Codigo/text()"))
        description = u"".join(elem.xpath("Descricao/text()"))
        self.body_types[code] = description
    def readLegalEntityType(self, elem):
        "Reads information on legal entity type,"
        code = u"".join(elem.xpath("Codigo/text()"))
        description = u"".join(elem.xpath("Descricao/text()"))
        self.legal_entity_types[code] = description

class BRPublicBodyReader(SIORGReader):
    "Reads the SIORG xml dump using lxml."
    def __init__(self, parse_file="", domain=None):
        self.public_bodies = []
        self.body_by_code = {}
        self.domain = domain
        SIORGReader.__init__(self, parse_file=parse_file)
    def parse(self, filename):
        "Parses a SIORG xml file."
        with open(filename)as f:
            context = etree.iterparse(f)
            for action, elem in context:
                if elem.tag == "Header":
                    self.readHeader(elem)
                elif (elem.tag == "Orgao") and \
                    elem.xpath("Dados_Cadastro/Indicador_Organizacao/text()")[0] == "O" and \
                    elem.xpath("Dados_Cadastro/Codigo_Orgao_Topo/text()")[0] not in ["2", "5", "10", "14", "21", "26", "30", "36", "62", "73"] and \
                    elem.xpath("Dados_Cadastro/Codigo_Tipo_Orgao/text()")[0] not in ["9", "45", "46"] and \
                    elem.xpath("Dados_Cadastro/Indicador_Extincao/text()")[0] == "false":
                        self.readBody(elem)
    def readBody(self, elem):
        "Reads information on a public body."
        cadastro = elem.xpath("Dados_Cadastro")[0]
        body = {}
        for col, elem_name in column_map.items():
            value = cadastro.xpath("%s/text()" % elem_name)
            if value:
                body[col] = unicode(value[0])
        body["slug"] = make_slug(body["name"])
        # # TODO: set category
        # body["category"] = tipo e natureza juridica
        # the following is disabled for now as it's too long
        # body["description"] = elem.xpath("Competencia/Descricao")[0]
        body["jurisdiction_code"] = u"BR"
        body["id"] = u"%s/%s" % (body["jurisdiction_code"].lower(), body["slug"])
        body["source_url"] = u"http://repositorio.dados.gov.br/governo-politica/administracao-publica/estrutura-organizacional/"
        body_type_code = u"".join(cadastro.xpath("Codigo_Tipo_Orgao/text()"))
        body_type_description = self.domain.body_types.get(body_type_code, None)
        if body_type_description:
            body["classification"] = body_type_description
        legal_entity_type_code = u"".join(cadastro.xpath("Codigo_Natureza_Juridica/text()"))
        legal_entity_type_description = self.domain.legal_entity_types.get(legal_entity_type_code, None)
        if legal_entity_type_description:
            # the schema doesn't have a legal entity type field, so we add to the tags
            body["tags"] = self.addTag(body, make_slug(legal_entity_type_description))
        localidade = elem.xpath("Localidade")[0]
        body["address"] = u", ".join(
            localidade.xpath("Descricao_Endereco/text()") +
            localidade.xpath("Descricao_Complemento/text()") +
            localidade.xpath("Nome_Cidade/text()") +
            localidade.xpath("Sigla_UF/text()")
            ) + u", Brasil"
        body["address"].replace(u",",u";")
        urlx = cadastro.xpath("Site/text()")
        if urlx:
            url = urlparse(unicode(urlx[0]))
        else:
            url = urlparse(u"")
        if url.geturl() == u"http://":
            body["url"] = u""
        elif not url.netloc and url.geturl().strip():
            # for bugged relative urls missing http://
            body["url"] = u"http://" + url.geturl()
        else:
            body["url"] = url.geturl()
        if INCLUDE_EMAIL:
            body["email"] = u"".join(cadastro.xpath("Email/text()"))
        if INCLUDE_PHONE:
            import phonenumbers
            areacode = u"".join(cadastro.xpath("DDD/text()"))
            # phonenumbers phone number parsing library needs a placeholder carrier, this is discarded after parsing
            # dirty data sometimes use a single "0" for regional area codes, sometimes for international area codes
            if re.match(r"^0\d", areacode.strip()) and len(areacode.strip()) > 3:
                areacode = u"0021" + areacode.strip()[:1]
            else: # national area code
                areacode = u"021" + areacode.strip().replace(u"0xx", u"") # remove carrier selector placeholder
            localnumbers = u"".join(cadastro.xpath("Telefones/text()"))
            localnumbermatch = next(localnumberpattern.finditer(localnumbers), None)
            if localnumbermatch:
                localnumber = localnumbermatch.group()
                phonenumber = phonenumbers.parse(areacode + localnumber, "BR")
                body["contact"] = phonenumbers.format_number(phonenumber, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        if INCLUDE_DESCRIPTION:
            descricao = elem.xpath("Finalidade/Descricao/text()")
            if not descricao:
                descricao = elem.xpath("Competencia/Descricao/text()")
            body["description"] = bulletpointpattern.subn(u" * ", paragraphpattern.subn(u"", u"".join(descricao))[0])[0]
        baselegal = elem.xpath("Base_Legal")[0]
        body["founding_date"] = unicode(datetime.strptime(baselegal.xpath("Data/text()")[0], "%d-%m-%Y").date().isoformat())
        #body["updated_at"] = self.global_metadata["generated_at"].isoformat()
        self.public_bodies.append(body)
        self.body_by_code[int(cadastro.xpath("Codigo/text()")[0])] = body
    @staticmethod
    def addTag(body, tag):
        tags = set(body.get("tags", "").split(u",")).discard(u"") or set()
        tags.add(tag)
        return u",".join(tags)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print "Usage: %s [filename] [outfile] [domainfilename]" % sys.argv[0]
        print "\n    filename:    file containing the Brazilian government's SIORG xml dump"
        print "           outfile:  output csv filename (optional)"
        print "    domainfilename:  file containing domain table information (optional)"
        print "                     (note: both files can be obtained at the following URL)"
        print "                      http://repositorio.dados.gov.br/governo-politica/administracao-publica/estrutura-organizacional/"
    else:
        filename = sys.argv[1]
        if len(sys.argv) > 3:
            domainfilename = sys.argv[3]
            domain = SIORGDomainReader(parse_file=domainfilename)
            print "Read metadata on %d public body types and %d legal entity types." % \
                (len(domain.body_types), len(domain.legal_entity_types))
        else:
            domain = None
        reader = BRPublicBodyReader(domain=domain)
        reader.parse(filename)
        print "Read information on %d public bodies." % len(reader.public_bodies)
        if len(sys.argv) > 2:
            outfilename = sys.argv[2]
            print "Writing to %s..." % outfilename
            with open(outfilename, "w") as f:
                writer = DictWriter(f, delimiter=",", fieldnames=csv_schema)
                writer.writerow(dict((fn, fn) for fn in csv_schema))
                #reader.public_bodies.sort(cmp=lambda m, n: int(m["key"]) - int(n["key"]))
                reader.public_bodies.sort(key=lambda b: b["slug"])
                for body in reader.public_bodies:
                    parent = reader.body_by_code.get(int(body["parent_id"]), "")
                    if parent:
                        body["parent_id"] = parent["id"]
                    else:
                        if body["parent_id"] == u"26":
                            body["parent"] = u"Presidência da República"
                            body["parent_id"] = u"br/presidencia-republica"
                    writer.writerow(dict((key, value.encode("utf-8")) for key, value in body.items() if key in csv_schema))
                print "Done."
    
