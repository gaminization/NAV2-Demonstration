import numpy as np

from nav2_demo import frontiers as fr


def _room():
    """10x10 map: free interior, wall border, unknown strip on the right side."""
    g = np.full((10, 10), 0, dtype=np.int16)
    g[0, :] = g[-1, :] = g[:, 0] = 100
    g[:, 9] = -1            # unknown column
    g[:, 8] = 0
    return g


def test_frontier_cells_touch_unknown():
    mask = fr.find_frontier_cells(_room())
    assert mask[:, 8].sum() >= 8          # free cells next to the unknown column
    assert not mask[:, 1:7].any()          # interior is not a frontier


def test_fully_known_map_has_no_frontier():
    g = np.zeros((6, 6), dtype=np.int16)
    assert not fr.find_frontier_cells(g).any()


def test_clustering_and_min_size():
    mask = fr.find_frontier_cells(_room())
    assert len(fr.cluster_frontiers(mask, min_size=3)) == 1
    assert fr.cluster_frontiers(mask, min_size=50) == []


def test_choose_prefers_near_and_respects_blacklist():
    near = [(5, 2)] * 6
    far = [(5, 9)] * 6
    robot = (5, 0)
    assert fr.choose_frontier([near, far], robot, 0.5, min_goal_distance_m=0.5) == (5, 2)
    assert fr.choose_frontier([near, far], robot, 0.5, blacklist=[(5, 2)],
                              min_goal_distance_m=0.5) == (5, 9)


def test_too_close_goal_is_skipped():
    assert fr.choose_frontier([[(5, 1)] * 6], (5, 0), 0.05, min_goal_distance_m=0.5) is None


def test_cell_world_round_trip():
    xy = fr.cell_to_world((10, 20), (-1.0, -2.0), 0.05)
    assert fr.world_to_cell(xy, (-1.0, -2.0), 0.05) == (10, 20)
