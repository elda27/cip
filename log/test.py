import math
def reverse_num(num):
    num_digit = math.ceil(math.log10(num))
    num_list = list()
    div = num
    for i in range(num_digit):
        remain = div % 10
        div = div // 10
        num_list.append(remain)
    result = 0
    for i, value in enumerate(num_list):
        result += value * (10 ** i)