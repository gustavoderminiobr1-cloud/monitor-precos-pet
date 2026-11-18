"""
MONITOR DE PREÇOS PET - programa principal.

Como usar (no terminal, dentro da pasta do projeto):

    py monitor.py --teste        -> modo teste: usa respostas salvas, NÃO gasta pesquisas
    py monitor.py                -> modo real: pesquisa os produtos do dia de hoje
    py monitor.py --so-painel    -> só refaz painel e planilha com o que já foi pesquisado

Opções extras do modo real:
    --produto "golden"   -> pesquisa só os produtos cujo nome contém esse texto
    --todos              -> ignora o dia da semana (CUIDADO: gasta 1 pesquisa por produto)
    --sim                -> não pergunta "confirma?" (usado pela automação do GitHub)
"""
import argparse
import json
import shutil
import sys
from datetime import timedelta

from codigo import config
from codigo.analise import montar_resumo
from codigo.busca import ErroBusca, buscar_real, buscar_teste, carregar_chave, extrair_anuncios
from codigo.contador import Contador
from codigo.filtro import motivo_descarte
from codigo.historico import Historico
from codigo.marcas import descobrir_marca
from codigo.painel import gerar_painel
from codigo.planilha import gerar_planilha
from codigo.produtos import ler_produtos
from codigo.texto import normalizar, reais, slug

# Mostra acentos corretamente no terminal do Windows
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")


def pesquisar_produto(produto, data_iso, historico, contador, pastas, modo_teste, chave, subpasta_teste=""):
    """Pesquisa UM produto, filtra os anúncios e salva no histórico."""
    if historico.ja_pesquisado(data_iso, produto.nome_busca):
        print(f"  - já pesquisado hoje, pulando: {produto.nome_busca}")
        return "pulado"

    try:
        if modo_teste:
            resposta = buscar_teste(produto.nome_busca, subpasta_teste)
        else:
            contador.somar()  # conta ANTES de chamar: na dúvida, conta a mais e nunca a menos
            resposta = buscar_real(produto.nome_busca, chave)
            arquivo = pastas.respostas_brutas / f"{data_iso}_{slug(produto.nome_busca)}.json"
            arquivo.write_text(json.dumps(resposta, ensure_ascii=False, indent=1), encoding="utf-8")
    except ErroBusca as e:
        print(f"  ! ERRO em {produto.nome_busca}: {e}")
        historico.registrar_pesquisa(data_iso, produto.nome_busca, 0, 0, f"erro: {e}"[:200])
        return "erro"

    anuncios = extrair_anuncios(resposta)
    linhas, aprovados = [], 0
    for a in anuncios:
        motivo = motivo_descarte(a["titulo"], produto.obrigatorias, produto.proibidas)
        aprovados += not motivo
        linhas.append({**a, "data": data_iso, "nome_busca": produto.nome_busca,
                       "categoria": produto.categoria, "marca": descobrir_marca(a["titulo"]),
                       "passou_filtro": "não" if motivo else "sim", "motivo": motivo})
    historico.salvar_anuncios(linhas)
    historico.registrar_pesquisa(data_iso, produto.nome_busca, len(anuncios), aprovados, "ok")

    precos = sorted(l["preco"] for l in linhas if not l["motivo"])
    faixa = f"{reais(precos[0])} a {reais(precos[-1])}" if precos else "nenhum aprovado"
    print(f"  ok {produto.nome_busca}: {len(anuncios)} anúncios, {aprovados} aprovados ({faixa})")
    return "ok"


