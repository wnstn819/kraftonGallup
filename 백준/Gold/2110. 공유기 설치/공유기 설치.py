from sys import stdin as s

N, M = list(map(int,s.readline().split()))

arr = list(map(int, s.readlines()))

arr.sort()

result = 0


def binary(target,start,end):
    global result
    mid = (start+end)//2
    cnt = 1
    location = 0
    if start > end:
        return

    for i in range(1,N):
        if abs(arr[location] - arr[i]) >= mid:
            cnt +=1
            location = i
        
 
        

    if cnt >= target:
        result = max(result,mid)
        binary(target,mid+1,end)
    else :
        binary(target,start,mid-1)



binary(M, 1,arr[-1] - arr[0])
print(result)