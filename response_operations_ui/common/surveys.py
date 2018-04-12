from enum import Enum


class Surveys(Enum):
    """Includes all surveys for the api"""
    ASHE = "ASHE"
    BLOCKS = "Blocks"
    BRES = "BRES"
    BRICKS = "Bricks"
    FDI = "FDI"
    NBS = "NBS"
    PCS = "PCS"
    QBS = "QBS"
    SANDANDGRAVEL = "Sand & Gravel"


class FDISurveys(Enum):
    """Includes all FDI surveys"""
    AOFDI = "AOFDI"
    AIFDI = "AIFDI"
    QIFDI = "QIFDI"
    QOFDI = "QOFDI"
