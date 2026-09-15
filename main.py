import requests
import feedparser
from datetime import datetime

PALAVRAS_CHAVE = [
    "petrobras",
    "axia",
    "vale"
]

FONTES = {
    "Globo": "https://g1.globo.com/rss/g1/",
    "Valor": "https://valor.globo.com/rss/valor",
    "Estadão": "https://www.estadao.com.br/arc/outboundfeeds/feeds/rss/sections/geral/"
}


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

        noticias_encontradas = []

        for noticia in feed.entries:
            titulo = noticia.get("title", "")
            link = noticia.get("link", "")

            texto = titulo.lower()

            if any(palavra in texto for palavra in PALAVRAS_CHAVE):
                noticias_encontradas.append({
                    "fonte": nome_fonte,
                    "titulo": titulo,
                    "link": link
                })

        return noticias_encontradas

    except Exception as erro:
        print(f"❌ Erro em {nome_fonte}: {erro}")
        return []


def main():
    print("=" * 60)
    print("       MONITOR DE NOTÍCIAS")
    print("=" * 60)

    print("\nPalavras monitoradas:")
    print("• Petrobras")
    print("• Axia")
    print("• Vale")

    print(f"\nConsulta iniciada em: {datetime.now():%d/%m/%Y %H:%M:%S}")

    todas_noticias = []

    for nome, url in FONTES.items():
        noticias = buscar_noticias(nome, url)
        todas_noticias.extend(noticias)

    print("\n" + "=" * 60)
    print("RESULTADOS")
    print("=" * 60)

    if not todas_noticias:
        print("\nNenhuma notícia encontrada.")
        return

    for noticia in todas_noticias:
        print(f"\n📰 {noticia['fonte']}")
        print(f"   {noticia['titulo']}")
        print(f"   {noticia['link']}")

    print("\n" + "=" * 60)
    print(f"Total encontrado: {len(todas_noticias)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
