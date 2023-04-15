from sys import stdin as s
import sys

n = int(s.readline())

arr = list(map(int,s.readline().split()))


start = 0
end = len(arr)-1

arr.sort()

result = sys.maxsize
d ,v, = 0 , 0

while start < end:
    if arr[start] + arr[end] > 0:
        if abs(result) > abs(arr[start] + arr[end]):
            d = start
            v = end
            result = arr[start]+arr[end]
        end -= 1
    elif arr[start] + arr[end] < 0 :
        if abs(result) > abs(arr[start] + arr[end]):
            d = start
            v = end
            result = arr[start] + arr[end]
        start +=1

    else:
        d = start
        v = end
        break



print(arr[d], arr[v])