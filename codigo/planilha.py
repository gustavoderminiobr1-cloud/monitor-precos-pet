"""
Planilha Excel de backup (relatorio.xlsx).

Abas:
- Resumo: um produto por linha (menor, maior, média, seu preço, sinal, tendência)
- Resultados: todos os anúncios aprovados, do mais barato ao mais caro
- Marcas: ranking de marcas por setor (estimativa de popularidade)
- Histórico: todos os anúncios de todas as datas
- Avisos: limite de pesquisas e outros recados
"""
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

COR_TITULO = PatternFill("solid", fgColor="1F2937")
CORES_SINAL = {"verde": "C6F6D5", "amarelo": "FEF3C7", "vermelho": "FED7D7"}
TEXTO_SINAL = {"verde": "Bom (abaixo da média)", "amarelo": "Um pouco acima (até 10%)",
               "vermelho": "Caro (mais de 10% acima)", "": "Sem seu preço"}
TEXTO_TENDENCIA = {"subiu": "Subiu ↑", "caiu": "Caiu ↓", "igual": "Igual →", "": "-"}
FORMATO_REAIS = 'R$ #,##0.00'


def _aba(wb, titulo, cabecalho, larguras):
    ws = wb.create_sheet(titulo)
    ws.append(cabecalho)
    for i, largura in enumerate(larguras, 1):
        ws.column_dimensions[get_column_letter(i)].width = largura
        c = ws.cell(row=1, column=i)
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = COR_TITULO
        c.alignment = Alignment(vertical="center", wrap_text=True)
    ws.freeze_panes = "A2"
    return ws


def _reais(ws, colunas):
    for col in colunas:
        for celula in ws[col][1:]:
            celula.number_format = FORMATO_REAIS


def gerar_planilha(resumo, historico, pesquisas, arquivo):
    wb = Workbook()
    wb.remove(wb.active)

    # ---- Resumo ----
    ws = _aba(wb, "Resumo", ["Produto", "Setor", "Grupo", "Data", "Menor preço", "Loja do menor",
                             "Maior preço", "Média", "Meu preço", "Sinal", "Diferença p/ média",
                             "Tendência", "Menor semana anterior", "Anúncios"],
              [45, 12, 14, 12, 13, 22, 13, 13, 13, 24, 12, 11, 14, 10])
    for p in resumo["produtos"]:
        if not p["pesquisado"]:
            ws.append([p["nome"], p["categoria"], p["subgrupo"], f"aguardando ({p['dia']})"])
            continue
        ws.append([p["nome"], p["categoria"], p["subgrupo"], p["data"], p["menor"], p["loja"],
                   p["maior"], p["media"], p["meu_preco"], TEXTO_SINAL[p["sinal"]],
                   p["diferenca"], TEXTO_TENDENCIA[p["tendencia"]], p["menor_anterior"],
                   len(p["ofertas"])])
        if p["sinal"]:
            ws.cell(row=ws.max_row, column=10).fill = PatternFill("solid", fgColor=CORES_SINAL[p["sinal"]])
    _reais(ws, "EGHIM")
    for c in ws["K"][1:]:
        c.number_format = "+0.0%;-0.0%;0%"

    # ---- Resultados ----
    ws = _aba(wb, "Resultados", ["Produto", "Posição", "Anúncio", "Loja", "Preço", "Nota",
                                 "Avaliações", "Link"], [40, 8, 60, 22, 12, 7, 11, 50])
    for p in resumo["produtos"]:
        for i, o in enumerate(p.get("ofertas", []), 1):
            ws.append([p["nome"], i, o["titulo"], o["loja"], o["preco"], o["nota"],
                       o["avaliacoes"], o["link"]])
            if o["link"]:
                ws.cell(row=ws.max_row, column=8).hyperlink = o["link"]
    _reais(ws, "E")

    # ---- Marcas ----
    ws = _aba(wb, "Marcas", ["Setor", "Posição", "Marca", "Vezes que aparece",
                             "Avaliações somadas"], [14, 9, 22, 18, 18])
    ws.cell(row=1, column=7, value="ATENÇÃO: estimativa de popularidade na internet, NÃO é volume real de vendas.").font = Font(bold=True, color="B91C1C")
    for setor in resumo["setores"]:
        for i, m in enumerate(setor["marcas"], 1):
            ws.append([setor["nome"], i, m["marca"], m["aparicoes"], m["avaliacoes"]])

    # ---- Histórico ----
    ws = _aba(wb, "Histórico", ["Data", "Produto", "Setor", "Anúncio", "Loja", "Preço", "Nota",
                                "Avaliações", "Marca", "Passou no filtro", "Motivo", "Link"],
              [11, 35, 11, 55, 20, 12, 7, 11, 15, 10, 18, 40])
    for a in historico:
        ws.append([a["data"], a["nome_busca"], a["categoria"], a["titulo"], a["loja"], a["preco"],
                   a["nota"], a["avaliacoes"], a["marca"], "sim" if a["passou_filtro"] else "não",
                   a["motivo"], a["link"]])
    _reais(ws, "F")
    ws.auto_filter.ref = ws.dimensions

    # ---- Avisos ----
    ws = _aba(wb, "Avisos", ["Item", "Valor"], [35, 80])
    c = resumo["contador"]
    ws.append(["Última atualização", resumo["atualizado"]])
    ws.append(["Pesquisas usadas no mês", f"{c.get('usadas', 0)} de {c.get('limite', 0)}"])
    ws.append(["Aviso", resumo["aviso"] or "Nenhum"])
    ws.append([])
    ws.append(["Pesquisas feitas (data / produto / anúncios / aprovados / situação)"])
    for l in pesquisas:
        ws.append([l["data"], f"{l['nome_busca']} | {l['anuncios']} anúncios | "
                              f"{l['aprovados']} aprovados | {l['situacao']}"])

    wb.save(arquivo)
