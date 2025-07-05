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

## 📥 Instalação

```bash
# Clone
git clone https://github.com/seu-usuario/knapsack-solvers.git
cd knapsack-solvers

# Configura o projeto
./config.bat

# Executa o projeto
./run.bat
