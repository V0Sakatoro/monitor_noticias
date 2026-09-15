import requests
import feedparser
import re
from datetime import datetime


# ============================================================
# CONFIGURAÇÕES
# ============================================================

FONTES = {
    "Globo": "https://g1.globo.com/rss/g1/",
    "Valor": "https://valor.globo.com/rss/valor",
    "Estadão": "https://www.estadao.com.br/arc/outboundfeeds/feeds/rss/sections/geral/"
}


EMPRESAS = {
    "Petrobras": [
        "petrobras",
        "petrobrás"
    ],

    "Axia": [
        "axia",
        "axia energia"
    ],

    "Vale": [
        "vale s.a",
        "vale s/a",
        "vale sa",
        "companhia vale",
        "companhia vale do rio doce",
        "vale mineração",
        "vale mineracao"
    ]
}


# ============================================================
# BUSCA DAS NOTÍCIAS
# ============================================================

def buscar_noticias(nome_fonte, url):

    print(f"\n🔎 Consultando {nome_fonte}...")

    try:

        resposta = requests.get(
            url,
            timeout=15,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        resposta.raise_for_status()

        feed = feedparser.parse(resposta.content)

        noticias = []

        for noticia in feed.entries:

            titulo = noticia.get("title", "").strip()

            descricao = (
                noticia.get("summary", "")
                or noticia.get("description", "")
            ).strip()

            link = noticia.get("link", "").strip()

            # Junta título + descrição
            texto = f"{titulo} {descricao}".lower()

            empresas_encontradas = identificar_empresas(texto)

            if empresas_encontradas:

                noticias.append({
                    "fonte": nome_fonte,
                    "titulo": titulo,
                    "descricao": descricao,
                    "link": link,
                    "empresas": empresas_encontradas
                })

        return noticias

    except Exception as erro:

        print(f"❌ Erro em {nome_fonte}: {erro}")

        return []


# ============================================================
# IDENTIFICAÇÃO DAS EMPRESAS
# ============================================================

def identificar_empresas(texto):

    encontradas = []

    texto = limpar_texto(texto)

    for empresa, palavras in EMPRESAS.items():

        for palavra in palavras:

            palavra = limpar_texto(palavra)

            # Procura a expressão como palavra separada
            padrao = rf"\b{re.escape(palavra)}\b"

            if re.search(padrao, texto):

                # Tratamento especial para "Vale"
                if empresa == "Vale":

                    if vale_realmente_e_empresa(texto):
                        encontradas.append(empresa)
                        break

                else:

                    encontradas.append(empresa)
                    break

    return encontradas


# ============================================================
# LIMPEZA DO TEXTO
# ============================================================

def limpar_texto(texto):

    texto = texto.lower()

    # Remove HTML
    texto = re.sub(r"<[^>]+>", " ", texto)

    # Normaliza espaços
    texto = re.sub(r"\s+", " ", texto)

    return texto.strip()


# ============================================================
# FILTRO ESPECIAL DA VALE
# ============================================================

def vale_realmente_e_empresa(texto):

    termos_excluir = [

        "vale do aço",
        "vale do aco",
        "vale-pedágio",
        "vale pedágio",
        "vale-pedagio",
        "vale pedagio",
        "vale transporte",
        "vale-transporte",
        "vale alimentação",
        "vale alimentacao",
        "vale-refeição",
        "vale-refeicao",
        "vale presente",
        "vale-presente",
        "vale combustível",
        "vale combustivel"
    ]

    for termo in termos_excluir:

        if termo in texto:
            return False

    return True


# ============================================================
# EXIBIÇÃO DOS RESULTADOS
# ============================================================

def mostrar_resultados(noticias):

    print("\n" + "=" * 70)
    print("RESULTADOS")
    print("=" * 70)

    if not noticias:

        print("\nNenhuma notícia encontrada.")

        return


    empresas = [
        "Petrobras",
        "Axia",
        "Vale"
    ]


    for empresa in empresas:

        noticias_empresa = [
            noticia
            for noticia in noticias
            if empresa in noticia["empresas"]
        ]


        print("\n")
        print("=" * 70)
        print(f" {empresa.upper()}")
        print("=" * 70)


        if not noticias_empresa:

            print("\nNenhuma notícia encontrada.")

            continue


        for noticia in noticias_empresa:

            print(f"\n📰 {noticia['fonte']}")
            print(f"   {noticia['titulo']}")

            if noticia["descricao"]:

                descricao = limpar_texto(noticia["descricao"])

                # Limita o tamanho da descrição
                if len(descricao) > 300:
                    descricao = descricao[:300] + "..."

                print(f"\n   {descricao}")

            print(f"\n   🔗 {noticia['link']}")


    print("\n" + "=" * 70)

    print(
        f"Total de notícias encontradas: {len(noticias)}"
    )

    print("=" * 70)


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

def main():

    print("=" * 70)
    print("             MONITOR DE NOTÍCIAS")
    print("=" * 70)

    print("\nPalavras monitoradas:")

    print("• Petrobras")
    print("• Axia")
    print("• Vale")

    print(
        f"\nConsulta iniciada em: "
        f"{datetime.now():%d/%m/%Y %H:%M:%S}"
    )


    todas_noticias = []


    # Consulta todas as fontes

    for nome, url in FONTES.items():

        noticias = buscar_noticias(
            nome,
            url
        )

        todas_noticias.extend(noticias)


    # Remove notícias duplicadas

    noticias_unicas = []

    links_processados = set()


    for noticia in todas_noticias:

        link = noticia["link"]

        if link not in links_processados:

            links_processados.add(link)

            noticias_unicas.append(noticia)


    # Mostra resultados

    mostrar_resultados(noticias_unicas)


# ============================================================
# INÍCIO
# ============================================================

if __name__ == "__main__":

    main()
