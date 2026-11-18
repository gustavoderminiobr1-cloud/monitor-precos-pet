"""
Contador mensal de pesquisas da SerpAPI.

Fica salvo em contador.json, assim:
    {"mes": "2026-11", "pesquisas": 12}

Quando o mês vira, o contador volta para zero sozinho.
Ao chegar no limite (230), a ferramenta para de pesquisar.
"""
import json

from . import config


class Contador:
    def __init__(self, arquivo, mes_atual: str):
        self.arquivo = arquivo
        self.mes = mes_atual
        self.pesquisas = 0
        if arquivo.exists():
            dados = json.loads(arquivo.read_text(encoding="utf-8"))
            if dados.get("mes") == mes_atual:
                self.pesquisas = int(dados.get("pesquisas", 0))

    @property
    def restantes(self) -> int:
        return max(0, config.LIMITE_MENSAL - self.pesquisas)

    def pode_pesquisar(self) -> bool:
        return self.pesquisas < config.LIMITE_MENSAL

    def somar(self):
        """Soma 1 e salva na hora (se o programa cair, o número não se perde)."""
        self.pesquisas += 1
        self.salvar()

    def salvar(self):
        self.arquivo.write_text(
            json.dumps({"mes": self.mes, "pesquisas": self.pesquisas,
                        "limite": config.LIMITE_MENSAL}, indent=2),
            encoding="utf-8")
