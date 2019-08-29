#!/usr/bin/env python
# -*- coding: utf-8 -*-
from numpy import random

from linear_threshold.LT_model import linear_threshold


def find_optimal(graph):
    minimal_dominating_set = set()
    degree_list = quick_sort4tuple_list(list(graph.degree), 1)
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
    for node, deg in degree_list[::-1]:
        minimal_dominating_set |= {node}
        layer_i_nodes = linear_threshold(graph, list(minimal_dominating_set))
        if len(layer_i_nodes) == 2:
            # return the optimal seeds
            return layer_i_nodes[0]


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


def quicksort(arr, left, right):
    if left < right:
        # pi is partitioning index, arr[p] is now
        # at right place
        pi = partition(arr, left, right)

        # Separately sort elements before
        # partition and after partition
        quicksort(arr, left, pi - 1)
        quicksort(arr, pi + 1, right)


def quick_sort_iterative(arr, l, h):
    # Create an auxiliary stack
    size = h - l + 1
    stack = [0] * size

    # initialize top of stack
    top = -1

    # push initial values of l and h to stack
    top += 1
    stack[0] = l
    top += 1
    stack[1] = h

    # Keep popping from stack while is not empty
    while top >= 0:

        # Pop h and l
        h = stack[top]
        top = top - 1
        l = stack[top]
        top = top - 1

        # Set pivot element at its correct position in
        # sorted array
        p = partition(arr, l, h)

        # If there are elements on left side of pivot,
        # then push left side to stack
        if p - 1 > l:
            top = top + 1
            stack[top] = l
            top = top + 1
            stack[top] = p - 1

        # If there are elements on right side of pivot,
        # then push right side to stack
        if p + 1 < h:
            top = top + 1
            stack[top] = p + 1
            top = top + 1
            stack[top] = h


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


def random_quicksort(arr, left, right):
    if left < right:
        mid = random_partition(arr, left, right)
        random_quicksort(arr, left, mid - 1)
        random_quicksort(arr, mid + 1, right)


def random_partition(arr, left, right):
    pivot = random.randint(left, right + 1)  # 生成[left,right]之间的一个随机数
    arr[pivot], arr[right] = arr[right], arr[pivot]
    x = arr[right]
    i = left - 1  # 初始i指向一个空，保证0到i都小于等于 x
    for j in range(left, right):  # j用来寻找比x小的，找到就和i+1交换，保证i之前的都小于等于x
        if arr[j] <= x:
            i = i + 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[right] = arr[right], arr[i + 1]  # 0到i 都小于等于x ,所以x的最终位置就是i+1
    return i + 1


if __name__ == '__main__':
    # g = networkx.Graph()
    # g.add_edges_from([(1, 2), (1, 3), (2, 3), (3, 4), (3, 5), (4, 5), (4, 6), (5, 6)])
    # print(find_optimal(g))

    arr_t = [2, 35, 1, 6, 23, 6762, 2435, 90]
    quick_sort_iterative(arr_t, 0, 7)
    print(arr_t)
