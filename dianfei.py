def cal_amount(x):
    if x < 200:
        return x * 0.588
    elif x < 450:
        return 200 * 0.588 + (x - 200) * 0.638
    else:
        return 200 * 0.588 + 250 * 0.638 + (x - 450) * 0.888


print('当前用电量(或者之前用电量 当前用电量):')
total = float(0)
amount = float(0)
for x in input().split():
    total += float(x)
    amount_before = amount
    amount = cal_amount(total)
    print(amount - amount_before)
print(amount)

input("Press enter to exit.")






