# Simple static mapping for demonstration
COMPANY_NAME_TO_TICKER = {
    "Banco Santander": "SAN",
    "BBVA": "BBVA",
    "CaixaBank": "CABK.MC",
    "Bankinter": "BKT.MC",
    "Banco Sabadell": "SAB.MC",
    "Mapfre": "MAP.MC",
    "Iberdrola": "IBE.MC",
    "Endesa": "ELE.MC",
    "Naturgy": "NTGY.MC",
    "Repsol": "REP.MC",
    "Telefonica": "TEF.MC",
    "Cellnex": "CLNX.MC",
    "Ferrovial": "FER.MC",
    "ACS": "ACS.MC",
    "Aena": "AENA.MC",
    "Amadeus": "AMS.MC",
    "Grifols": "GRF.MC",
    "Inditex": "ITX.MC",
    "Indra": "IDR.MC",
    "Meliá Hotels": "MEL.MC",
    "Red Eléctrica": "REE.MC",
    "Siemens Gamesa": "SGRE.MC",
    "Acciona": "ANA.MC",
    "Enagás": "ENG.MC",
    "Sacyr": "SCYR.MC",
    "Viscofan": "VIS.MC",
    "Solaria": "SLR.MC",
    "Colonial": "COL.MC",
    "Merlin Properties": "MRL.MC",
    # Add more as needed
}

def get_ticker_from_name(name: str) -> str | None:
    """Return the ticker for a given company name, or None if not found."""
    return COMPANY_NAME_TO_TICKER.get(name)

# Stub for future dynamic lookup (e.g., Yahoo autocomplete API)
def get_ticker_dynamic(name: str) -> str | None:
    # TODO: Implement dynamic lookup using Yahoo Finance autocomplete or similar
    return None 