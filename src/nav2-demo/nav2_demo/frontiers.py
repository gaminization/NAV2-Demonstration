"""Frontier detection for autonomous exploration (pure numpy, no ROS imports).

A frontier cell is a FREE cell that touches an UNKNOWN cell. Driving to a frontier
reveals new map, so repeating this until no frontiers remain maps the whole space.
"""
import math
from collections import deque

import numpy as np

UNKNOWN = -1


def find_frontier_cells(grid, free_threshold=50):
    """grid: 2D int array [row=y, col=x] using OccupancyGrid values (-1, 0..100).
    Returns a boolean mask of frontier cells."""
    grid = np.asarray(grid)
    free = (grid >= 0) & (grid < free_threshold)
    unknown = grid == UNKNOWN
    near_unknown = np.zeros_like(unknown)
    near_unknown[1:, :] |= unknown[:-1, :]
    near_unknown[:-1, :] |= unknown[1:, :]
    near_unknown[:, 1:] |= unknown[:, :-1]
    near_unknown[:, :-1] |= unknown[:, 1:]
    return free & near_unknown


def cluster_frontiers(mask, min_size=5):
    """Group frontier cells into 8-connected clusters. Returns a list of lists of
    (row, col) tuples, dropping clusters smaller than min_size."""
    rows, cols = mask.shape
    seen = np.zeros_like(mask, dtype=bool)
    clusters = []
    for r0, c0 in zip(*np.nonzero(mask)):
        if seen[r0, c0]:
            continue
        queue = deque([(int(r0), int(c0))])
        seen[r0, c0] = True
        cluster = []
        while queue:
            r, c = queue.popleft()
            cluster.append((r, c))
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    nr, nc = r + dr, c + dc
                    if (0 <= nr < rows and 0 <= nc < cols
                            and mask[nr, nc] and not seen[nr, nc]):
                        seen[nr, nc] = True
                        queue.append((nr, nc))
        if len(cluster) >= min_size:
            clusters.append(cluster)
    return clusters


def cluster_target(cluster):
    """The cluster cell closest to the cluster's mean (always a real frontier cell)."""
    mr = sum(r for r, _ in cluster) / len(cluster)
    mc = sum(c for _, c in cluster) / len(cluster)
    return min(cluster, key=lambda rc: (rc[0] - mr) ** 2 + (rc[1] - mc) ** 2)


def choose_frontier(clusters, robot_cell, resolution, blacklist=(),
                    blacklist_radius_m=0.5, min_goal_distance_m=0.5, size_weight=0.02):
    """Pick the best frontier target (row, col), or None.

    score = distance_m - size_weight * cluster_size   (near and big is good)
    Targets near a blacklisted (previously failed) goal or too close to the robot are skipped.
    """
    best, best_score = None, math.inf
    for cluster in clusters:
        target = cluster_target(cluster)
        dist = math.hypot(target[0] - robot_cell[0], target[1] - robot_cell[1]) * resolution
        if dist < min_goal_distance_m:
            continue
        if any(math.hypot(target[0] - b[0], target[1] - b[1]) * resolution < blacklist_radius_m
               for b in blacklist):
            continue
        score = dist - size_weight * len(cluster)
        if score < best_score:
            best, best_score = target, score
    return best


def cell_to_world(cell, origin_xy, resolution):
    row, col = cell
    return (origin_xy[0] + (col + 0.5) * resolution,
            origin_xy[1] + (row + 0.5) * resolution)


def world_to_cell(xy, origin_xy, resolution):
    return (int((xy[1] - origin_xy[1]) / resolution),
            int((xy[0] - origin_xy[0]) / resolution))
