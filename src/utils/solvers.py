from typing import List, Tuple
import heapq
import math


def knapsack_bnb(items: List[Tuple[int, int]], W: int):
    '''Branch-and-Bound best-first para mochila 0-1; devolve valor ótimo e itens escolhidos.'''
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
    '''FPTAS (1-ε) para mochila; devolve valor aproximado e itens escolhidos.'''
    n = len(items)
    vmax = max(v for _, v in items)

    if vmax == 0:
        return 0, []

    mu = eps * vmax / n

    v_scaled = [int(v // mu) for _, v in items]
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


def knapsack_two_approx(items: List[Tuple[int, int]], W: int) -> Tuple[int, List[int]]:
    """ Algoritmo 2-aproximativo para a Mochila Binária. """
    idx_sorted = sorted(range(len(items)),
                        key=lambda i: items[i][1] / items[i][0],
                        reverse=True)

    w_acc = v_greedy = 0
    chosen = []
    for i in idx_sorted:
        w, v = items[i]
        if w_acc + w <= W:
            w_acc += w
            v_greedy += v
            chosen.append(i)

    best_single_value = max((v for w, v in items if w <= W), default=0)
    value = max(v_greedy, best_single_value)
    return value, chosen
