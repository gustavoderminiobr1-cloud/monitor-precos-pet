"""
Pequenas funções para lidar com texto e preço.
"""
import re
import unicodedata


def sem_acento(texto: str) -> str:
    """'Ração Cães' -> 'Racao Caes'"""
    texto = unicodedata.normalize("NFKD", texto or "")
    return "".join(c for c in texto if not unicodedata.combining(c))


def normalizar(texto: str) -> str:
    """Deixa o texto num formato fácil de comparar:
    minúsculo, sem acento, e '15 kg' vira '15kg'."""
    t = sem_acento(texto).lower()
    t = re.sub(r"(\d)\s*(kg|mg|g|ml|l|un)\b", r"\1\2", t)  # 15 kg -> 15kg
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def separar_lista(celula: str) -> list[str]:
    """'light, senior ,filhote' -> ['light', 'senior', 'filhote']"""
    if not celula:
        return []
    return [normalizar(p) for p in re.split(r"[,;|]", celula) if p.strip()]


def posicao_termo(texto_normalizado: str, termo: str) -> int:
    """Onde o termo aparece no texto (-1 se não aparece).
    O termo precisa começar no início de uma palavra
    (assim 'adulto' encontra 'adultos', mas '4kg' não encontra '14kg')."""
    padrao = r"(?<![a-z0-9])" + re.escape(termo)
    if termo and termo[-1].isdigit():
        padrao += r"(?![0-9])"  # '10' não encontra '100'
    achado = re.search(padrao, texto_normalizado)
    return achado.start() if achado else -1


def contem_termo(texto_normalizado: str, termo: str) -> bool:
    return posicao_termo(texto_normalizado, termo) >= 0


def ler_preco(valor) -> float | None:
    """Converte '189,90', 'R$ 1.234,56' ou 189.9 em número. Vazio -> None."""
    if valor is None:
        return None
    if isinstance(valor, (int, float)):
        return float(valor)
    s = str(valor).strip().replace("R$", "").replace(" ", "")
    if not s:
        return None
    if "," in s:  # formato brasileiro: 1.234,56
        s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def slug(texto: str) -> str:
    """'Ração Golden 15kg' -> 'racao-golden-15kg' (para nome de arquivo)."""
    t = normalizar(texto)
    t = re.sub(r"[^a-z0-9]+", "-", t).strip("-")
    return t[:80]


def reais(valor: float | None) -> str:
    """189.9 -> 'R$ 189,90'"""
    if valor is None:
        return "-"
    s = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {s}"
