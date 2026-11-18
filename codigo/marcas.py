"""
Descobre a marca de cada anúncio e monta o ranking de marcas por setor.

ATENÇÃO: o ranking é uma ESTIMATIVA de popularidade, baseada em
quantas vezes a marca aparece no Google Shopping e quantas avaliações
os anúncios dela somam. NÃO é o volume real de vendas.
"""
from collections import defaultdict

from . import config
from .texto import normalizar, posicao_termo

# Marcas mais compridas primeiro ("Royal Canin" antes de "Royal", "Pro Plan" antes de "Purina")
_MARCAS = sorted(config.MARCAS_CONHECIDAS, key=len, reverse=True)
# Nomes iguais escritos de jeitos diferentes
_APELIDOS = {"Fórmula Natural": "Formula Natural", "GranPlus": "Gran Plus"}


def descobrir_marca(titulo: str) -> str:
    t = normalizar(titulo)
    # Se aparecer mais de uma marca conhecida, vale a que vem primeiro no título.
    # Fabricantes (ex.: "Premier Pet Golden") perdem para a marca do produto (Golden).
    encontradas = []
    for marca in _MARCAS:
        posicao = posicao_termo(t, normalizar(marca))
        if posicao >= 0:
            eh_fabricante = marca in config.FABRICANTES
            encontradas.append((eh_fabricante, posicao, -len(marca), marca))
    if encontradas:
        marca = min(encontradas)[3]
        return _APELIDOS.get(marca, marca)
    # Não reconheceu: usa a primeira palavra "de verdade" do título
    for palavra in titulo.split():
        limpa = palavra.strip(" -–,.:()[]").lower()
        if len(limpa) > 2 and limpa not in config.PALAVRAS_GENERICAS and not limpa[0].isdigit():
            return palavra.strip(" -–,.:()[]").capitalize()
    return "Outras"


def ranking_por_setor(anuncios: list[dict]) -> dict:
    """Recebe anúncios (das pesquisas mais recentes) e devolve, por setor:
    [{marca, aparicoes, avaliacoes}], do mais popular para o menos."""
    contagem = defaultdict(lambda: defaultdict(lambda: {"aparicoes": 0, "avaliacoes": 0}))
    for a in anuncios:
        item = contagem[a["categoria"]][a["marca"]]
        item["aparicoes"] += 1
        item["avaliacoes"] += a["avaliacoes"]

    resultado = {}
    for setor, marcas in contagem.items():
        lista = [{"marca": m, **v} for m, v in marcas.items() if m != "Outras"]
        # Ordem: mais avaliações somadas; empate -> quem aparece mais
        lista.sort(key=lambda x: (x["avaliacoes"], x["aparicoes"]), reverse=True)
        resultado[setor] = lista
    return resultado
