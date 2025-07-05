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
![image](https://github.com/user-attachments/assets/c663dfbc-9d53-406e-869b-ac385b260fc2)

### Aproximativos<br>
![image2](https://github.com/user-attachments/assets/b693a2c1-c7d2-48cd-9363-0dcd47516ecf)

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
