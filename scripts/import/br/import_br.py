"""Imports Brazilian public body data from the official source and
complements it with data from several auxiliary sources.

Official source: [SIORG's open data API](https://dados.gov.br/dataset/siorg)
"""

# dependencies
# standard library
import io, re
import argparse
from urllib.parse import urlparse

# packages
import requests
import pandas as pd
import numpy as np
from slugify import slugify

# data sources
# official source
URL = "http://estruturaorganizacional.dados.gov.br/doc/orgao-entidade/completa.json"
URL_CATEGORIAS = "http://estruturaorganizacional.dados.gov.br/doc/categoria-unidade"
URL_NATUREZAJURIDICA = (
    "http://estruturaorganizacional.dados.gov.br/doc/natureza-juridica"
)
URL_SUBNATUREZAJURIDICA = (
    "http://estruturaorganizacional.dados.gov.br/doc/subnatureza-juridica"
)

# auxiliary sources
URL_OLD_FILE = "https://github.com/okfn/publicbodies/raw/c7466bbfad3169e573b6e7f2ff92a3861bfda82a/data/br.csv"
URL_MUNICIPIOS = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
URL_PAISES = "https://balanca.economia.gov.br/balanca/bd/tabelas/PAIS.csv"
URL_IMAGES = "https://legado.dados.gov.br/api/3/action/organization_list?all_fields=1&include_extras=1"

# config for making requests
USER_AGENT = "PublicBodiesBot (https://github.com/okfn/publicbodies)"

# regular expressions
phone_re = re.compile(r"(?:\((\d{1,3})\)\s*)?(?:\((\d{1,2})\)\s)?([0-9- ]{7,9})")


