"""Hand-check KSG marginal boundary and self-count conventions.

Small deterministic cases make kth-radius boundaries and exact ties inspectable.
This is a count-convention test, not an estimator certification.
"""
import numpy as np
from scipy.spatial import cKDTree
from scipy.special import digamma


def marginal_counts(x, y, k, index, mode):
    joint = np.column_stack([x, y])
    distances, _ = cKDTree(joint).query(joint, k=k + 1, p=np.inf)
    radius = float(distances[index, k])
    if mode == "strict":
        query_radius = np.nextafter(radius, -np.inf)
    elif mode == "inclusive":
        query_radius = radius
    else:
        raise ValueError(mode)
    nx = cKDTree(np.asarray(x).reshape(-1, 1)).query_ball_point(
        [x[index]], r=query_radius, p=np.inf, return_length=True
    )
    ny = cKDTree(np.asarray(y).reshape(-1, 1)).query_ball_point(
        [y[index]], r=query_radius, p=np.inf, return_length=True
    )
    # Independent brute-force counts guard against relying on the same tree API.
    brute_x = int(np.count_nonzero(np.abs(x - x[index]) <= query_radius))
    brute_y = int(np.count_nonzero(np.abs(y - y[index]) <= query_radius))
    assert int(nx) == brute_x, (nx, brute_x, mode)
    assert int(ny) == brute_y, (ny, brute_y, mode)
    return radius, int(nx), int(ny)


def check_case(name, x, y, k, expected):
    strict = marginal_counts(x, y, k, 0, "strict")
    inclusive = marginal_counts(x, y, k, 0, "inclusive")
    observed = {
        "radius": strict[0],
        "strict_including_self": [strict[1], strict[2]],
        "inclusive_including_self": [inclusive[1], inclusive[2]],
    }
    assert observed == expected, (name, observed, expected)

    # Type-I psi(n_x+1) with self-excluded neighbour counts is psi(strict
    # count including self).
    strict_other_x, strict_other_y = strict[1] - 1, strict[2] - 1
    assert np.isclose(digamma(strict_other_x + 1), digamma(strict[1]))
    assert np.isclose(digamma(strict_other_y + 1), digamma(strict[2]))
    assert inclusive[1] >= 1 and inclusive[2] >= 1

    # Type II uses separate marginal radii: maximum X and Y projections
    # across the k nearest joint-space neighbours. Different neighbours may
    # determine the two radii.
    joint = np.column_stack([x, y])
    _, indices = cKDTree(joint).query(joint, k=k + 1, p=np.inf)
    neighbour_indices = indices[0, 1 : k + 1]
    radius_x = float(np.max(np.abs(x[0] - x[neighbour_indices])))
    radius_y = float(np.max(np.abs(y[0] - y[neighbour_indices])))
    type_ii_x = int(cKDTree(x.reshape(-1, 1)).query_ball_point(
        [x[0]], r=radius_x, p=np.inf, return_length=True
    ))
    type_ii_y = int(cKDTree(y.reshape(-1, 1)).query_ball_point(
        [y[0]], r=radius_y, p=np.inf, return_length=True
    ))
    return observed, {
        "type_ii_marginal_radii": [radius_x, radius_y],
        "type_ii_counts_including_self": [type_ii_x, type_ii_y],
    }


def brute_force_type_ii_counts(x, y, k):
    """Independent O(N^2) reference for Type-II radii and inclusive counts."""
    n = len(x)
    dx = np.abs(x[:, None] - x[None, :])
    dy = np.abs(y[:, None] - y[None, :])
    joint_distance = np.maximum(dx, dy)
    np.fill_diagonal(joint_distance, np.inf)
    neighbour_indices = np.argsort(joint_distance, axis=1)[:, :k]
    radius_x = np.max(np.take_along_axis(dx, neighbour_indices, axis=1), axis=1)
    radius_y = np.max(np.take_along_axis(dy, neighbour_indices, axis=1), axis=1)
    nx = np.count_nonzero(dx <= radius_x[:, None], axis=1)
    ny = np.count_nonzero(dy <= radius_y[:, None], axis=1)
    return radius_x, radius_y, nx, ny


