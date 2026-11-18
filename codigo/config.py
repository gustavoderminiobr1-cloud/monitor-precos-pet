"""
Configurações gerais da ferramenta.
Se precisar mudar algum número (ex.: o limite de pesquisas), é aqui.
"""
from datetime import datetime, timedelta, timezone
from pathlib import Path

# ---------------------------------------------------------------
# Pastas
# ---------------------------------------------------------------
RAIZ = Path(__file__).resolve().parent.parent
ARQUIVO_PRODUTOS = RAIZ / "produtos.csv"
ARQUIVO_ENV = RAIZ / ".env"
PASTA_RESPOSTAS_TESTE = RAIZ / "dados" / "respostas-teste"


class Pastas:
    """Onde cada modo salva seus arquivos.
    O modo real usa dados/, docs/ e saida/.
    O modo teste usa a pasta teste/, para nunca misturar com dados reais."""

    def __init__(self, modo_teste: bool):
        if modo_teste:
            base = RAIZ / "teste"
            self.dados = base
            self.painel = base / "painel.html"
            self.planilha = base / "relatorio.xlsx"
        else:
            self.dados = RAIZ / "dados"
            self.painel = RAIZ / "docs" / "index.html"
            self.planilha = RAIZ / "saida" / "relatorio.xlsx"
        self.historico = self.dados / "historico.csv"
        self.pesquisas_feitas = self.dados / "pesquisas-feitas.csv"
        self.contador = self.dados / "contador.json"
        self.respostas_brutas = self.dados / "respostas"
        for p in (self.dados, self.painel.parent, self.planilha.parent, self.respostas_brutas):
            p.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------
# SerpAPI (Google Shopping, Brasil)
# ---------------------------------------------------------------
SERPAPI_URL = "https://serpapi.com/search.json"
SERPAPI_PARAMETROS = {
    "engine": "google_shopping",
    "gl": "br",
    "hl": "pt-br",
    "google_domain": "google.com.br",
    "location": "Brazil",
}

# ---------------------------------------------------------------
# Limite de custo
# O plano grátis tem 250 pesquisas/mês. Paramos em 230 por segurança.
# ---------------------------------------------------------------
LIMITE_MENSAL = 230

# ---------------------------------------------------------------
# Semáforo: quanto acima da média do mercado ainda é "amarelo"
# ---------------------------------------------------------------
TOLERANCIA_AMARELO = 0.10  # 10%

# Variação mínima para mostrar seta de tendência (1% = evita setas por centavos)
VARIACAO_MINIMA_SETA = 0.01

# ---------------------------------------------------------------
# Fuso horário de Brasília (o Brasil não tem mais horário de verão)
# ---------------------------------------------------------------
FUSO_BRASILIA = timezone(timedelta(hours=-3))


def agora():
    return datetime.now(FUSO_BRASILIA)


# Dias da semana como a pessoa escreve no produtos.csv (sem acento)
DIAS_DA_SEMANA = ["segunda", "terca", "quarta", "quinta", "sexta", "sabado", "domingo"]

# ---------------------------------------------------------------
# Setores do painel (ordem, ícone, cor)
# ---------------------------------------------------------------
SETORES = {
    "racao":      {"nome": "Ração",      "icone": "🍖", "cor": "#F59E0B"},
    "areia":      {"nome": "Areia",      "icone": "🪣", "cor": "#0EA5E9"},
    "antipulgas": {"nome": "Antipulgas", "icone": "🐜", "cor": "#10B981"},
    "remedios":   {"nome": "Remédios",   "icone": "💊", "cor": "#EF4444"},
    "gaiolas":    {"nome": "Gaiolas",    "icone": "🏠", "cor": "#8B5CF6"},
}

# ---------------------------------------------------------------
# Marcas conhecidas, para o ranking de marcas.
# Se uma marca não estiver aqui, a ferramenta tenta adivinhar pelo título.
# Pode acrescentar nomes à vontade (o mais comprido primeiro não importa).
# ---------------------------------------------------------------
MARCAS_CONHECIDAS = [
    # Rações
    "Golden", "Premier", "Royal Canin", "Pedigree", "Whiskas", "Pro Plan", "Purina",
    "Dog Chow", "Cat Chow", "Friskies", "Special Dog", "Special Cat", "Guabi Natural",
    "Biofresh", "Formula Natural", "Fórmula Natural", "Hill's", "N&D", "Farmina", "Quatree",
    "Magnus", "Gran Plus", "GranPlus", "Origens", "Three Dogs", "Three Cats", "Equilíbrio",
    "Max", "Kitekat", "Faro", "Baw Waw", "Foster", "Nutrilus", "Vitalcan",
    # Areias
    "Pipicat", "Viva Verde", "Chalesco", "Kelco", "Snow Cat", "Gatsy", "Sanicat",
    "Fofinho", "Cats Best", "American Pets", "Minecat",
    # Antipulgas e remédios
    "NexGard", "Bravecto", "Simparic", "Credeli", "Frontline", "Advocate", "Revolution",
    "Seresto", "Capstar", "Comfortis", "Advantage", "Effipro", "Apoquel", "Drontal",
    "Vermivet", "Milbemax",
    # Gaiolas
    "Jel Plast", "Savic", "Ferplast", "Furacão Pet", "MMA", "Pawise",
]

# Palavras que nunca são marca (usadas quando a marca não é reconhecida)
PALAVRAS_GENERICAS = {
    "racao", "ração", "areia", "sanitaria", "sanitária", "antipulgas", "anti", "pulgas",
    "kit", "combo", "para", "de", "do", "da", "com", "gato", "gatos", "cao", "cão", "caes",
    "cães", "cachorro", "cachorros", "gaiola", "remedio", "remédio", "comprimido",
    "comprimidos", "pet", "seca", "umida", "úmida", "petisco", "promoção", "oferta", "novo",
}

# Fabricantes que também aparecem no título junto da marca do produto.
# Quando aparecem junto de outra marca, a outra marca é que conta.
# Ex.: "Ração Premier Pet Golden Fórmula" -> marca Golden
FABRICANTES = {"Premier", "Purina"}
