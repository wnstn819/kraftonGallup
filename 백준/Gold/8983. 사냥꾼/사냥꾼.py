from sys import stdin as s

M, N, L = list(map(int,s.readline().split()))

arr = list(map(int, s.readline().split()))

arr.sort()

count = 0
for i in range(N):
    x, y = list(map(int,s.readline().split()))
    if y > L :
        continue
    else :
        temp = L-y
        for j in arr:
            if x+temp >= j and x-temp <= j:
                count+=1
                break


print(count)