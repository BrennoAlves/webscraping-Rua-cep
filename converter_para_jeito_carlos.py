import json
import os

def converter_dados(arquivo_entrada, arquivo_saida):

    with open(arquivo_entrada, 'r', encoding='utf-8') as f:
        dados_estado = json.load(f)

    dados_convertidos = []
    for cidade_id, cidade_info in dados_estado.items():
        for bairro in cidade_info['bairros']:
            dados_convertidos.append({
                "idCidade": int(cidade_id),
                "nome": bairro
            })

    with open(arquivo_saida, 'w', encoding='utf-8') as f:
        json.dump(dados_convertidos, f, ensure_ascii=False, indent=4)

def main():

    diretorio_bairros = os.path.join(os.path.dirname(__file__), 'data', 'bairros_por_estado')

    for filename in os.listdir(diretorio_bairros):
        if filename.endswith('.json'):
            arquivo_entrada = os.path.join(diretorio_bairros, filename)
            arquivo_saida = os.path.join(diretorio_bairros, f'novo_{filename}')
            converter_dados(arquivo_entrada, arquivo_saida)
            print(f"Dados de {filename} convertidos para {arquivo_saida}")

if __name__ == "__main__":
    main()