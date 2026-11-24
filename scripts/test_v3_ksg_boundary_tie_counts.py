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

    # Type II uses separate marginal radii taken from the same kth joint
    # neighbour, not the joint-space max radius in both marginals.
    joint = np.column_stack([x, y])
    _, indices = cKDTree(joint).query(joint, k=k + 1, p=np.inf)
    kth_index = int(indices[0, k])
    radius_x = abs(float(x[0] - x[kth_index]))
    radius_y = abs(float(y[0] - y[kth_index]))
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
    assert tied_type_ii["type_ii_marginal_radii"] in ([1.0, 0.0], [0.0, 1.0])
    assert tied_type_ii["type_ii_counts_including_self"] in ([3, 2], [2, 3])

    print({
        "status": "passed",
        "unique_boundary": unique,
        "unique_type_ii": unique_type_ii,
        "tied_kth_boundary": tied,
        "tied_type_ii": tied_type_ii,
        "interpretation": (
            "Strict and inclusive inequalities produce the expected counts; "
            "self-count conversion for the Type-I digamma term is algebraically consistent."
        ),
    })


if __name__ == "__main__":
    main()
