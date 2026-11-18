"""
Gera o painel visual (uma página HTML única).
Pega o modelo painel-modelo.html e coloca os dados dentro dele.
"""
import json
from pathlib import Path

MODELO = Path(__file__).with_name("painel-modelo.html")


def gerar_painel(resumo: dict, arquivo, modo_teste: bool = False):
    dados = dict(resumo, modo_teste=modo_teste)
    texto_json = json.dumps(dados, ensure_ascii=False)
    texto_json = texto_json.replace("</", "<\\/")  # segurança: não deixa fechar a tag <script>
    html = MODELO.read_text(encoding="utf-8").replace("__DADOS__", texto_json)
    Path(arquivo).write_text(html, encoding="utf-8")
