import pandas as pd

def test_threshold_filtering():
    df = pd.DataFrame({
        "c1": [0.8, 0.6],
        "c2": [0.9, 0.4],
        "c3.1": [0.8, 0.5],
        "c3.2": [0.9, 0.5],
        "c4": [False, False],
        "c5": [False, False],
        "c6": [False, False],
        "c7": [False, False],
    })
    t = 0.7
    df["c1_check"] = df["c1"] >= t
    df["c2_check"] = df["c2"] >= t
    df["c3_check"] = (df["c3.1"] >= t) & (df["c3.2"] >= t)
    filtered = df[df[["c1_check", "c2_check", "c3_check", "c4", "c5", "c6", "c7"]].any(axis=1)]
    assert len(filtered) == 1