def tree_type_ii_counts(x, y, k):
    """cKDTree implementation under test, returning radii and inclusive counts."""
    joint = np.column_stack([x, y])
    _, indices = cKDTree(joint).query(joint, k=k + 1, p=np.inf)
    neighbours = indices[:, 1 : k + 1]
    radius_x = np.max(np.abs(x[:, None] - x[neighbours]), axis=1)
    radius_y = np.max(np.abs(y[:, None] - y[neighbours]), axis=1)
    tx, ty = cKDTree(x[:, None]), cKDTree(y[:, None])
    nx = np.array([
        tx.query_ball_point([x[i]], r=radius_x[i], p=np.inf, return_length=True)
        for i in range(len(x))
    ])
    ny = np.array([
        ty.query_ball_point([y[i]], r=radius_y[i], p=np.inf, return_length=True)
        for i in range(len(y))
    ])
    return radius_x, radius_y, nx, ny


def check_type_ii_against_brute_force(name, x, y, k):
    reference = brute_force_type_ii_counts(x, y, k)
    observed = tree_type_ii_counts(x, y, k)
    for label, expected, actual in zip(
        ("radius_x", "radius_y", "nx", "ny"), reference, observed
    ):
        if not np.allclose(expected, actual, rtol=0.0, atol=1e-12):
            raise AssertionError(
                f"{name}: {label} differs; reference={expected}, tree={actual}"
            )
    return {
        "samples": len(x),
        "k": k,
        "status": "matched",
        "radius_x_range": [float(np.min(observed[0])), float(np.max(observed[0]))],
        "radius_y_range": [float(np.min(observed[1])), float(np.max(observed[1]))],
    }


def main():
    # Unique kth boundary: k=1, one neighbour lies exactly at radius 1.
    unique, unique_type_ii = check_case(
        "unique_boundary",
        np.array([0.0, 1.0, 3.0, -4.0]),
        np.array([0.0, 0.0, 3.0, -4.0]),
        1,
        {
            "radius": 1.0,
            "strict_including_self": [1, 2],
            "inclusive_including_self": [2, 2],
        },
    )

    # Tie-heavy kth boundary: two neighbours tie at radius 1 for k=2.
    tied, tied_type_ii = check_case(
        "tied_kth_boundary",
        np.array([0.0, 1.0, 0.0, 2.0, -2.0]),
        np.array([0.0, 0.0, 1.0, 2.0, -2.0]),
        2,
        {
            "radius": 1.0,
            "strict_including_self": [2, 2],
            "inclusive_including_self": [3, 3],
        },
    )

    assert unique_type_ii["type_ii_marginal_radii"] == [1.0, 0.0]
    assert unique_type_ii["type_ii_counts_including_self"] == [2, 2]
    assert tied_type_ii["type_ii_marginal_radii"] == [1.0, 1.0]
    assert tied_type_ii["type_ii_counts_including_self"] == [3, 3]

    rng = np.random.default_rng(20261124)
    random_x = rng.normal(size=40)
    random_y = 0.4 * random_x + rng.normal(size=40)
    random_reference = check_type_ii_against_brute_force(
        "random_continuous", random_x, random_y, 3
    )
    tied_reference = check_type_ii_against_brute_force(
        "tie_heavy", xt, yt, 2
    )

    print({
        "status": "passed",
        "unique_boundary": unique,
        "unique_type_ii": unique_type_ii,
        "tied_kth_boundary": tied,
        "tied_type_ii": tied_type_ii,
        "type_ii_brute_force_crosschecks": [random_reference, tied_reference],
        "interpretation": (
            "Strict and inclusive inequalities produce the expected counts; "
            "self-count conversion for the Type-I digamma term is algebraically consistent."
        ),
    })


if __name__ == "__main__":
    main()
