from enum import Enum


class Surveys(Enum):
    """Includes all surveys for the api"""
    ASHE = "ASHE"
    BLOCKS = "Blocks"
    BRICKS = "Bricks"
    FDI = "FDI"
    NBS = "NBS"
    PCS = "PCS"
    QBS = "QBS"
    SANDANDGRAVEL = "Sand & Gravel"
    BRES = "BRES"


class FDISurveys(Enum):
    """Includes all FDI surveys"""
    AOFDI = "AOFDI"
    AIFDI = "AIFDI"
    QIFDI = "QIFDI"
    QOFDI = "QOFDI"