def main():
    ap = argparse.ArgumentParser(description="Monitor de preços pet")
    ap.add_argument("--teste", action="store_true", help="usa respostas salvas, sem gastar pesquisas")
    ap.add_argument("--todos", action="store_true", help="ignora o dia da semana")
    ap.add_argument("--produto", help="pesquisa só produtos que contêm este texto")
    ap.add_argument("--so-painel", action="store_true", help="só refaz painel e planilha")
    ap.add_argument("--sim", action="store_true", help="não pede confirmação")
    args = ap.parse_args()

    pastas = config.Pastas(args.teste)
    agora = config.agora()
    hoje = agora.date()
    produtos = ler_produtos()
    historico = Historico(pastas)
    contador = Contador(pastas.contador, hoje.strftime("%Y-%m"))
    aviso = ""

    print(f"Monitor de preços pet | {'MODO TESTE' if args.teste else 'MODO REAL'} | "
          f"{hoje.strftime('%d/%m/%Y')} ({config.DIAS_DA_SEMANA[hoje.weekday()]})")
    print(f"Produtos na lista: {len(produtos)}")

    if args.so_painel:
        pass

    elif args.teste:
        # Começa do zero e simula duas semanas: a passada e a de hoje
        shutil.rmtree(pastas.dados, ignore_errors=True)
        pastas = config.Pastas(True)
        historico = Historico(pastas)
        contador = Contador(pastas.contador, hoje.strftime("%Y-%m"))
        semana_passada = (hoje - timedelta(days=7)).isoformat()
        print(f"\nSimulando semana passada ({semana_passada}):")
        for p in produtos:
            if (config.PASTA_RESPOSTAS_TESTE / "semana-anterior" / f"{slug(p.nome_busca)}.json").exists():
                pesquisar_produto(p, semana_passada, historico, contador, pastas, True, None, "semana-anterior")
        print(f"\nSimulando hoje ({hoje.isoformat()}):")
        for p in produtos:
            pesquisar_produto(p, hoje.isoformat(), historico, contador, pastas, True, None)

    else:
        # ---------- MODO REAL ----------
        dia_hoje = config.DIAS_DA_SEMANA[hoje.weekday()]
        if args.produto:
            alvo = normalizar(args.produto)
            escolhidos = [p for p in produtos if alvo in normalizar(p.nome_busca)]
        elif args.todos:
            escolhidos = produtos
        else:
            escolhidos = [p for p in produtos if p.dia == dia_hoje]
        escolhidos = [p for p in escolhidos
                      if not historico.ja_pesquisado(hoje.isoformat(), p.nome_busca)]

        print(f"Pesquisas usadas este mês: {contador.pesquisas} de {config.LIMITE_MENSAL}")
        print(f"Produtos para pesquisar agora: {len(escolhidos)}")
        for p in escolhidos:
            print(f"  * {p.nome_busca}")

        if escolhidos:
            chave = carregar_chave()
            if not args.sim and sys.stdin.isatty():
                resp = input(f"\nIsso vai gastar até {len(escolhidos)} pesquisa(s) da SerpAPI. Confirma? (s/n) ")
                if resp.strip().lower() not in ("s", "sim"):
                    print("Cancelado. Nenhuma pesquisa foi feita.")
                    return
            nao_feitos = []
            for p in escolhidos:
                if not contador.pode_pesquisar():
                    nao_feitos.append(p.nome_busca)
                    continue
                pesquisar_produto(p, hoje.isoformat(), historico, contador, pastas, False, chave)
            if nao_feitos:
                aviso = (f"Limite de {config.LIMITE_MENSAL} pesquisas do mês atingido. "
                         f"{len(nao_feitos)} produto(s) ficaram sem pesquisa hoje. "
                         f"Volta ao normal no dia 1º do mês que vem.")

    if not aviso and not contador.pode_pesquisar():
        aviso = (f"Limite de {config.LIMITE_MENSAL} pesquisas do mês atingido. "
                 f"As pesquisas param até o dia 1º do mês que vem.")
    elif not aviso and contador.restantes <= 20:
        aviso = f"Atenção: restam só {contador.restantes} pesquisas neste mês."

    # ---------- Painel e planilha ----------
    todos = historico.todos()
    # Reaplica o filtro com as palavras ATUAIS do produtos.csv.
    # Assim, se a lista de palavras mudar, o painel já reflete isso, inclusive nas pesquisas antigas.
    regras = {p.nome_busca: p for p in produtos}
    for a in todos:
        p = regras.get(a["nome_busca"])
        if p:
            a["motivo"] = motivo_descarte(a["titulo"], p.obrigatorias, p.proibidas)
            a["passou_filtro"] = not a["motivo"]
    resumo = montar_resumo(
        produtos, todos, aviso=aviso,
        contador={"usadas": contador.pesquisas, "limite": config.LIMITE_MENSAL},
        atualizado=agora.strftime("%d/%m/%Y às %H:%M"))
    gerar_painel(resumo, pastas.painel, modo_teste=args.teste)
    gerar_planilha(resumo, todos, historico.todas_pesquisas(), pastas.planilha)

    if aviso:
        print(f"\nAVISO: {aviso}")
    print(f"\nPainel:   {pastas.painel}")
    print(f"Planilha: {pastas.planilha}")


if __name__ == "__main__":
    main()
