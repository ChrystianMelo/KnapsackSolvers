# KnapsackSolvers

Implementações de algoritmos **exatos** (Branch-and-Bound) e **aproximativos** para o Problema da Mochila, acompanhadas de experimentos de desempenho e análise comparativa.

---

## ✨ Visão geral

Este repositório contém:

| Pasta / arquivo              | Descrição                                                                                   |
|------------------------------|----------------------------------------------------------------------------------------------|
| `src/`                       | Implementações em **Python 3** dos algoritmos: BnB, FPTAS, heurística 2-aproximada.          |
| `experiments/`               | Scripts para executar lote de testes, coletar métricas e gerar tabelas CSV.                 |
| `data/`                      | Instâncias de teste (low-dimensional e large-scale). **Não versionadas** ↠ baixar via script |
| `reports/`                   | Artigo científico em LaTeX (template SBC) + gráficos e tabelas finais.                      |
| `results/`                   | Saídas brutas: tempos, uso de memória, qualidade da solução.                                |
| `requirements.txt`           | Facilidades de instalação e automação.                                                      |
| `config.bat` / `config.sh`   | Atalho: ativa venv + executa workflow
| `run.bat` / `run.sh`         | Executável para rodar o projeto

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
