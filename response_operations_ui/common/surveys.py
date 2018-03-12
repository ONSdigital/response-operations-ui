from enum import Enum


class Surveys(Enum):
    """Includes all surveys for the api"""
    """should we have all 'active' surveys?"""
    ASHE = "ASHE"
    BLOCKS = "Blocks"
    BRICKS = "Bricks"
    FDI = "FDI"
    NBS = "NBS"
    PCS = "PCS"
    QBS = "QBS"
    SANDANDGRAVEL = "Sand & Gravel"

    survey_list = [ASHE, BLOCKS, BRICKS, FDI, NBS, PCS, QBS]
