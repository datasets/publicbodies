"""Imports Brazilian public body data from the official source and
complements it with data from several auxiliary sources.

Official source: [SIORG's open data API](https://dados.gov.br/dataset/siorg)
"""

# dependencies
# standard library
import io, re
from urllib.parse import urlparse

# packages
import requests
import pandas as pd
from slugify import slugify

# data sources
# official source
URL = 'http://estruturaorganizacional.dados.gov.br/doc/orgao-entidade/completa.json'
URL_CATEGORIAS = 'http://estruturaorganizacional.dados.gov.br/doc/categoria-unidade'
URL_NATUREZAJURIDICA = 'http://estruturaorganizacional.dados.gov.br/doc/natureza-juridica'
URL_SUBNATUREZAJURIDICA = 'http://estruturaorganizacional.dados.gov.br/doc/subnatureza-juridica'

# auxiliary sources
URL_OLD_FILE = 'https://github.com/okfn/publicbodies/raw/c7466bbfad3169e573b6e7f2ff92a3861bfda82a/data/br.csv'
URL_MUNICIPIOS = 'https://servicodados.ibge.gov.br/api/v1/localidades/municipios'
URL_PAISES = 'https://balanca.economia.gov.br/balanca/bd/tabelas/PAIS.csv'
URL_IMAGES = 'https://dados.gov.br/api/3/action/organization_list?all_fields=1&include_extras=1'

# regular expressions
phone_re = re.compile(r'(?:\((\d{1,3})\)\s*)?(?:\((\d{1,2})\)\s)?([0-9- ]{7,9})')

