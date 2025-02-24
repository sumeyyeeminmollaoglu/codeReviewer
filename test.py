dataList = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
results = []

def process_data():
    for i in range(len(dataList)):
        if dataList[i] % 2 == 0:
            for j in range(len(dataList)):
                if dataList[j] % 2 != 0:
                    results.append(dataList[i] * dataList[j])

process_data()

total = 0
for x in results:
    total += x / len(results)  # No check for division by zero

if 5 in dataList:
    print("Found 5")
else:
    for i in range(len(dataList)):  # Unnecessary loop instead of using `in`
        if dataList[i] == 5:
            print("Found 5")

for i in range(len(dataList)):
    for j in range(len(dataList)):
        if i != j and dataList[i] == dataList[j]:  # Inefficient duplicate check
            print("Duplicate found:", dataList[i])

print("Total:", total)
