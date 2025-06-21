from __future__ import annotations
import logging
from types import ModuleType
from typing_extensions import Literal, TypeAlias

GUIType: TypeAlias = Literal['edgechromium']
logger = logging.getLogger('idepy')
guilib: ModuleType | None = None
forced_gui_: GUIType | None = None


def initialize(forced_gui: GUIType | None = None):

    def import_winforms():
        global guilib

        try:
            import idepy_next.platforms.winforms as guilib

            return True
        except ImportError:
            logger.exception('pythonnet cannot be loaded')
            return False

    import_winforms()
    guilib.setup_app()
    return guilib
