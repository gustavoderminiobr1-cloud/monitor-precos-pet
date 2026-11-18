"""
Filtro de resultados: tira anúncios que não são o produto certo.

Regra:
- o título precisa ter TODAS as palavras obrigatórias;
- o título não pode ter NENHUMA palavra proibida.
"""
from .texto import contem_termo, normalizar


def motivo_descarte(titulo: str, obrigatorias: list, proibidas: list) -> str:
    """Devolve '' se o anúncio passou, ou o motivo de ter sido descartado."""
    t = normalizar(titulo)
    for palavra in obrigatorias:
        if not contem_termo(t, palavra):
            return f"falta '{palavra}'"
    for palavra in proibidas:
        if contem_termo(t, palavra):
            return f"tem '{palavra}'"
    return ""
