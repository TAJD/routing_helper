"""Python code to support domain point generation."""
import numpy as np
import pyproj
from shapely.geometry import Point


def line_points(x, y, n_nodes, dist):
    """Calculate the locations of the points along a rank."""
    p_ll = pyproj.Proj(init='epsg:4326')
    p_mt = pyproj.Proj(init='epsg:3857')
    g = pyproj.Geod(ellps='clrk66')
    tran = pyproj.transform(p_ll, p_mt, x, y)
    upper = Point((tran[0], tran[1]+dist*n_nodes/2))
    lower = Point((tran[0], tran[1]-dist*n_nodes/2))
    tran_upper = pyproj.transform(p_mt, p_ll, upper.x, upper.y)
    tran_lower = pyproj.transform(p_mt, p_ll, lower.x, lower.y)
    points = g.npts(tran_upper[0], tran_upper[1],
                    tran_lower[0], tran_lower[1], n_nodes-2)
    return np.vstack((np.array(tran_upper), np.array(points),
                     np.array(tran_lower)))


def gen_grid(start_long, finish_long, start_lat, finish_lat,
             n_ranks, n_nodes, dist):
    """Return grid between start and finish locations.
 
    Dist needs to be in metres."""
    g = pyproj.Geod(ellps='clrk66')
    dist *= 1.852001*1000.0
    azimuths = g.inv(start_long, start_lat, finish_long, finish_lat)
    rot = azimuths[0]-90.0
    height = dist * np.sin(rot) + dist * np.cos(rot)
    great_circle = g.npts(start_long, start_lat, finish_long, finish_lat,
                          n_ranks)
    grid = [line_points(g[0], g[1], n_nodes, height) for g in great_circle]
    return grid


def gen_indx(x_locs):
    """
    Return the indexes for each node to be iterated over.

    Uses the x_locs array as an array to mimic.
    """
    n_elem = x_locs.shape[0] * x_locs.shape[1]
    indx = np.arange(n_elem).reshape(x_locs.shape[0], x_locs.shape[1])
    pindx = np.zeros_like(indx)
    pindx[:] = -1
    return indx, pindx


def return_co_ords(start_long, finish_long, start_lat, finish_lat,
                   n_ranks=10, n_nodes=10, dist=5000):
    """Return grid co-ordinates between start and finish over the Earths surface."""
    grid = gen_grid(start_long, finish_long, start_lat, finish_lat,
                    n_ranks, n_nodes, dist)
    g = np.reshape(grid, (1, -1))
    x = np.reshape(g[0][::2], (n_ranks, n_nodes))
    y = np.reshape(g[0][1::2], (n_ranks, n_nodes))
    return np.around(x, decimals=6), np.around(y, decimals=6)

