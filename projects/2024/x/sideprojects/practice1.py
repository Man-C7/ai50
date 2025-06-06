def linear_search(lst, target):
    for i, x in enumerate(lst):
        if x == target:
            return i
    return None

def binary_search(lst, target):
    low, high = 0, len(lst) - 1
    while(low <= high):
        mid = (low + high) // 2
        if lst[mid] == target:
            return mid
        elif lst[mid] > target:
            high = mid - 1
        else:
            low = mid + 1
    return None
