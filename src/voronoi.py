"""
Create voronoi geometry for grid structure
"""

from scipy.spatial import Voronoi, voronoi_plot_2d
import matplotlib.pyplot as plt
import numpy as np
import sys
import random
from random import randint
import math

def lineIntersection(line1, line2):
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
       raise Exception('lines do not intersect')

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return x, y

def getEndpoint(p, perpen1, perpen2, n):
    mid_x = (perpen1[0] + perpen2[0]) / 2.0
    mid_y = (perpen1[1] + perpen2[1]) / 2.0
    left = [[0, 0], [0, n - 1]]
    right = [[n - 1, 0], [n - 1, n - 1]]
    bottom = [[0, 0], [n - 1, 0]]
    top = [[0, n - 1], [n - 1, n - 1]]
    max_dis = 2 * n
    ans = []
    try:
        cros_left = lineIntersection(left, [p, [mid_x, mid_y]])
        if cros_left[1] >= 0 and cros_left[1] < n:
            dis = math.sqrt((cros_left[0] - mid_x) ** 2 + (cros_left[1] - mid_y) ** 2)
            if dis < max_dis:
                max_dis = dis
                ans = cros_left
    except:
        print("no intersect")
    try:
        cros_right = lineIntersection(right, [p, [mid_x, mid_y]])
        if cros_right[1] >= 0 and cros_right[1] < n:
            dis = math.sqrt((cros_right[0] - mid_x) ** 2 + (cros_right[1] - mid_y) ** 2)
            if dis < max_dis:
                max_dis = dis
                ans = cros_right
    except:
        print("no intersect")
    try:
        cros_bottom = lineIntersection(bottom, [p, [mid_x, mid_y]])
        if cros_bottom[0] >= 0 and cros_bottom[0] < n:
            dis = math.sqrt((cros_bottom[0] - mid_x) ** 2 + (cros_bottom[1] - mid_y) ** 2)
            if dis < max_dis:
                max_dis = dis
                ans = cros_bottom
    except:
        print("no intersect")
    try:
        cros_top = lineIntersection(top, [p, [mid_x, mid_y]])
        if cros_top[0] >= 0 and cros_top[1] < n:
            dis = math.sqrt((cros_top[0] - mid_x) ** 2 + (cros_top[1] - mid_y) ** 2)
            if dis < max_dis:
                max_dis = dis
                ans = cros_top
    except:
        print("no intersect")
    return ans



def initVoro(n, p):
    sigma = 2
    sigma_x = 1

    random.seed(1)
    points = [[randint(0, n), randint(0, n)] for i in range(p)] 
    vor = Voronoi(points)

    matrix = [[0 for i in range(n)] for j in range(n)]
    
    vertices = vor.vertices
    ridge = vor.ridge_vertices
    ridge_point = vor.ridge_points
    lines = []
    for i in range(len(ridge)):
        p1 = ridge[i][0] 
        p2 = ridge[i][1]
        if p1 == -1 and p2 == -1:
            continue
        elif p1 == -1 or p2 == -1:
            perpen1 = points[ridge_point[i][0]]
            perpen2 = points[ridge_point[i][1]]
            if p1 == -1:

                cross = getEndpoint(vertices[p2], perpen1, perpen2, n)
                if len(cross) < 2:
                    continue
                x1, y1 = cross
                x2 = vertices[p2][0]
                y2 = vertices[p2][1]
            else:
                cross = getEndpoint(vertices[p1], perpen1, perpen2, n)
                if len(cross) < 2:
                    continue
                x2, y2 = cross
                x1 = vertices[p1][0]
                y1 = vertices[p1][1]

        else:
            x1 = vertices[p1][0]
            y1 = vertices[p1][1]
            x2 = vertices[p2][0]
            y2 = vertices[p2][1]

        if abs(x1 - x2) > 1:
            slope = float(y1 - y2) / (x1 - x2)
            lines.append([min(x1, x2), max(x1, x2), x1, y1, slope, min(y1, y2), max(y1, y2)])
        else:
            lines.append([min(x1, x2), max(x1, x2), min(y1, y2), max(y1, y2)])

    for i in range(n):
        for j in range(n):
            for line in lines:
                if len(line) == 7:
                    if line[1] - line[0] < 3:
                        if i >= (line[0] - sigma_x) and i <= (line[1] + sigma_x) and j >= line[5] and j <= line[6]:  
                            if abs((i - line[2]) * line[4] - (j - line[3])) <=  abs(line[4] * sigma):
                                matrix[i][j] = 1
                    elif abs(line[4]) > 1:
                        if i >= (line[0]) and i <= (line[1]) and j >= line[5] and j <= line[6]:

                            if abs((i - line[2]) * line[4] - (j - line[3])) <=  abs(line[4] * sigma):
                                matrix[i][j] = 1

                    else:
                        if i >= (line[0]) and i <= (line[1]):
                            if abs((i - line[2]) * line[4] - (j - line[3])) <=  abs(sigma):
                                matrix[i][j] = 1
                else:
                    if i >= (line[0] - sigma_x) and i <= (line[1] + sigma_x) and j >= line[2] and j <= line[3]:
                        matrix[i][j] = 1
    return matrix


