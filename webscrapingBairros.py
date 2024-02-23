import requests
from bs4 import BeautifulSoup
import json
import os

# Número de paginas totais do site
paginas = 78
nomes_bairros = []

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
}

# URL já com filtro da cidade
base_url = "https://www.ruacep.com.br/mg/sao-joao-del-rei/bairros/"

print(f"Acessando: {base_url}")

with requests.Session() as session:
    for pagina in range(1, paginas + 1):
        urlPaginacao = f"{base_url}{pagina}/"
        site = session.get(urlPaginacao, headers=headers)
        soup = BeautifulSoup(site.content, "html.parser")

        bairros = soup.find_all("div", class_="card-header")

        for bairro in bairros:
            nome_bairro = bairro.find("strong").text.strip()
            nomes_bairros.append(nome_bairro)

        print(f"Página {pagina} concluída.")


diretorio_atual = os.path.dirname(os.path.realpath(__file__))
nome_arquivo_json = "nomes_bairros.json"
caminho_arquivo_json = os.path.join(diretorio_atual, nome_arquivo_json)

with open(caminho_arquivo_json, "w", encoding="utf-8") as arquivo_json:
    json.dump(nomes_bairros, arquivo_json, ensure_ascii=False)


print("Done!!!!!")
