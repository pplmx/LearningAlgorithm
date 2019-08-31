#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime

import networkx
from numpy import random

from linear_threshold import LT_model
from linear_threshold.LT_model import LinearThresholdModel


def find_optimal(graph):
    minimal_dominating_set = set()
    degree_list = list(graph.degree)
    start = datetime.now()
    # quick_sort_iterative(degree_list, 0, len(degree_list) - 1, 1)
    degree_list = sorted(degree_list, key=lambda x: x[1])
    end = datetime.now()
    print("Sort cost: {}s".format(end - start))
    # store the node whose degree is zero
    degree_0_node_list = []
    # store the node who has a neighbor whose degree is 1
    degree_1_node_nbr_list = []
    for idx, val in enumerate(degree_list):
        if val[1] == 0:
            degree_0_node_list.append(val[0])
        elif val[1] == 1:
            degree_1_node_nbr_list.append(list(graph[val[0]])[0])
        else:
            # remove the nodes whose degree is 0 or 1
            degree_list = degree_list[idx:]
            break
    minimal_dominating_set |= set(degree_0_node_list + degree_1_node_nbr_list)

    # To init the graph
    lt_model = LinearThresholdModel(graph)
    graph = lt_model.get_graph()

    flag = 0
    for node, deg in degree_list[::-1]:
        flag += 1
        if flag > 1:
            # except the 1st times, if node in minimal dominating set, go to the next loop
            if node in minimal_dominating_set:
                continue
        minimal_dominating_set.add(node)
        # print(minimal_dominating_set)
        next_seeds, this_activated = LT_model.diffuse_one_round(graph, minimal_dominating_set)
        # layer_i_nodes = LT_model.linear_threshold(graph, minimal_dominating_set, steps=1)
        if len(next_seeds) == len(graph):
            # return the optimal seeds
            return list(minimal_dominating_set)


def quick_sort4tuple_list(unsorted_list, idx=0, is_ordered_by_ascend=True):
    """
        unsorted_list e.g.:
                li1 = [(1, 3), (5, 9), (2, 1), (4, 14)]
                li2 = [(1, 3, 12), (5, 9, 1), (2, 1, 343), (4, 14, 0)]
                quick_sort4tuple_list(li1)
                => [(1, 3), (2, 1), (4, 14), (5, 9)]
                quick_sort4tuple_list(li2, 2, False)
                => [(2, 1, 343), (1, 3, 12), (5, 9, 1), (4, 14, 0)]
    :param unsorted_list:
    :param idx: order by the idx_th value of tuple
    :param is_ordered_by_ascend: default order by Ascend
    :return:
    """
    data_len = len(unsorted_list)
    if data_len <= 1:
        return unsorted_list
    rand_val = random.randint(data_len)
    mid_tuple = unsorted_list[rand_val]
    del unsorted_list[rand_val]
    less = [i for i in unsorted_list if i[idx] <= mid_tuple[idx]]
    greater = [i for i in unsorted_list if i[idx] > mid_tuple[idx]]
    if is_ordered_by_ascend:
        return quick_sort4tuple_list(less, idx) + [mid_tuple] + quick_sort4tuple_list(greater, idx)
    return quick_sort4tuple_list(greater, idx, False) + [mid_tuple] + quick_sort4tuple_list(less, idx, False)


def quick_sort_by_recursion(arr):
    data_len = len(arr)
    if data_len <= 1:
        return arr
    rand_val = random.randint(data_len)
    mid_val = arr[rand_val]
    del arr[rand_val]
    less = [i for i in arr if i <= mid_val]
    greater = [i for i in arr if i > mid_val]
    return quick_sort_by_recursion(less) + [mid_val] + quick_sort_by_recursion(greater)


def quick_sort(arr, left, right):
    if left < right:
        pivot_idx = partition(arr, left, right)

        # Separately sort elements before
        # partition and after partition
        quick_sort(arr, left, pivot_idx - 1)
        quick_sort(arr, pivot_idx + 1, right)


def quick_sort_iterative(arr, low, high, idx=None):
    # Create an auxiliary stack
    size = high - low + 1
    stack = [0] * size

    # initialize top of stack
    top = -1

    # push initial values of l and h to stack
    top += 1
    stack[top] = low
    top += 1
    stack[top] = high

    # Keep popping from stack while is not empty
    while top >= 0:

        # Pop h and l
        high = stack[top]
        top = top - 1
        low = stack[top]
        top = top - 1

        # Set pivot element at its correct position in
        # sorted array
        # pivot_idx = partition(arr, low, high)
        pivot_idx = random_partition4tuple_list(arr, low, high, idx)

        # If there are elements on left side of pivot,
        # then push left side to stack
        if pivot_idx - 1 > low:
            top = top + 1
            stack[top] = low
            top = top + 1
            stack[top] = pivot_idx - 1

        # If there are elements on right side of pivot,
        # then push right side to stack
        if pivot_idx + 1 < high:
            top = top + 1
            stack[top] = pivot_idx + 1
            top = top + 1
            stack[top] = high


def random_quick_sort(arr, left, right):
    if left < right:
        pivot_idx = random_partition(arr, left, right)
        random_quick_sort(arr, left, pivot_idx - 1)
        random_quick_sort(arr, pivot_idx + 1, right)


def partition(arr, start_idx, end_idx):
    pivot = arr[end_idx]

    # index of smaller element
    i = start_idx - 1
    for j in range(start_idx, end_idx):
        # If current element is smaller than the pivot
        if arr[j] <= pivot:
            # increment index of smaller element
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[end_idx] = arr[end_idx], arr[i + 1]
    return i + 1


def random_partition4tuple_list(tuple_list, left, right, idx=0):
    pivot_idx = random.randint(left, right + 1)
    tuple_list[pivot_idx], tuple_list[right] = tuple_list[right], tuple_list[pivot_idx]
    x = tuple_list[right][idx]
    i = left - 1
    for j in range(left, right):
        if tuple_list[j][idx] <= x:
            i += 1
            tuple_list[i], tuple_list[j] = tuple_list[j], tuple_list[i]
    tuple_list[i + 1], tuple_list[right] = tuple_list[right], tuple_list[i + 1]
    return i + 1


def random_partition(arr, left, right):
    pivot_idx = random.randint(left, right + 1)  # 生成[left,right]之间的一个随机数
    arr[pivot_idx], arr[right] = arr[right], arr[pivot_idx]
    x = arr[right]
    i = left - 1  # 初始i指向一个空，保证0到i都小于等于 x
    for j in range(left, right):  # j用来寻找比x小的，找到就和i+1交换，保证i之前的都小于等于x
        if arr[j] <= x:
            i = i + 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[right] = arr[right], arr[i + 1]  # 0到i 都小于等于x ,所以x的最终位置就是i+1
    return i + 1


if __name__ == '__main__':
    g = networkx.Graph()
    g.add_edges_from([(1, 2), (1, 3), (2, 3), (3, 4), (3, 5), (4, 5), (4, 6), (5, 6)])
    print(find_optimal(g))

    # To check if the rate of custom quick sort is normal
    # tuple_l = [(i, i + 1) for i in range(2_000_000)]
    # for i in range(10):
    #     random.shuffle(tuple_l)
    #     start_time = datetime.now()
    #     quick_sort_iterative(tuple_l, 0, len(tuple_l) - 1, 1)
    #     end_time = datetime.now()
    #     print("Defined Quick Sort cost: {}s".format(end_time - start_time))
    #     if tuple_l == sorted(tuple_l, key=lambda x: x[1]):
    #         print("Quick sort is successful.")
    #     else:
    #         print("Quick sort is error.")
