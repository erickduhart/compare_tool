from pathlib import Path
import sys


# Paths / config
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.append(str(SRC))

    
DATA_DIR = ROOT / "data"
NEW_DATA_DIR = ROOT / "data_new"
BASE_TEMPLATE_PATH = DATA_DIR / "base_yacht_master.csv"
OUTPUT_PATH = NEW_DATA_DIR / "yachts_master.csv"


# const
M_TO_FT = 3.28084
COLOR_A = "#000000"
COLOR_B = "#C5C7C4"
COLOR_REG = "#ff3366"
COLOR_CHARTS = "#3889b9"
COLOR_LINES = "#666666"

__version__ = "v0.0205 prev"
APP_TITLE = "Yachts Comparison Dashboard"