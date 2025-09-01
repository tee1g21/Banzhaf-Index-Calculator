import powerindex as px
from typing import List, Tuple
from itertools import combinations

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


def main():
    total_seats = 180
    seats = [62, 53, 32, 16, 4, 7, 3, 3]
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
        print("  Order of Party (%):", values)
        print("Descending order (%):", sorted(values, reverse=True), "\n")

    # Custom implementation
    critical_counts, banzhaf_values = banzhaf_custom(seats, quota)
    values_custom = [round(x * 100, 2) for x in banzhaf_values]
    print("=== Banzhaf via custom implementation ===")
    print("  Order of Party (%):", values_custom)
    print("Descending order (%):", sorted(values_custom, reverse=True))
    print("\nCritical Counts:", critical_counts)


if __name__ == "__main__":
    main()