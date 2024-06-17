import json
import os
import unicodedata
import requests
from bs4 import BeautifulSoup

DATA_PATH = os.path.join(os.path.dirname(__file__), 'data')
CIDADES_CANONICAS_JSON = os.path.join(DATA_PATH, 'cidades_canonicas.json')
BAIRROS_PATH = os.path.join(DATA_PATH, 'bairros_por_estado')

URL_BASE_IBGE = 'https://servicodados.ibge.gov.br/api/v1/localidades/municipios'
URL_BASE_RUACEP = 'https://www.ruacep.com.br'

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
}

def obter_nomes_municipios():
    response = requests.get(URL_BASE_IBGE)
    data = response.json()
    return [{"id": item['id'], "nome": item['nome'], "estado": item['microrregiao']['mesorregiao']['UF']['sigla'].lower()} for item in data]

def normalizar_nome(nome):
    nome_normalizado = unicodedata.normalize('NFKD', nome.lower()).encode('ASCII', 'ignore').decode('utf-8')
    return nome_normalizado.replace(" ", "-")

def criar_dicionario_cidades(nomes_municipios):
    return {normalizar_nome(cidade["nome"]): {"id": cidade["id"], "nome": cidade["nome"], "estado": cidade["estado"]} for cidade in nomes_municipios}

def salvar_dicionario_cidades(dicionario_cidades, arquivo_saida):
    with open(arquivo_saida, 'w', encoding='utf-8') as f:
        json.dump(dicionario_cidades, f, ensure_ascii=False, indent=4)

def get_bairros(cidade, estado, headers):
    bairros = []
    base_url = f"{URL_BASE_RUACEP}/{estado}/{normalizar_nome(cidade)}/bairros/"
    
    with requests.Session() as session:
        for pagina in range(1, 2000):
            url_paginacao = f"{base_url}{pagina}/"
            site = session.get(url_paginacao, headers=headers)
            if site.status_code != 200:
                break
            soup = BeautifulSoup(site.content, "html.parser")
            bairro_divs = soup.find_all("div", class_="card-header")

            if not bairro_divs:
                break

            for bairro in bairro_divs:
                nome_bairro = bairro.find("strong").text.strip()
                bairros.append(nome_bairro)

            print(f"Página {pagina} de {cidade} concluída.")
    
    return bairros

def main():
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)
    
    nomes_municipios = obter_nomes_municipios()
    dicionario_cidades = criar_dicionario_cidades(nomes_municipios)
    salvar_dicionario_cidades(dicionario_cidades, CIDADES_CANONICAS_JSON)
    
    bairros_por_estado = {}

    for cidade_info in nomes_municipios:
        cidade_id = cidade_info["id"]
        cidade = cidade_info["nome"]
        estado = cidade_info["estado"]
        print(f"Scraping bairros de {cidade}, {estado}")
        bairros = get_bairros(cidade, estado, HEADERS)

        if estado not in bairros_por_estado:
            bairros_por_estado[estado] = {}
        
        bairros_por_estado[estado][cidade_id] = {
            "nome": cidade,
            "bairros": bairros
        }

    if not os.path.exists(BAIRROS_PATH):
        os.makedirs(BAIRROS_PATH)

    for estado, cidades_bairros in bairros_por_estado.items():
        estado_filename = os.path.join(BAIRROS_PATH, f'bairros_{estado}.json')
        with open(estado_filename, 'w', encoding='utf-8') as f:
            json.dump(cidades_bairros, f, ensure_ascii=False, indent=4)

    print("Scraping concluído e dados salvos por estado.")

if __name__ == "__main__":
    main()