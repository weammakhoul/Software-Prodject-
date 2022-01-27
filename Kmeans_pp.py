import pandas as pd
import numpy as np
import mykmeanssp
import argparse
import sys


def dist(point1, point2):
    sum = 0
    d = len(point1)
    for i in range(d):
        sum += (point1[i] - point2[i]) ** 2

    return sum


def kmeansPlus(k, MAX_ITER, filename1, filename2):
    DataPoints = ReadData(k, filename1, filename2)

    Data_indices = DataPoints.iloc[:, :1]
    Data_indices = Data_indices.to_numpy()
    Data_indices = np.array(Data_indices)

    DataPoints = DataPoints.iloc[:, 1:]
    DataPoints = DataPoints.to_numpy()
    DataPoints = np.array(DataPoints)

    rows = DataPoints.shape[0]
    dimension = DataPoints.shape[1]

    if (k >= rows):
        print("Invalid Input!")
        return -1

    centroids = np.ndarray((k, dimension), float)
    centroids_index = np.ndarray(k, int)
    init_Centroids(DataPoints, centroids, centroids_index, k, dimension, rows)
    Data_list = DataPoints.tolist()
    centroids_list = centroids.tolist()
    centroids = mykmeanssp.fit(Data_list, centroids_list, rows, dimension, k, MAX_ITER)
    centroids = np.array(centroids)
    centroids = np.round(centroids, decimals=4)	
    print_centroids(centroids)
    print()
    return None


def print_centroids(centroids):
    for i in range(len(centroids)):
        centroid = centroids[i]
        for j in range(len(centroid)):
            if (j != (len(centroid) - 1)):
                print(str(centroid[j]) + ",", end="")
            else:
                if (i == len(centroids) - 1):
                    print(centroid[j], end="")
                else:
                    print(centroid[j])


def ReadData(k, filename1, filename2):
    DataPoints1 = pd.read_csv(filename1, header=None)
    DataPoints2 = pd.read_csv(filename2, header=None)
    DataPoints = pd.merge(DataPoints1, DataPoints2, on=0)
    DataPoints = DataPoints.sort_values(by=[0])

    return DataPoints


def init_Centroids(DataPoints, centroids, centroids_index, k, dimension, rows):
    sum1 = 0
    D = np.zeros(rows)
    P = np.zeros(rows)

    np.random.seed(0)
    mew = np.random.choice(rows)
    centroids_index[0] = mew
    centroids[0] = DataPoints[mew]

    Z = 1
    while Z < k:
        for i in range(0, rows):
            min = float("inf")
            for j in range(0, Z):
                distance = dist(DataPoints[i], centroids[j])
                if (distance < min):
                    min = distance
            sum1 -= D[i]
            D[i] = min
            sum1 += D[i]

        P = np.divide(D, sum1)
        index1 = np.random.choice(rows, p=P)
        centroids_index[Z] = index1
        centroids[Z] = DataPoints[index1]
        Z += 1
    print(','.join(str(i) for i in centroids_index), flush=True)




def start(): #gets arguments and starts the algorethim.
    parser = argparse.ArgumentParser()
    parser.add_argument("K", type=int, help="K is the number of clusters")
    parser.add_argument("MAX_ITER", nargs="?", type=int, help="The maximum number of the K-means algorithm")
    parser.add_argument("ep", type=float, help="epsilon")
    parser.add_argument("file_name_1", type=str, help="The path to file 1 which contains N observations")
    parser.add_argument("file_name_2", type=str, help="The path to file 2 which contains N observations")
    args = parser.parse_args()
    K = args.K 
    MAX_ITER = args.MAX_ITER
    ep = args.ep
    file_name_1 = args.file_name_1
    file_name_2 = args.file_name_2
    #assertions
    if MAX_ITER == None:
    	MAX_ITER = 300
    if MAX_ITER < 1:
        print("Invalid Input!")
        return -1
    if K == None:
        print("Invalid Input!")
        return -1
    if(K<1):
        print("Invalid Input!")
        return -1
    if (file_name_1 or file_name_2) == None:
        print("Invalid Input!")
        return -1
    kmeansPlus(K, MAX_ITER, file_name_1, file_name_2)

start()
