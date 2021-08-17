from geopy.distance import geodesic
from itertools import product, combinations_with_replacement
import pandas as pd


def distances_table(df, permute=False) -> pd.DataFrame:
    cities1, cities2, distances = [], [], []
    if permute:
        iterator = product(list(df.index), repeat=2)
    else:
        iterator = combinations_with_replacement(list(df.index), 2)

    for city1, city2 in iterator:
        cities1.append(city1)
        cities2.append(city2)
        g_city1 = (df.at[city1, 'lat'], df.at[city1, 'long'])
        g_city2 = (df.at[city2, 'lat'], df.at[city2, 'long'])
        distances.append(geodesic(g_city1, g_city2).km)

    return pd.DataFrame({'city1': cities1, 'city2': cities2, 'dist': distances})


def get_distance(node1, node2, df_dist):
    df = df_dist.loc[(df_dist.city1 == node1) & (df_dist.city2 == node2)]
    if len(df) == 0:
        df = df_dist.loc[(df_dist.city1 == node2) & (df_dist.city2 == node1)]
    return df.at[list(df.index)[0], 'dist']