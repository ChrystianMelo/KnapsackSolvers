from typing import List, Tuple
import heapq
import math


def knapsack_bnb(items: List[Tuple[int, int]], W: int):
    """
    Resolve a mochila 0-1 por Branch-and-Bound (best-first).

    items : lista de pares (peso, valor)
    W     : capacidade inteira

    Retorna (valor ótimo, lista de índices dos itens escolhidos)
    """
    n = len(items)

    order = sorted(
        range(n), key=lambda i: items[i][1] / items[i][0], reverse=True)
    items_ord = [items[i] for i in order]

    def bound(level, value, weight):
        """Cálculo do bound fracionário igual ao slide."""
        if weight >= W:
            return 0
        tot_val = value
        j = level
        cap = W - weight

        while j < n and items_ord[j][0] <= cap:
            cap -= items_ord[j][0]
            tot_val += items_ord[j][1]
            j += 1
        if j < n:
            w_j, v_j = items_ord[j]
            tot_val += v_j * cap / w_j
        return tot_val

    root = (-bound(0, 0, 0), 0, 0, 0, [])
    heap = [root]
    best_val = 0
    best_set = []

    while heap:
        nb, level, value, weight, chosen = heapq.heappop(heap)
        nb = -nb

        if nb <= best_val or level == n:
            continue

        w_i, v_i = items_ord[level]
        idx_i = order[level]

        new_w = weight + w_i
        new_v = value + v_i
        if new_w <= W:
            if new_v > best_val:
                best_val, best_set = new_v, chosen + [idx_i]
            bnd = bound(level + 1, new_v, new_w)
            if bnd > best_val:
                heapq.heappush(heap, (-bnd, level + 1, new_v, new_w,
                                      chosen + [idx_i]))

        bnd = bound(level + 1, value, weight)
        if bnd > best_val:
            heapq.heappush(heap, (-bnd, level + 1, value, weight, chosen))

    best_set.sort()
    return best_val, best_set


def knapsack_fptas(items: List[Tuple[int, int]], W: int, eps: float = 0.1):
    """
    FPTAS (1-eps)-aproximado para a mochila.

    items : lista (peso, valor)
    W     : capacidade
    eps   : 0 < eps < 1

    Retorna (valor_aprox, subconjunto_itens)
    """
    n = len(items)
    vmax = max(v for _, v in items)
    mu = eps * vmax / n

    v_scaled = [math.floor(v / mu) for _, v in items]
    V_sum = sum(v_scaled)

    INF = W + 1
    dp = [0] + [INF] * V_sum

    parent = [(-1, -1)] * (V_sum + 1)

    for i, (w_i, _v_i) in enumerate(items):
        v_i = v_scaled[i]
        for X in range(V_sum, v_i - 1, -1):
            prev_w = dp[X - v_i]
            if prev_w + w_i < dp[X]:
                dp[X] = prev_w + w_i
                parent[X] = (i, X - v_i)

    X_star = max(x for x, w in enumerate(dp) if w <= W)
    val_aprox = int(round(X_star * mu))

    sol = []
    cur = X_star
    while cur > 0 and parent[cur][0] != -1:
        idx, prev = parent[cur]
        sol.append(idx)
        cur = prev
    sol.reverse()

    return val_aprox, sol
