def dist(point1, point2):
    sum = 0
    d = len(point1)
    for i in range(d):
        sum += (point1[i] - point2[i]) ** 2
    sum = sum ** 0.5
    return sum


def mindist(centroids_list, point):
    min = "inf"
    index = 0
    for j in range(len(centroids_list)):
        distance = dist(centroids_list[j], point)
        if (min == "inf" or distance < min):
            min = distance
            index = j
    return index


def clustering(centroids_list, DataPoints, indexingList):
    for i in range(len(DataPoints)):
        x = mindist(centroids_list, DataPoints[i])
        indexingList[x].append(i)


def update(centroids_list, DataPoints, indexingList):
    boolean = True
    for i in range(len(centroids_list)):
        old_avg = centroids_list[i]
        centroids_list[i] = Avg(indexingList[i], DataPoints)
        distance = dist(centroids_list[i], old_avg)
        if (distance > 0.001):
            boolean = False

    return boolean


def Avg(lst, DataPoints):
    avg_point = []
    d = len(DataPoints[0])
    for i in range(d):
        sum = 0
        for item in lst:
            sum += DataPoints[item][i]
        sum = sum / len(lst)
        avg_point.append(sum)
    return avg_point


def kmeans(k, max_iter, inputfile, outputfile):

    centroids_list = []
    DataPoints = []

    file = open(inputfile)
    content = file.read()
    DataPoints = content.splitlines()
    for i in range(len(DataPoints)):
        DataPoints[i] = DataPoints[i].split(",")
        for j in range(len(DataPoints[i])):
            DataPoints[i][j] = float(DataPoints[i][j])

    for i in range(k):
        centroids_list.append(DataPoints[i])
    if(k<=1 or k>= len(DataPoints)):
        print("Invalid Input!")
        sys.exit()

    if(max_iter<1):
        print("Invalid Input!")
        sys.exit()


    for iter in range(max_iter):
        indexingList = []
        for i in range(k):
            indexingList.append([])
        clustering(centroids_list, DataPoints, indexingList)
        bol = update(centroids_list, DataPoints, indexingList)
        if (bol == True):
            break

    for i in range(len(centroids_list)):
        for j in range(len(centroids_list[0])):
            a = centroids_list[i][j]
            centroids_list[i][j] = "%.4f" %round(a, 4)



    ff = open(outputfile, 'w')
    for i in range(len(centroids_list)):
        ff.write(','.join([format(centroids_list[i][j]) for j in range(len(centroids_list[i]))]) + '\n')
    ff.close()

import sys
args = sys.argv
maxiter=0

if len(args)==5:
    if (args[1].isdigit() == False or args[2].isdigit() == False):
        print("Invalid Input!")
        sys.exit()

    assert args[1].isdigit() , "Invalid input."
    assert args[2].isdigit(), "Invalid input."
    k = int(args[1])
    maxiter=int(args[2])
    inputfile =args[3]
    outputfile =args[4]
    kmeans(k, maxiter,inputfile,outputfile)
if len(args)==4:
    if(args[1].isdigit()==False):
        print("Invalid Input!")
        sys.exit()

    k = int(args[1])
    maxiter=200
    inputfile = args[2]
    outputfile = args[3]
    kmeans(k, maxiter, inputfile, outputfile)


