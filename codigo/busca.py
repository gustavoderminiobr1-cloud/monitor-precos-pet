"""
Busca de preços.

- Modo REAL: chama a SerpAPI (Google Shopping Brasil). Cada chamada gasta 1 pesquisa.
- Modo TESTE: lê uma resposta salva em arquivo JSON. Não gasta nada.

Nos dois casos o resultado sai no mesmo formato, então o resto da
ferramenta não precisa saber de onde veio.
"""
import json
import os
import urllib.error
import urllib.parse
import urllib.request

from . import config
from .texto import ler_preco, slug


class ErroBusca(Exception):
    pass


def carregar_chave() -> str:
    """Pega a chave SERPAPI_KEY do ambiente (GitHub) ou do arquivo .env (computador)."""
    chave = os.environ.get("SERPAPI_KEY", "").strip()
    if not chave and config.ARQUIVO_ENV.exists():
        for linha in config.ARQUIVO_ENV.read_text(encoding="utf-8-sig").splitlines():
            if linha.strip().startswith("SERPAPI_KEY"):
                chave = linha.split("=", 1)[1].strip().strip('"').strip("'")
    if not chave or chave == "cole_sua_chave_aqui":
        raise SystemExit(
            "ERRO: não encontrei a chave da SerpAPI.\n"
            "Abra o arquivo .env e coloque: SERPAPI_KEY=sua_chave")
    return chave


def buscar_real(termo: str, chave: str) -> dict:
    """Faz UMA pesquisa na SerpAPI e devolve a resposta completa."""
    parametros = dict(config.SERPAPI_PARAMETROS, q=termo, api_key=chave)
    url = config.SERPAPI_URL + "?" + urllib.parse.urlencode(parametros)
    try:
        with urllib.request.urlopen(url, timeout=60) as resp:
            dados = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        corpo = e.read().decode("utf-8", "ignore")[:300]
        raise ErroBusca(f"SerpAPI respondeu erro {e.code}: {corpo}") from e
    except urllib.error.URLError as e:
        raise ErroBusca(f"Sem conexão com a SerpAPI: {e.reason}") from e
    if dados.get("error"):
        # "Google hasn't returned any results" não é erro grave: só veio vazio
        if "hasn't returned any results" in dados["error"]:
            return dados
        raise ErroBusca(f"SerpAPI: {dados['error']}")
    return dados


def buscar_teste(termo: str, subpasta: str = "") -> dict:
    """Lê a resposta salva em dados/respostas-teste/<nome-do-produto>.json"""
    pasta = config.PASTA_RESPOSTAS_TESTE / subpasta if subpasta else config.PASTA_RESPOSTAS_TESTE
    arquivo = pasta / f"{slug(termo)}.json"
    if not arquivo.exists():
        raise ErroBusca(f"Modo teste: não existe o arquivo {arquivo.name} em {pasta}")
    return json.loads(arquivo.read_text(encoding="utf-8"))


def extrair_anuncios(resposta: dict) -> list[dict]:
    """Pega os anúncios da resposta da SerpAPI e deixa só o que interessa."""
    brutos = list(resposta.get("shopping_results") or [])
    brutos += resposta.get("inline_shopping_results") or []
    for grupo in resposta.get("categorized_shopping_results") or []:
        brutos += grupo.get("shopping_results") or []

    anuncios, vistos = [], set()
    for r in brutos:
        preco = r.get("extracted_price")
        if preco is None:
            preco = ler_preco(r.get("price"))
        titulo = (r.get("title") or "").strip()
        if not titulo or preco is None:
            continue
        loja = (r.get("source") or "").strip()
        chave = (titulo.lower(), loja.lower(), preco)
        if chave in vistos:  # o Google às vezes repete o mesmo anúncio
            continue
        vistos.add(chave)
        anuncios.append({
            "titulo": titulo,
            "loja": loja,
            "preco": float(preco),
            "nota": r.get("rating"),
            "avaliacoes": int(r.get("reviews") or 0),
            # "link" vai direto para a loja; "product_link" vai para a página do Google
            "link": r.get("link") or r.get("product_link") or "",
            "imagem": r.get("thumbnail") or "",
        })
    return anuncios
