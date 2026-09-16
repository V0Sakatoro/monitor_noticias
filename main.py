import requests
import feedparser
import re
import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


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
        "vale"
    ]
}


def limpar_texto(texto):
    texto = texto.lower()
    texto = re.sub(r"<[^>]+>", " ", texto)
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()


def identificar_empresas(texto):
    encontradas = []

    texto = limpar_texto(texto)

    for empresa, palavras in EMPRESAS.items():

        for palavra in palavras:

            palavra = limpar_texto(palavra)

            padrao = rf"\b{re.escape(palavra)}\b"

            if re.search(padrao, texto):

                encontradas.append(empresa)
                break

    return encontradas


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

            titulo = noticia.get(
                "title",
                ""
            ).strip()

            descricao = (
                noticia.get("summary", "")
                or noticia.get("description", "")
            ).strip()

            link = noticia.get(
                "link",
                ""
            ).strip()

            texto = f"{titulo} {descricao}"

            empresas_encontradas = identificar_empresas(
                texto
            )

            if empresas_encontradas:

                noticias.append({
                    "fonte": nome_fonte,
                    "titulo": titulo,
                    "descricao": descricao,
                    "link": link,
                    "empresas": empresas_encontradas
                })

        print(
            f"✅ {nome_fonte}: "
            f"{len(noticias)} notícia(s) encontrada(s)"
        )

        return noticias

    except Exception as erro:

        print(
            f"❌ Erro em {nome_fonte}: {erro}"
        )

        return []


def criar_relatorio(noticias):

    agora = datetime.now().strftime(
        "%d/%m/%Y %H:%M"
    )

    html = f"""
    <html>

    <body style="
        font-family: Arial, sans-serif;
        background-color: #f5f5f5;
        padding: 20px;
    ">

        <div style="
            max-width: 800px;
            margin: auto;
            background: white;
            padding: 25px;
            border-radius: 10px;
        ">

            <h1>📰 Monitor de Notícias</h1>

            <p>
                <strong>Data da consulta:</strong>
                {agora}
            </p>

            <hr>
    """

    empresas = [
        "Petrobras",
        "Axia",
        "Vale"
    ]

    for empresa in empresas:

        html += f"""
            <h2>{empresa}</h2>
        """

        noticias_empresa = [
            noticia
            for noticia in noticias
            if empresa in noticia["empresas"]
        ]

        if not noticias_empresa:

            html += """
                <p>Nenhuma notícia encontrada.</p>
            """

            continue

        for noticia in noticias_empresa:

            descricao = limpar_texto(
                noticia["descricao"]
            )

            if len(descricao) > 500:

                descricao = (
                    descricao[:500]
                    + "..."
                )

            html += f"""
                <div style="
                    margin-bottom: 25px;
                    padding: 15px;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                ">

                    <p>
                        <strong>Fonte:</strong>
                        {noticia["fonte"]}
                    </p>

                    <h3>
                        {noticia["titulo"]}
                    </h3>

                    <p>
                        {descricao}
                    </p>

                    <p>
                        <a href="{noticia["link"]}">
                            🔗 Ler notícia
                        </a>
                    </p>

                </div>
            """

    html += f"""
            <hr>

            <p>
                Total de notícias encontradas:
                <strong>{len(noticias)}</strong>
            </p>

            <p style="color: #777;">
                Relatório enviado automaticamente
                pelo Monitor de Notícias.
            </p>

        </div>

    </body>

    </html>
    """

    return html


def enviar_email(noticias):

    remetente = os.getenv(
        "EMAIL_REMETENTE"
    )

    destinatario = os.getenv(
        "EMAIL_DESTINO"
    )

    senha = os.getenv(
        "EMAIL_SENHA"
    )

    if not remetente or not destinatario or not senha:

        print(
            "❌ Variáveis de e-mail não configuradas."
        )

        return

    relatorio = criar_relatorio(
        noticias
    )

    mensagem = MIMEMultipart(
        "alternative"
    )

    mensagem["Subject"] = (
        "📰 Monitor de Notícias - "
        f"{datetime.now():%d/%m/%Y}"
    )

    mensagem["From"] = remetente

    mensagem["To"] = destinatario

    mensagem.attach(
        MIMEText(
            relatorio,
            "html",
            "utf-8"
        )
    )

    try:

        print(
            "\n📧 Enviando relatório por e-mail..."
        )

        with smtplib.SMTP_SSL(
            "smtp.gmail.com",
            465
        ) as servidor:

            servidor.login(
                remetente,
                senha
            )

            servidor.sendmail(
                remetente,
                destinatario,
                mensagem.as_string()
            )

        print(
            "✅ E-mail enviado com sucesso!"
        )

    except Exception as erro:

        print(
            f"❌ Erro ao enviar e-mail: {erro}"
        )


def main():

    print("=" * 70)

    print(
        "             MONITOR DE NOTÍCIAS"
    )

    print("=" * 70)

    print(
        "\nPalavras monitoradas:"
    )

    print("• Petrobras")
    print("• Axia")
    print("• Vale")

    print(
        f"\nConsulta iniciada em: "
        f"{datetime.now():%d/%m/%Y %H:%M:%S}"
    )

    todas_noticias = []

    for nome, url in FONTES.items():

        noticias = buscar_noticias(
            nome,
            url
        )

        todas_noticias.extend(
            noticias
        )

    noticias_unicas = []

    links_processados = set()

    for noticia in todas_noticias:

        link = noticia["link"]

        if link not in links_processados:

            links_processados.add(
                link
            )

            noticias_unicas.append(
                noticia
            )

    print("\n" + "=" * 70)

    print(
        f"TOTAL: "
        f"{len(noticias_unicas)} notícia(s)"
    )

    print("=" * 70)

    enviar_email(
        noticias_unicas
    )


if __name__ == "__main__":
    main()
