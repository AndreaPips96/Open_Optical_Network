# Exercise Set 4 -> Pandas & Matplotlib

# 1
import pandas as pd
import matplotlib.pyplot as plt

my_dict = pd.read_csv('sales_data.csv', sep=',')
# print(my_dict)
# plt.figure(1)
# plt.plot(my_dict['month_number'], my_dict['total_profit'], label='Profit data of last year', color='r', marker='o', markerfacecolor='k', linestyle='-', linewidth=3.)
# plt.legend()
# plt.show()

# plt.figure(2)
# plt.plot(my_dict['month_number'], my_dict['facecream'], my_dict['month_number'], my_dict['facewash'],
#          my_dict['month_number'], my_dict['toothpaste'], my_dict['month_number'], my_dict['bathingsoap'],
#          my_dict['month_number'], my_dict['shampoo'], my_dict['month_number'], my_dict['moisturizer'])
# plt.show()

# plt.figure(3)
# plt.scatter(my_dict['month_number'], my_dict['toothpaste'])
# plt.show()

# fig = plt.figure(4)
# plt.bar(my_dict['month_number'], my_dict['bathingsoap'])
# fig.savefig("bathingsoap_hist.png")
# plt.show()

plt.figure(5)
plt.hist(my_dict['total_profit'])
plt.show()
