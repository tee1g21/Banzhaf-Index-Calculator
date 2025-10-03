import powerindex as px
from itertools import combinations, permutations
from math import factorial

"""This information is taken DIRECTLY from the official IPU Parline Database and is available at:
https://data.ipu.org/election-summary/HTML/2251_90.htm
OR
https://data.ipu.org/parliament/PE/PE-LC01/election/PE-LC01-E19900408/

Round no 1: Distribution of seats	 
Political Group	Total
Democratic Front (FREDEMO)	62
American Popular Revolutionary Alliance (APRA)	53
Cambio 90	32
United Left (IU)	16
Socialist Left	4
Moralizador Independent Front	7
National Front of Workers and Peasants (FNTC/FRENATRACA)	3
Independents	3

This solution verifies the answer using a pre-existing python library to calculate Banzhaf values:
https://github.com/maxlit/powerindex

As well as a custom Banzhaf calculation script.
"""


def banzhaf_powerindex(weights, quota):
    """Return normalized Banzhaf indices using the powerindex library."""
    game = px.Game(quota=quota, weights=weights)
    game.calc_banzhaf()

    return game.banzhaf


def banzhaf_custom(weights, quota):
    """
    Compute Banzhaf indices by exhaustive enumeration.

    A player is critical in a coalition if:
      - the coalition (including them) meets the quota,
      - but without them, it fails the quota.
    """
    num_parties = len(weights)
    critical_counts = [0] * num_parties

    # Generate all possible coalitions
    for coalition_size in range(1, num_parties + 1):
        for coalition in combinations(range(num_parties), coalition_size):
            coalition_weight = sum(weights[i] for i in coalition)

            if coalition_weight < quota:
                continue

            for i in coalition:
                if coalition_weight - weights[i] < quota:
                    critical_counts[i] += 1

    total_critical = sum(critical_counts)

    banzhaf_values = [
        c / total_critical if total_critical else 0.0 for c in critical_counts
    ]
    return critical_counts, banzhaf_values


def shapley_powerindex(weights, quota):
    """Return Shapley-Shubik indices using the powerindex library."""
    game = px.Game(quota=quota, weights=weights)
    game.calc_shapley_shubik()

    return game.shapley_shubik


def shapley_custom(weights, quota):
    """Compute Shapley-Shubik indices by enumerating player orderings."""
    num_parties = len(weights)
    pivotal_counts = [0] * num_parties

    for ordering in permutations(range(num_parties)):
        cumulative = 0
        for player in ordering:
            cumulative += weights[player]
            if cumulative >= quota:
                pivotal_counts[player] += 1
                break

    total_permutations = factorial(num_parties)
    shapley_values = [
        count / total_permutations if total_permutations else 0.0
        for count in pivotal_counts
    ]
    return pivotal_counts, shapley_values

def shapley_dp(weights, quota):
    """
    Compute Shapley-Shubik indices using dynamic programming / coalition counting.
    Returns pivotal_counts, shapley_values (same as shapley_custom).
    """
    n = len(weights)
    total_permutations = factorial(n)
    pivotal_counts = [0] * n

    # For each player, count pivotal permutations via DP
    for i, w in enumerate(weights):
        # DP table: dp[s][t] = number of coalitions of size s (without i) summing to t
        dp = [[0] * (quota) for _ in range(n)]  # up to quota-1 is enough
        dp[0][0] = 1

        # build subsets from other players
        for j, wj in enumerate(weights):
            if j == i:
                continue
            # update in reverse to avoid reuse
            for s in range(n-2, -1, -1):
                for t in range(quota-1-wj, -1, -1):
                    dp[s+1][t+wj] += dp[s][t]

        # now count pivot contributions
        for s in range(n):  # size of coalition before i
            for t in range(quota):  # weight of coalition
                if quota - w <= t <= quota-1:
                    count = dp[s][t]
                    if count:
                        pivotal_counts[i] += count * factorial(s) * factorial(n-s-1)

    shapley_values = [count / total_permutations for count in pivotal_counts]
    return pivotal_counts, shapley_values


def main():
    #seats = [62, 53, 32, 16, 4, 7, 3, 3]
    seats = [52,29,9,9,6,4,3,3,3,2]
    total_seats = sum(seats)

    quota = total_seats // 2 + 1

    print("=== Input Data ===")
    print(f"Total seats: {total_seats}")
    print(f"Quota: {quota}")
    print(f"Seats: {seats}\n")

    # Power index
    banzhaf_px = banzhaf_powerindex(seats, quota)
    print("=== Banzhaf via powerindex ===")
    if banzhaf_px is not None:
        values = [round(x * 100, 2) for x in banzhaf_px]
        print(values)

    # Custom implementation
    critical_counts, banzhaf_values = banzhaf_custom(seats, quota)
    values_custom = [round(x * 100, 2) for x in banzhaf_values]
    print("\n=== Banzhaf via custom implementation ===")
    print(values_custom)
    print("\nCritical Counts:", critical_counts)

    shapley_px = shapley_powerindex(seats, quota)
    print("\n=== Shapley-Shubik via powerindex ===")
    if shapley_px is not None:
        shapley_values_px = [round(x, 3) for x in shapley_px]
        print(shapley_values_px)

    shapley_counts, shapley_values = shapley_custom(seats, quota)
    shapley_values_custom = [round(x, 3) for x in shapley_values]
    print("\n=== Shapley-Shubik via custom implementation ===")
    print(shapley_values_custom)
    
    shapley_counts, shapley_values = shapley_dp(seats, quota)
    shapley_values_dp = [round(x, 3) for x in shapley_values]
    print("\n=== Shapley-Shubik via dp implementation ===")
    print(shapley_values_dp)
    print("\nPivotal Counts:", shapley_counts)


if __name__ == "__main__":
    main()
