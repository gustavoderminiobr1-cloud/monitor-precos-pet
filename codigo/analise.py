"""
Junta tudo num resumo pronto para o painel e para a planilha:
- menor, maior e média de preço de cada produto (só anúncios aprovados no filtro);
- semáforo comparando com meu_preco;
- seta de tendência comparando com a pesquisa anterior;
- pódio de marcas por setor.
"""
from collections import defaultdict
from datetime import date

from . import config
from .marcas import ranking_por_setor

ICONE_ANIMAL = {"Cão": "🐶", "Gato": "🐱", "Outros": "🐾"}
ICONE_IDADE = {"Filhote": "🍼", "Adulto": "💪", "Idoso": "👴"}
ORDEM_SUBGRUPO = ["Cão · Filhote", "Cão · Adulto", "Cão · Idoso", "Cão",
                  "Gato · Filhote", "Gato · Adulto", "Gato · Idoso", "Gato"]


def _data_br(iso: str) -> str:
    return date.fromisoformat(iso).strftime("%d/%m/%Y")


def _sinal(meu_preco, media):
    """verde: igual ou abaixo da média | amarelo: até 10% acima | vermelho: mais de 10% acima"""
    if meu_preco is None or not media:
        return "", None
    diferenca = (meu_preco - media) / media
    if diferenca <= 0:
        return "verde", diferenca
    if diferenca <= config.TOLERANCIA_AMARELO:
        return "amarelo", diferenca
    return "vermelho", diferenca


def _tendencia(atual, anterior):
    if atual is None or anterior is None:
        return ""
    variacao = (atual - anterior) / anterior
    if variacao > config.VARIACAO_MINIMA_SETA:
        return "subiu"
    if variacao < -config.VARIACAO_MINIMA_SETA:
        return "caiu"
    return "igual"


def _icones_subgrupo(subgrupo: str) -> str:
    partes = [p.strip() for p in subgrupo.split("·")]
    icone = ICONE_ANIMAL.get(partes[0], "🐾")
    if len(partes) > 1:
        icone += ICONE_IDADE.get(partes[1], "")
    return icone


def montar_resumo(produtos, anuncios_historico, aviso="", contador=None, atualizado=""):
    # Agrupa o histórico: produto -> data -> anúncios
    por_produto = defaultdict(lambda: defaultdict(list))
    for a in anuncios_historico:
        por_produto[a["nome_busca"]][a["data"]].append(a)

    resumo_produtos = []
    anuncios_recentes = []  # para o ranking de marcas
    for p in produtos:
        datas = sorted(por_produto[p.nome_busca].keys())
        item = {
            "id": len(resumo_produtos),  # posição na lista (o painel usa para abrir a janela)
            "nome": p.nome_busca, "categoria": p.categoria, "subgrupo": p.subgrupo,
            "dia": p.dia, "meu_preco": p.meu_preco, "pesquisado": bool(datas),
        }
        if not datas:
            resumo_produtos.append(item)
            continue

        ultima = datas[-1]
        anuncios_recentes += por_produto[p.nome_busca][ultima]
        ofertas = sorted((a for a in por_produto[p.nome_busca][ultima] if a["passou_filtro"]),
                         key=lambda a: a["preco"])
        precos = [o["preco"] for o in ofertas]

        # Pesquisa anterior (semana passada, normalmente)
        menor_anterior, data_anterior = None, ""
        for d in reversed(datas[:-1]):
            anteriores = [a["preco"] for a in por_produto[p.nome_busca][d] if a["passou_filtro"]]
            if anteriores:
                menor_anterior, data_anterior = min(anteriores), d
                break

        menor = min(precos) if precos else None
        media = sum(precos) / len(precos) if precos else None
        sinal, diferenca = _sinal(p.meu_preco, media)
        imagem = next((o["imagem"] for o in ofertas if o["imagem"]), "")

        item.update({
            "data": _data_br(ultima),
            "menor": menor,
            "maior": max(precos) if precos else None,
            "media": media,
            "loja": ofertas[0]["loja"] if ofertas else "",
            "imagem": imagem,
            "sinal": sinal,
            "diferenca": diferenca,
            "menor_anterior": menor_anterior,
            "data_anterior": _data_br(data_anterior) if data_anterior else "",
            "tendencia": _tendencia(menor, menor_anterior),
            "ofertas": [{k: o[k] for k in ("titulo", "loja", "preco", "nota", "avaliacoes", "link", "imagem")}
                        for o in ofertas],
        })
        resumo_produtos.append(item)

    ranking = ranking_por_setor(anuncios_recentes)

    # Monta os setores na ordem do painel
    setores = []
    for chave, info in config.SETORES.items():
        do_setor = [x for x in resumo_produtos if x["categoria"] == chave]
        grupos = defaultdict(list)
        for x in do_setor:
            grupos[x["subgrupo"]].append(x)
        ordem = sorted(grupos, key=lambda g: ORDEM_SUBGRUPO.index(g) if g in ORDEM_SUBGRUPO else 99)
        setores.append({
            "chave": chave, **info,
            "total": len(do_setor),
            "subgrupos": [{"nome": g.replace(" · ", " "), "icone": _icones_subgrupo(g),
                           "produtos": grupos[g]} for g in ordem],
            "marcas": ranking.get(chave, []),
        })

    return {
        "atualizado": atualizado,
        "aviso": aviso,
        "contador": contador or {},
        "setores": setores,
        "produtos": resumo_produtos,
    }
