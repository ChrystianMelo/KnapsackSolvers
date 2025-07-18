# KnapsackSolvers

Implementações de algoritmos **exatos** (Branch-and-Bound) e **aproximativos** para o Problema da Mochila, acompanhadas de experimentos de desempenho e análise comparativa.

---

## ✨ Visão geral
<!-- (INALTERADO) -->
| Pasta / arquivo              | Descrição                                                                                   |
|------------------------------|----------------------------------------------------------------------------------------------|
| `src/`                       | Implementações em **Python 3** dos algoritmos: BnB, FPTAS, heurística 2-aproximada.          |
| `experiments/`               | Scripts para executar lote de testes, coletar métricas e gerar tabelas CSV.                 |
| `data/`                      | Instâncias de teste (low-dimensional e large-scale).                                         |
| `reports/`                   | Artigo científico em LaTeX (template SBC) + gráficos e tabelas finais.                      |
| `results/`                   | Saídas brutas: tempos, uso de memória, qualidade da solução.                                |
| `requirements.txt`           | Facilidades de instalação e automação.                                                      |
| `config.bat`                 | Atalho: ativa venv + executa workflow                                                       |
| `run.bat`                    | Executável para rodar o projeto                                                             |

---
---
## Pseudo-algoritmos
### Branch-and-Bound <br>
<sup>[Aula 12, slides 11]</sup>

```text
Procedure bnb-knapsack(items, W)
    # cada item i é (peso, valor, razão vᵢ/wᵢ)
    root  ← (0, 0, 0,  W · items[0][2],  [])      # (level, value, weight, bound, S)
    queue ← heap([root])                          # fila de prioridades (max-heap pelo bound)
    best  ← 0

    while queue ≠ ∅ do
        node ← queue.pop()                        # retira nó com maior bound

        if node.level = n − 1 then                # folha
            if best < node.value then
                best ← node.value
                sol  ← node.S                     # solução corrente
            end

        else if node.bound > best then            # só expande se bound é promissor
            with ← node.value
                    + items[node.level][1]
                    + (W − w − items[node.level][0]) · items[node.level + 1][2]

            wout ← node.value
                    + (W − w) · items[node.level + 1][2]

            if node.weight + items[node.level + 1] < W   and   with > best then
                queue.push( (node.level + 1,
                             node.value + items[node.level][1],
                             w + items[node.level][0],
                             with,
                             S ∪ {node.level}) )
            end

            if wout > best then
                queue.push( (node.level + 1,
                             node.value,
                             w,
                             wout,
                             S) )
            end
        end
    end
end
```

### Aproximativos<br>
<sup>[Aula 15, slides 12-14]</sup>

```text
Procedure FPTAS-Knapsack(items[1…n], W, ε ∈ (0,1))
  # cada item i possui peso wi e valor vi

  1. vmax ← max{ vi | 1 ≤ i ≤ n }
  2. μ    ← (ε · vmax) / n
  3. Para i ← 1 … n:
         v′i ← ⌊ vi / μ ⌋
  4. V′ ← Σ v′i
  5. Alocar matriz DP[0…n][0…V′] com ∞
  6. DP[0][0] ← 0
  7. Para k ← 1 … n:
         Para X ← 0 … V′:
              Se v′k > X então
                   DP[k][X] ← DP[k-1][X]
              senão
                   DP[k][X] ← min(DP[k-1][X],
                                   wk + DP[k-1][X − v′k])
  8. X* ← maior X tal que DP[n][X] ≤ W
  9. valor_aprox ← μ · X*
 10. (Opc.) reconstruir conjunto percorrendo DP
 11. Return (valor_aprox, conjunto_itens)
```

###  Algoritmo 2-aproximativo <br>
<sup> Inspirado no material [Aula 13 – Algoritmos Aproximativos, slides sobre Vertex Cover 2-aprox.]</sup>

```text
Procedure TwoApprox-Knapsack(items[1..n], W)
    # cada item i possui peso wi e valor vi
1.  Ordene os itens por densidade decrescente: di ← vi / wi
2.  peso_total   ← 0
    valor_guloso ← 0
3.  Para cada item (wi , vi ) na lista ordenada:
        se peso_total + wi ≤ W então
            peso_total   ← peso_total   + wi
            valor_guloso ← valor_guloso + vi
4.  valor_item ←  max { vi | wi ≤ W }        # melhor item avulso
5.  valor_alg  ←  max(valor_guloso, valor_item)
6.  Return valor_alg                          # garante ≤ 2 · OPT
```

---
## 📥 Instalação

```bash
# Clone
git clone https://github.com/ChrystianMelo/knapsack-solvers.git
cd knapsack-solvers

# Configura o projeto
./config.bat

# Executa o projeto
./run.bat
```

---

## 🗄️ Conjuntos de dados utilizados

| Categoria        | Fonte                                                                                                               |
|------------------|---------------------------------------------------------------------------------------------------------------------|
| Low dimensional  | Artemisa/UNICAUCA instances 01 KP – <http://artemisa.unicauca.edu.co/~johnyortega/instances_01_KP/> |
| Large scale      | Kaggle - “large-scale-01-knapsack-problems” – <https://www.kaggle.com/datasets/sc0v1n0/large-scale-01-knapsack-problems> |

As instâncias são automaticamente baixadas pelo script `experiments/fetch_data.py` na primeira execução.

---

## ⚡ Pipeline de experimentos

```mermaid
flowchart TD
    A[Instâncias .csv] --> C{Algoritmo}
    C -->|BnB| D[utils.solvers.bnb]
    C -->|FPTAS| E[utils.solvers.fptas]
    C -->|2-approx| F[utils.solvers.two_approx]
    D & E & F --> H[results/*.csv]
    H --> I[reports/article.tex]
```

---

## 📊 Principais achados empíricos

* **BnB** resolveu **100 %** das instâncias *low‑dimensional* em ≤ 31 s e manteve tempo **≤ 8 ms** nas *large‑scale* analisadas (4/4).
* **FPTAS (ε = 0.02)** alcançou **erro máximo = 0.14 %** (mediana = 0 %) com tempo mediano **≈ 50 ms**; houve *timeout* em **22 %** das instâncias mais densas.
* **Heurística 2‑aprox.** finalizou sempre em **< 7 ms**; o desvio médio foi **2.8 %** (máx. 30 %), ficando **≤ 5 % em 75 %** dos casos.

Esses números reproduzem as Tabelas 2 e 3 do artigo.

---
