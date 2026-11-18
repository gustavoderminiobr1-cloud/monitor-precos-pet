"""
Histórico de pesquisas.

Dois arquivos (abrem no Excel):
- historico.csv: cada anúncio encontrado, com a data. É daqui que saem
  o painel, a planilha e a comparação semana a semana.
- pesquisas-feitas.csv: uma linha por pesquisa (data, produto, quantos
  anúncios vieram). Serve para nunca repetir o mesmo produto no mesmo dia.
"""
import csv

CAMPOS_HISTORICO = ["data", "nome_busca", "categoria", "titulo", "loja", "preco",
                    "nota", "avaliacoes", "marca", "passou_filtro", "motivo",
                    "link", "imagem"]
CAMPOS_PESQUISAS = ["data", "nome_busca", "anuncios", "aprovados", "situacao"]


def _ler(arquivo) -> list[dict]:
    if not arquivo.exists():
        return []
    with open(arquivo, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


def _acrescentar(arquivo, campos, linhas: list[dict]):
    novo = not arquivo.exists()
    with open(arquivo, "a", encoding="utf-8-sig" if novo else "utf-8", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=campos, delimiter=";", extrasaction="ignore")
        if novo:
            escritor.writeheader()
        escritor.writerows(linhas)


class Historico:
    def __init__(self, pastas):
        self.pastas = pastas

    # ---------- pesquisas feitas ----------
    def ja_pesquisado(self, data: str, nome_busca: str) -> bool:
        return any(l["data"] == data and l["nome_busca"] == nome_busca
                   for l in _ler(self.pastas.pesquisas_feitas))

    def registrar_pesquisa(self, data, nome_busca, anuncios, aprovados, situacao):
        _acrescentar(self.pastas.pesquisas_feitas, CAMPOS_PESQUISAS, [{
            "data": data, "nome_busca": nome_busca, "anuncios": anuncios,
            "aprovados": aprovados, "situacao": situacao}])

    # ---------- anúncios ----------
    def salvar_anuncios(self, linhas: list[dict]):
        _acrescentar(self.pastas.historico, CAMPOS_HISTORICO, linhas)

    def todos(self) -> list[dict]:
        """Todos os anúncios já salvos, com números já convertidos."""
        linhas = _ler(self.pastas.historico)
        for l in linhas:
            l["preco"] = float(l["preco"])
            l["avaliacoes"] = int(l["avaliacoes"] or 0)
            l["nota"] = float(l["nota"]) if l.get("nota") else None
            l["passou_filtro"] = l["passou_filtro"] == "sim"
        return linhas

    def todas_pesquisas(self) -> list[dict]:
        return _ler(self.pastas.pesquisas_feitas)
