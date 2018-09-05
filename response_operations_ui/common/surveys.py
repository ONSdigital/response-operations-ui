from enum import Enum


class Surveys(Enum):
    """Includes all surveys for the api"""
    ASHE = "ASHE"
    BLOCKS = "Blocks"
    BRES = "BRES"
    BRICKS = "Bricks"
    FDI = "FDI"
    GOVERD = "GovERD"
    MBS = "MBS"
    MWSS = "MWSS"
    NBS = "NBS"
    OFATS = "OFATS"
    PCS = "PCS"
    QBS = "QBS"
    QCAS = "QCAS"
    RSI = "RSI"
    SANDANDGRAVEL = "Sand & Gravel"


class FDISurveys(Enum):
    """Includes all FDI surveys"""
    AOFDI = "AOFDI"
    AIFDI = "AIFDI"
    QIFDI = "QIFDI"
    QOFDI = "QOFDI"
