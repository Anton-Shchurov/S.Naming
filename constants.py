# Constants
# URL to the Excel file with the distribution table
URL = "https://globalteamgf-my.sharepoint.com/:x:/g/personal/a_shchurov_glassfordglobal_rs/EVUH6ebvB6pFg4w-8n-x2Y4B3dtIefUJVxjHJ86jmSpisQ?download=1"

# Constants for customtkinter
FONT = ('CoFo Sans Medium', 18)
BORDER_WIDTH = 4
CORNER_RADIUS = 15
BLUE_COLOR = '#007bfb'
WRAP = 'word'

PADX_LABEL = 0
PADY_LABEL = (0, 10)

PADX_OPTMENU = 40
PADY_OPTMENU = (40, 0)

PADX_CHECKBOX = 40
PADY_CHECKBOX = 40

STICKY_UP = 'NEW'
STICKY_ALL = 'NSEW'

# Constants for name generation
# Field "Section"
SECTION = "00"

# Field "Discipline"
DISCIPLINE = [
    'ES',  # Engineering Surveys
    'MP',  # Master Plan
    'LD',  # Land Development
    'SW',  # Sewage
    'SD',  # Storm Drainage
    'WS',  # Water Supply
    'HN',  # Heating Networks
    'PS',  # Power Supply
    'LT'   # Lighting
]

# Field "Set"
SET = [
    'EEN',     # External Engineering Networks
    'LPP',     # Land Plot Plan
    'LD1',     # Land Development 1
    'LD2.1',   # Land Development 2.1
    'LD2.2'    # Land Development 2.2
]

# Field "Description" for model files
MODEL_NAME = [
    'M-MAIN',  # Main
    'M-DISM',  # Dismantling
    'M-SAF',   # Small Architectural Forms
    'M-GRN',   # Greening
    'M-RP',    # Relief Plan
    'M-CPE',   # Combined Plan of Engineering Networks
    'M-SRN'    # Street Road Network
]

# Field "Description" for sheet files
SHEET_NAME = [
    'S-SP',    # Situation Plan
    'S-SPOT',  # SPOT Plan
    'S-SAF',   # Small Architectural Forms
    'S-GRN',   # Greening
    'S-RP',    # Relief Plan
    'S-LDP',   # Land Plot Development Plan
    'S-CPE',   # Combined Plan of Engineering Networks
    'S-PS'     # Pavement Structure
]
