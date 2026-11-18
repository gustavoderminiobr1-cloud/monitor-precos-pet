"""
Lê a lista de produtos (produtos.csv) que o dono da loja edita.

O arquivo usa ponto e vírgula (;) para separar colunas, que é o padrão
do Excel em português. Dentro de uma célula, as palavras são separadas
por vírgula. Exemplo de linha:

Ração Golden Fórmula cães adultos carne e arroz 15kg;racao;golden,adulto,15kg;light,senior;segunda;199,90
"""
import csv
from dataclasses import dataclass

from . import config
from .texto import ler_preco, normalizar, separar_lista, sem_acento

COLUNAS = ["nome_busca", "categoria", "palavras_obrigatorias",
           "palavras_proibidas", "dia_da_semana", "meu_preco"]


@dataclass
class Produto:
    nome_busca: str
    categoria: str          # chave do setor: racao, areia, antipulgas, remedios, gaiolas
    obrigatorias: list
    proibidas: list
    dia: str                # segunda, terca, ...
    meu_preco: float | None
    subgrupo: str           # ex.: "Cão · Adulto" (descoberto pelo nome)
    animal: str             # "cao", "gato" ou ""


def _categoria(texto: str) -> str:
    """Aceita 'Ração', 'racao', 'Remédios', 'remedio' etc."""
    t = normalizar(texto)
    for chave in config.SETORES:
        if t.startswith(chave[:5]):
            return chave
    return t or "racao"


def _dia(texto: str) -> str:
    """Aceita 'Segunda', 'segunda-feira', 'terça', 'sab' etc."""
    t = normalizar(texto)
    for dia in config.DIAS_DA_SEMANA:
        if t.startswith(dia[:3]):
            return dia
    return t


def _descobrir_subgrupo(nome: str, categoria: str) -> tuple[str, str]:
    """Descobre o animal e a idade pelo nome do produto.
    Devolve (animal, subgrupo)."""
    t = normalizar(nome)
    animal = ""
    if any(p in t for p in ("gato", "felino", "cat ")):
        animal = "gato"
    elif any(p in t for p in ("cao", "caes", "cachorro", "canino", "dog")):
        animal = "cao"
    elif categoria == "areia":
        animal = "gato"

    nome_animal = {"cao": "Cão", "gato": "Gato"}.get(animal, "Outros")
    if categoria != "racao":
        return animal, nome_animal

    if any(p in t for p in ("filhote", "puppy", "junior", "kitten")):
        idade = "Filhote"
    elif any(p in t for p in ("senior", "idoso", "7+", "mature")):
        idade = "Idoso"
    else:
        idade = "Adulto"
    return animal, f"{nome_animal} · {idade}"


def ler_produtos() -> list[Produto]:
    """Lê o produtos.csv e devolve a lista de produtos."""
    produtos = []
    # utf-8-sig: aceita o arquivo salvo pelo Excel (que coloca um caractere invisível no início)
    with open(config.ARQUIVO_PRODUTOS, encoding="utf-8-sig", newline="") as f:
        amostra = f.read(2048)
        f.seek(0)
        separador = ";" if amostra.count(";") >= amostra.count(",") / 3 else ","
        leitor = csv.DictReader(f, delimiter=separador)
        # nomes de coluna sem acento/maiúscula, para tolerar pequenas diferenças
        leitor.fieldnames = [sem_acento(c).strip().lower() for c in leitor.fieldnames]
        faltando = [c for c in COLUNAS[:2] if c not in leitor.fieldnames]
        if faltando:
            raise SystemExit(f"ERRO: o produtos.csv não tem as colunas: {', '.join(faltando)}")

        for linha in leitor:
            nome = (linha.get("nome_busca") or "").strip()
            if not nome or nome.startswith("#"):
                continue  # linha vazia ou comentada
            categoria = _categoria(linha.get("categoria", ""))
            animal, subgrupo = _descobrir_subgrupo(nome, categoria)
            produtos.append(Produto(
                nome_busca=nome,
                categoria=categoria,
                obrigatorias=separar_lista(linha.get("palavras_obrigatorias", "")),
                proibidas=separar_lista(linha.get("palavras_proibidas", "")),
                dia=_dia(linha.get("dia_da_semana", "")),
                meu_preco=ler_preco(linha.get("meu_preco")),
                subgrupo=subgrupo,
                animal=animal,
            ))
    return produtos