def import_br_data(url: str, output: str):
    "Imports data from the SIORG open data API on the given URL."

    # initiate the requests session
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    # get the json data on the public bodies
    print(f"Fetching public bodies data from {url}...")
    response = session.get(url)
    data = response.json()

    # filter data to get only federal level and executive branch
    base_id = "estruturaorganizacional.dados.gov.br/id/"
    filtered_data = [
        unidade
        for unidade in data["unidades"]
        if unidade["codigoEsfera"].split("://")[-1] == f"{base_id}esfera/1"
        and unidade["codigoPoder"].split("://")[-1] == f"{base_id}poder/1"
    ]

    # get the old data for filling some missing values
    print(f"Fetching old public bodies data from {URL_OLD_FILE}...")
    br_old = pd.read_csv(URL_OLD_FILE)

    # add the 'phone' column, which didn't exist at the time
    columns = list(br_old.columns)
    columns.insert(columns.index("email"), "phone")

    df = pd.DataFrame(columns=columns)
    df["id"] = ["/".join(("br", slugify(orgao["nome"]))) for orgao in filtered_data]
    df["name"] = [orgao["nome"] for orgao in filtered_data]
    df["abbreviation"] = [orgao["sigla"] for orgao in filtered_data]

    # the dataset does not have a description for Brazilian public bodies.
    # As a substitute, we take the purpose, and failing that, the legal
    # competencies of the body.
    df["description"] = [
        orgao["finalidade"] if orgao.get("finalidade", None) else orgao["competencia"]
        for orgao in filtered_data
    ]

    # the category is very generic for the type 'Vinculado', so we take
    # the nature of the legal person to enrich the possible categories
    print(f"Fetching nj data from {URL_NATUREZAJURIDICA}...")
    natureza_juridica_response = session.get(URL_NATUREZAJURIDICA)
    natureza_juridica_data = natureza_juridica_response.json()
    natureza_juridica_map = {
        natureza_juridica["codigoNaturezaJuridica"]: natureza_juridica[
            "descricaoNaturezaJuridica"
        ]
        for natureza_juridica in natureza_juridica_data["naturezaJuridica"]
        if natureza_juridica["ativo"] == "SIM"
    }

    print(f"Fetching category data from {URL_CATEGORIAS}...")
    categorias_response = session.get(URL_CATEGORIAS)
    categorias_data = categorias_response.json()
    category_map = {
        categoria["codigoCategoriaUnidade"]: categoria["descricaoCategoriaUnidade"]
        for categoria in categorias_data["categoriaUnidade"]
        if categoria["ativo"] == "SIM"
    }

    def get_category(code: str, nj: str) -> str:
        "Retorna a categoria do órgão com base no código."
        category = category_map[int(code.split("/")[-1])]
        if category == "Vinculado":
            category += f' ({natureza_juridica_map[int(nj.split("/")[-1])]})'
        return category

    df["classification"] = [
        get_category(orgao["codigoCategoriaUnidade"], orgao["codigoNaturezaJuridica"])
        for orgao in filtered_data
    ]

    # we need to map the public bodies internal code to their respective
    # names, in order to be able to build the proper parent_id
    code_map = {orgao["codigoUnidade"]: orgao["nome"] for orgao in data["unidades"]}

    df["parent_id"] = [
        (
            "/".join(("br", slugify(code_map[orgao["codigoUnidadePai"]])))
            if orgao["codigoUnidadePai"].split("/")[-1]
            not in (
                "208615",  # poder executivo
                "208613",  # poder executivo
                "244320",  # poder legislativo
                "244321",  # poder judiciário
                "244322",  # funções essenciais à justiça
                "94",  # comando do exército
                "185",  # comando da marinha
                "48",  # comando da aeronáutica
            )
            else None  # set to None those parents which are not present
        )
        for orgao in filtered_data
    ]

    # get URLs of images, like logos and photos, from the dados.gov.br
    # open data portal. Luckily, those have the siorg code property set.
    print(f"Fetching image URLs from {URL_IMAGES}...")
    images_response = requests.get(URL_IMAGES)
    images_data = images_response.json()

    image_map = {
        int(extra["value"]): organization["image_display_url"]
        for organization in images_data["result"]
        if len(organization.get("extras", "")) > 0
        for extra in organization["extras"]
        if extra["key"].lower() == "siorg"
    }

    df["image"] = [
        image_map.get(int(orgao["codigoUnidade"].split("/")[-1]), None)
        for orgao in filtered_data
    ]

    def cleanup_url(url: str, verbose: bool = False):
        old_url = url
        url = url.strip()  # some have leading or trailing spaces
        url = url.replace(" ", "")  # others, white space right in the middle
        # yet others, a trailing dash or dot
        if url.endswith(".br-") or url.endswith(".br."):
            url = url[:-1]
        url = url.replace("http://http://", "http://")  # double scheme
        parsed = urlparse(url)
        if not parsed.scheme:  # some don't have the scheme part
            url = f"https://{url}"
        else:
            url = parsed.geturl()
        if verbose and url != old_url:
            print(f'cleaned from "{old_url}" to "{url}"')
        return url

    # finds and cleans dirty data of the public body's website
    def get_site_url(contato: list) -> str:
        "Retorna a URL do site institucional."
        if len(contato) < 1:
            return None
        contact = contato[0]
        site_details = contact.get("site", None)
        if site_details is None:
            return None
        sites = [  # we only want URLs of the type 'official site'
            site for site in site_details if site["tipo"] == "Site Institucional"
        ]
        if len(sites) < 1:
            return None
        else:
            url = sites[0]["site"]
            return cleanup_url(url)

    df["url"] = [get_site_url(orgao["contato"]) for orgao in filtered_data]

    # fix urls also in the old file
    br_old["url"] = br_old["url"].apply(
        lambda v: cleanup_url(v) if isinstance(v, str) else v
    )

    # some URLs missing from the official source can be found in the
    # old version of the dataset
    missing_url = (
        df[df.url.isna()]
        .reset_index()
        .merge(br_old.loc[:, ["abbreviation", "url"]], on="abbreviation")
        .set_index("index")
        .rename(columns={"url_y": "url"})
        .loc[:, ["abbreviation", "url"]]
    )
    df.update(missing_url.url)

    # always the same for the whole dataset
    df["jurisdiction_code"] = ["BR" for orgao in filtered_data]

    def get_email(contato: list) -> str:
        "Retorna o e-mail institucional."
        if len(contato) < 1:
            return None
        contact = contato[0]
        email_details = contact.get("email", None)
        if email_details is None:
            return None
        if len(email_details) < 1:
            return None
        else:
            email = email_details[0]
            return email

    df["email"] = [get_email(orgao["contato"]) for orgao in filtered_data]

    # the main data source has only the municipality code, not their
    # names. So we go to IBGE to get the corresponding name.
    print(f"Fetching municipality codes data from {URL_MUNICIPIOS}...")
    municipios_response = session.get(URL_MUNICIPIOS)
    municipios_data = municipios_response.json()

    municipios_map = {
        int(municipio["id"]): municipio["nome"] for municipio in municipios_data
    }

    # the main data source has only the country code, not their names.
    # So we go to the SISCOMEX (foreign trade) data to get country
    # names in English.
    print(f"Fetching country codes data from {URL_PAISES}...")
    paises_response = session.get(URL_PAISES, verify=False)
    paises_df = pd.read_csv(
        io.StringIO(paises_response.text), delimiter=";", encoding="iso-8859-1"
    )

    country_map = {
        row[1]["CO_PAIS"]: row[1]["NO_PAIS_ING"] for row in paises_df.iterrows()
    }
    country_map[1058] = "Brazil"  # set manually as the dataset does not have it

    # build the address string from several parts
    def get_address(endereco: list) -> str:
        "Retorna o endereço físico."
        if len(endereco) < 1:
            return None
        addresses = [
            address for address in endereco if address["tipoEndereco"] == "Principal"
        ]
        if len(addresses) < 1:  # if there is no main address,
            address = endereco[0]  # get the first available address
        else:
            address = addresses[0]  # get the first main address
        address_str = address["logradouro"]
        if address.get("numero", None) is not None:
            address_str += ", " + str(address["numero"])
        if address.get("complemento", None) is not None:
            address_str += ", " + address["complemento"]
        if address.get("bairro", None) is not None:
            address_str += "\n" + address["bairro"]
        address_str += "\n"
        if address.get("cep", None) is not None:
            address_str += str(address["cep"]) + " "
        address_str += municipios_map[address["municipio"]] + ", " + address["uf"]
        address_str += (
            "\n"
            + country_map[address.get("pais", None) or 1058]  # default to Brazil (1058)
        )
        return address_str

    df["address"] = [get_address(orgao["endereco"]) for orgao in filtered_data]

    # get and change the formatting of phone numbers
    def get_phones(contato: list) -> str:
        "Retorna o e-mail institucional."
        if len(contato) < 1:
            return None
        contact = contato[0]
        phone_details = contact.get("telefone", None)
        if phone_details is None:
            return None
        if len(phone_details) < 1:
            return None
        else:
            phone = ", ".join(
                [
                    "+" + " ".join(phone_re.match(phone_detail).groups())
                    for phone_detail in phone_details
                ]
            )
            return phone

    df["phone"] = [get_phones(orgao["contato"]) for orgao in filtered_data]

    # this attribute has some useful properties. For lack of a better
    # field, we create tags out of them.
    print(f"Fetching snj data from {URL_SUBNATUREZAJURIDICA}...")
    snj_response = session.get(URL_SUBNATUREZAJURIDICA)
    snj_data = snj_response.json()

    snj_map = {
        snj["codigoSubNaturezaJuridica"]: snj["descricaoSubNaturezaJuridica"]
        for snj in snj_data["subNaturezaJuridica"]
        if snj["ativo"] == "SIM"
    }

    df["tags"] = [
        (
            slugify(snj_map[int(orgao["codigoSubNaturezaJuridica"].split("/")[-1])])
            if orgao.get("codigoSubNaturezaJuridica", None) is not None
            else None
        )
        for orgao in filtered_data
    ]

    # the ID is a URI that responds with data about that entity, so we
    # can use it also as a source URL
    df["source_url"] = [orgao["codigoUnidade"] for orgao in filtered_data]

    df.to_csv(output, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        help="filename for the data output as CSV",
        metavar="file_name",
        default="br.csv",
    )
    args = parser.parse_args()

    import_br_data(URL, args.output)