def import_br_data(url: str, output: str):
    "Imports data from the SIORG open data API on the given URL."

    # get the json data on the public bodies
    response = requests.get(url)
    data = response.json()

    # filter data to get only federal level and executive branch
    base_id = 'estruturaorganizacional.dados.gov.br/id/'
    filtered_data = [
    unidade for unidade in data['unidades'] \
    if unidade['codigoEsfera'].split('://')[-1] == f'{base_id}esfera/1' and \
        unidade['codigoPoder'].split('://')[-1] == f'{base_id}poder/1'
    ]

    # get the old data for filling some missing values
    br_old = pd.read_csv(URL_OLD_FILE)

    # add the 'phone' column, which didn't exist at the time
    columns = list(br_old.columns)
    columns.insert(columns.index('email'), 'phone')

    df = pd.DataFrame(columns=columns)
    df['id'] = [
        '/'.join(('br', slugify(orgao['nome'])))
        for orgao in filtered_data
    ]
    df['name'] = [orgao['nome'] for orgao in filtered_data]
    df['abbreviation'] = [orgao['sigla'] for orgao in filtered_data]
    df['description'] = [
        orgao['finalidade']
        if orgao.get('finalidade', None) else orgao['competencia']
        for orgao in filtered_data
    ]

    natureza_juridica_response = requests.get(URL_NATUREZAJURIDICA)
    natureza_juridica_data = natureza_juridica_response.json()
    natureza_juridica_map = {
        natureza_juridica['codigoNaturezaJuridica']:
            natureza_juridica['descricaoNaturezaJuridica']
        for natureza_juridica in natureza_juridica_data['naturezaJuridica']
        if natureza_juridica['ativo'] == 'SIM'
    }

    categorias_response = requests.get(URL_CATEGORIAS)
    categorias_data = categorias_response.json()
    category_map = {
        categoria['codigoCategoriaUnidade']:
            categoria['descricaoCategoriaUnidade']
        for categoria in categorias_data['categoriaUnidade']
        if categoria['ativo'] == 'SIM'
    }

    def get_category(code: str, nj: str) -> str:
        "Retorna a categoria do órgão com base no código."
        category = category_map[int(code.split('/')[-1])]
        if category == 'Vinculado':
            category += f' ({natureza_juridica_map[int(nj.split("/")[-1])]})'
        return category
    
    df['classification'] = [
        get_category(
            orgao['codigoCategoriaUnidade'],
            orgao['codigoNaturezaJuridica']
        )
        for orgao in filtered_data \
    ]

    code_map = {
        orgao['codigoUnidade']: orgao['nome'] \
            for orgao in data['unidades']
    }

    df['parent_id'] = [
        (
            '/'.join(('br', slugify(code_map[orgao['codigoUnidadePai']])))
            if orgao['codigoUnidadePai'].split('/')[-1] not in (
                '208615', # poder executivo
                '208613', # poder executivo
                '244320', # poder legislativo
                '244321', # poder judiciário
                '244322', # funções essenciais à justiça
                '94', # comando do exército
                '185', # comando da marinha
                '48', # comando da aeronáutica
            )
            else None
        )  for orgao in filtered_data
    ]

    images_response = requests.get(URL_IMAGES)
    images_data = images_response.json()

    image_map = {
        int(extra['value']): organization['image_display_url']
        
        for organization in images_data['result']
        if len(organization.get('extras', '')) > 0
            for extra in organization['extras']
            if extra['key'].lower() == 'siorg'
    }

    df['image'] = [
        image_map.get(int(orgao['codigoUnidade'].split('/')[-1]), None)
        for orgao in filtered_data
    ]

    def get_site_url(contato: list) -> str:
        "Retorna a URL do site institucional."
        if len(contato) < 1:
            return None
        contact = contato[0]
        site_details = contact.get('site', None)
        if site_details is None:
            return None
        sites = [
            site
            for site in site_details
            if site['tipo'] == 'Site Institucional'
        ]
        if len (sites) < 1:
            return None
        else:
            url = sites[0]['site']
            url = url.strip()
            parsed = urlparse(url)
            if not parsed.scheme:
                url = f'https://{url}'
            else:
                url = parsed.geturl()
            return url

    df['url'] = [
        get_site_url(orgao['contato'])
        for orgao in filtered_data
    ]

    missing_url = (
        df[df.url.isna()]
        .reset_index()
        .merge(br_old.loc[:,['abbreviation', 'url']], on='abbreviation')
        .set_index('index')
        .rename(columns={'url_y':'url'})
        .loc[:,['abbreviation', 'url']]
    )
    df.update(missing_url.url)

    df['jurisdiction_code'] = [
        'BR'
        for orgao in filtered_data
    ]

    def get_email(contato: list) -> str:
        "Retorna o e-mail institucional."
        if len(contato) < 1:
            return None
        contact = contato[0]
        email_details = contact.get('email', None)
        if email_details is None:
            return None
        if len (email_details) < 1:
            return None
        else:
            email = email_details[0]
            return email

    df['email'] = [
        get_email(orgao['contato'])
        for orgao in filtered_data
    ]

    municipios_response = requests.get(URL_MUNICIPIOS)
    municipios_data = municipios_response.json()

    municipios_map = {
        municipio['id']: municipio['nome']
        for municipio in municipios_data
    }

    paises_response = requests.get(URL_PAISES, verify=False)
    paises_df = pd.read_csv(
        io.StringIO(paises_response.text),
        delimiter=';',
        encoding='iso-8859-1'
    )

    country_map = {
        row[1]['CO_PAIS']: row[1]['NO_PAIS_ING']
        for row in paises_df.iterrows()
    }
    country_map[1058] = 'Brazil'

    def get_address(endereco: list) -> str:
        "Retorna o endereço físico."
        if len(endereco) < 1:
            return None
        addresses = [
            address
            for address in endereco
            if address['tipoEndereco'] == 'Principal'
        ]
        if len(addresses) < 1: # se não houver endereço principal,
            address = endereco[0] # pega o primeiro endereço disponível
        else: # caso contrário,
            address = addresses[0] # pega o primeiro endereço principal
        address_str = address['logradouro']
        if address.get('numero', None) is not None:
            address_str += ', ' + str(address['numero'])
        if address.get('complemento', None) is not None:
            address_str += ', ' + address['complemento']
        if address.get('bairro', None) is not None:
            address_str += '\n' + address['bairro']
        address_str += '\n'
        if address.get('cep', None) is not None:
            address_str += str(address['cep']) + ' '
        address_str += (
            municipios_map[address['municipio']] +
            ', ' + address['uf']
        )
        address_str += '\n' + \
            country_map[
                address.get('pais', None) or
                1058 # default to Brazil (1058)
            ]
        return address_str

    df['address'] = [
        get_address(orgao['endereco'])
        for orgao in filtered_data
    ]

    def get_phones(contato: list) -> str:
        "Retorna o e-mail institucional."
        if len(contato) < 1:
            return None
        contact = contato[0]
        phone_details = contact.get('telefone', None)
        if phone_details is None:
            return None
        if len (phone_details) < 1:
            return None
        else:
            phone = ', '.join([
                '+' + ' '.join(phone_re.match(phone_detail).groups())
                for phone_detail in phone_details
            ])
            return phone

    df['phone'] = [
        get_phones(orgao['contato'])
        for orgao in filtered_data
    ]

    snj_response = requests.get(URL_SUBNATUREZAJURIDICA)
    snj_data = snj_response.json()

    snj_map = {
        snj['codigoSubNaturezaJuridica']:
            snj['descricaoSubNaturezaJuridica']
        for snj in snj_data['subNaturezaJuridica']
        if snj['ativo'] == 'SIM'
    }

    df['tags'] = [
        (
            slugify(snj_map[
                int(orgao['codigoSubNaturezaJuridica'].split('/')[-1])
            ])
            if orgao.get('codigoSubNaturezaJuridica', None) is not None
            else None
        )
        for orgao in filtered_data
    ]

    df['source_url'] = [
        orgao['codigoUnidade']
        for orgao in filtered_data
    ]

    df.to_csv(output, index=False)

if __name__ == '__main__':
    import_br_data(URL, 'br.csv')