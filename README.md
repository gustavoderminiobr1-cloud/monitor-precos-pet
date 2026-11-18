# 🐾 Monitor de Preços Pet

Esta ferramenta pesquisa **toda semana** quanto o mercado está cobrando pelos
produtos da loja (ração, areia, antipulgas, remédios e gaiolas) no Google Shopping.
Ela mostra tudo num **painel colorido** que abre no celular.

Ela não usa inteligência artificial. Só pesquisa, organiza e mostra os preços.

---

## 📱 Onde ver os resultados

**Painel:** abra o link do painel no celular ou no computador.
👉 _(o link é preenchido quando o GitHub Pages for ativado)_

### Como ler o painel

| O que você vê | O que significa |
|---|---|
| 🟢 👍 **Bom preço** | Seu preço está **igual ou mais barato** que a média do mercado |
| 🟡 ✋ **Um pouco acima** | Seu preço está **até 10% mais caro** que a média |
| 🔴 👎 **Caro** | Seu preço está **mais de 10% acima** da média |
| 📏 **Faixa de preço** | Você não informou seu preço; só aparece o menor e o maior preço |
| ⬆️ **Subiu** (vermelho) | O menor preço do mercado **subiu** desde a última semana |
| ⬇️ **Caiu** (verde) | O menor preço do mercado **caiu** desde a última semana |
| ➡️ **Igual** | O preço praticamente não mudou |
| 🥇🥈🥉 **Mais procuradas na internet** | Marcas que mais aparecem e têm mais avaliações no Google. **É uma estimativa, não é venda real.** |

Toque num setor para entrar e toque num produto para ver **todas as lojas**,
da mais barata para a mais cara, com o botão **"Ver na loja"**.

### Planilha (backup)

No GitHub, abra a pasta `saida` e clique em `relatorio.xlsx`. Depois clique em **Download**.
Ela tem as abas: Resumo, Resultados, Marcas, Histórico e Avisos.

---

## ✏️ Como mudar a lista de produtos

A lista fica no arquivo **`produtos.csv`**.

**Pelo site do GitHub, sem instalar nada:**
1. Abra o repositório e clique em `produtos.csv`.
2. Clique no **lápis ✏️** (Edit), no canto direito.
3. Altere, acrescente ou apague linhas.
4. Clique no botão verde **Commit changes** e confirme.

**No computador:** dá para abrir o arquivo no Excel. Ao salvar, escolha **CSV (separado por ponto e vírgula)**.

### O que vai em cada coluna

As colunas são separadas por **ponto e vírgula `;`**.
Dentro de uma coluna, as palavras são separadas por **vírgula `,`**.

| Coluna | O que colocar | Exemplo |
|---|---|---|
| `nome_busca` | O que você digitaria no Google | `Ração Golden Fórmula cães adultos carne e arroz 15kg` |
| `categoria` | Um destes: `racao`, `areia`, `antipulgas`, `remedios`, `gaiolas` | `racao` |
| `palavras_obrigatorias` | Palavras que o anúncio **precisa** ter | `golden, adult, carne, 15kg` |
| `palavras_proibidas` | Palavras que fazem o anúncio ser **descartado** | `light, senior, filhote, mini bits` |
| `dia_da_semana` | Dia em que o produto é pesquisado | `segunda` |
| `meu_preco` | Quanto **a loja** cobra hoje (pode deixar vazio) | `219,90` |

Exemplo de uma linha completa:
```
Ração Golden Fórmula cães adultos carne e arroz 15kg;racao;golden, adult, carne, 15kg;light, senior, filhote, mini bits;segunda;219,90
```

### Dicas para não errar

- **Palavras obrigatórias:** use o começo da palavra para pegar plural e singular.
  `adult` pega "adulto", "adultos" e "adulta".
- **Peso:** escreva junto, como `15kg`. Ela entende "15 kg" e "15kg".
  `4kg` **não** pega "14kg".
- **Acentos e maiúsculas não importam:** `racao` = `Ração`.
- **Grupos no painel:** a ferramenta descobre sozinha pelo nome.
  Se o nome tem "cães" vai para 🐶 Cão, se tem "gatos" vai para 🐱 Gato.
  Na ração, "filhote" vai para 🍼 Filhote, "senior" para 👴 Idoso e o resto para 💪 Adulto.
- **Para desligar um produto sem apagar:** coloque `#` no começo da linha.

---

## 💰 Limite de pesquisas (para não pagar nada)

- O plano grátis da SerpAPI dá **250 pesquisas por mês**.
- A ferramenta **para sozinha em 230** e avisa no topo do painel com uma faixa vermelha ⚠️.
- Cada produto gasta **1 pesquisa por semana**, cerca de 4 ou 5 por mês.
- **Na prática, cabem até uns 45 produtos** na lista.
- O mesmo produto **nunca** é pesquisado duas vezes no mesmo dia.
- O contador volta a zero todo dia 1º.

---

## ⏰ Quando roda

Todo dia às **8h da manhã** (horário de Brasília), sozinha, pelo GitHub.
Ela pesquisa só os produtos marcados para o dia da semana.
O GitHub às vezes atrasa alguns minutos; isso é normal.

---

## 🔧 Parte técnica (para quem mantém a ferramenta)

```
monitor.py                → programa principal
produtos.csv              → lista de produtos
codigo/                   → código (busca, filtro, contador, histórico, marcas, painel, planilha)
codigo/painel-modelo.html → visual do painel (edite aqui, não no docs/index.html)
dados/historico.csv       → todos os anúncios, com data
dados/pesquisas-feitas.csv→ uma linha por pesquisa feita
dados/contador.json       → pesquisas gastas no mês
dados/respostas/          → resposta bruta da SerpAPI de cada pesquisa
dados/respostas-teste/    → respostas salvas, usadas no modo teste
docs/index.html           → painel publicado no GitHub Pages
saida/relatorio.xlsx      → planilha de backup
.github/workflows/diario.yml → automação diária
```

Comandos (Windows, dentro da pasta do projeto):

```
py -m pip install -r requirements.txt   # uma vez só
py monitor.py --teste                   # modo teste: não gasta pesquisas, gera teste/painel.html
py monitor.py                           # modo real: produtos do dia (pede confirmação)
py monitor.py --produto golden          # modo real: só produtos com "golden" no nome
py monitor.py --so-painel               # refaz painel e planilha sem pesquisar
```

A chave fica no arquivo `.env` (copie de `.env.exemplo`). No GitHub, ela fica em
**Settings → Secrets and variables → Actions**, com o nome `SERPAPI_KEY`.
O `.env` nunca vai para o GitHub.
