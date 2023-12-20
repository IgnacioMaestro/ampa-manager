from __future__ import annotations

from typing import Optional


class LevelConstants:
    ID_HH2 = 'HH2'
    ID_HH3 = 'HH3'
    ID_HH4 = 'HH4'
    ID_HH5 = 'HH5'
    ID_LH1 = 'LH1'
    ID_LH2 = 'LH2'
    ID_LH3 = 'LH3'
    ID_LH4 = 'LH4'
    ID_LH5 = 'LH5'
    ID_LH6 = 'LH6'

    @classmethod
    def obtain_level_from_str(cls, level: str) -> Optional[str]:
        if level == 'HH2':
            return LevelConstants.ID_HH2
        elif level == 'HH3':
            return LevelConstants.ID_HH3
        elif level == 'HH4':
            return LevelConstants.ID_HH4
        elif level == 'HH5':
            return LevelConstants.ID_HH5
        elif level == 'LH1':
            return LevelConstants.ID_LH1
        elif level == 'LH2':
            return LevelConstants.ID_LH2
        elif level == 'LH3':
            return LevelConstants.ID_LH3
        elif level == 'LH4':
            return LevelConstants.ID_LH4
        elif level == 'LH5':
            return LevelConstants.ID_LH5
        elif level == 'LH6':
            return LevelConstants.ID_LH6
        else:
            return None


