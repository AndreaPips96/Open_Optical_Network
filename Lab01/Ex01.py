# Excercise Set 1 -> Python basics #

# 1
print("Insert two integer numbers")
var1 = int(input("Insert first number: "))
var2 = int(input("Insert second number: "))
print("You inserted", var1, " and ", var2)

if (var1 * var2) > 1000:
    sum = var1 + var2
    print(sum)
else:
    print("Their product is smaller than 1000.")

# 2
print("In order to create a range of numbers insert two integer numbers")
var1 = int(input("Insert first number: "))
var2 = int(input("Insert last number: "))
print("You inserted", var1, " and ", var2)

prev_x = 0
for x in range(var1, var2+1):
    print(x+prev_x)
    prev_x = x

# 3
# creating an empty list
lst = []
# number of elements as input
n = int(input("Insert number of elements : "))

# iterating till the range
for i in range(0, n):
    elem = int(input())
    lst.append(elem)  # adding the element to the list

print(lst)
