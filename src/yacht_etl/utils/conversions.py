import pandas as pd

def ft_in_to_ft(ft, inch):
    ft = pd.to_numeric(ft, errors="coerce")
    inch = pd.to_numeric(inch, errors="coerce")
    return ft + inch / 12.0