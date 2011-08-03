from PyQt4.QtCore import Qt
from guiqwt.events import *
from guiqwt.tools import InteractiveTool


class RtSelectionTool(InteractiveTool):
    """
        modified SelectTool from guiqwt.
    """
    TITLE = "mZ Selection"
    ICON = "selection.png"
    CURSOR = Qt.ArrowCursor


    def setup_filter(self, baseplot):
        filter = baseplot.filter
        # Initialisation du filtre
        start_state = filter.new_state()
        # Bouton gauche :
        ObjectHandler(filter, Qt.LeftButton, start_state=start_state)
        ObjectHandler(filter, Qt.LeftButton, mods=Qt.ControlModifier,
                      start_state=start_state, multiselection=True)

        filter.add_event(start_state,
                         KeyEventMatch((Qt.Key_Enter, Qt.Key_Return,)),

                         baseplot.do_enter_pressed, start_state)

        filter.add_event(start_state,
                         KeyEventMatch((Qt.Key_Space,)),
                         baseplot.do_space_pressed, start_state)

        filter.add_event(start_state,
                         KeyEventMatch((Qt.Key_Right,)),
                         baseplot.do_right_pressed, start_state)

        filter.add_event(start_state,
                         KeyEventMatch((Qt.Key_Left,)),
                         baseplot.do_left_pressed, start_state)

        filter.add_event(start_state,
                         KeyEventMatch((Qt.Key_Backspace,)),
                         baseplot.do_backspace_pressed, start_state)

        return setup_standard_tool_filter(filter, start_state)


class MzSelectionTool(InteractiveTool):
    """
        modified SelectTool from guiqwt.
    """
    TITLE = "mZ Selection"
    ICON = "selection.png"
    CURSOR = Qt.CrossCursor

    def setup_filter(self, baseplot):
        filter = baseplot.filter
        # Initialisation du filtre
        start_state = filter.new_state()
        # Bouton gauche :
        ObjectHandler(filter, Qt.LeftButton, start_state=start_state)
        ObjectHandler(filter, Qt.LeftButton, mods=Qt.ControlModifier,
                      start_state=start_state, multiselection=True)

        filter.add_event(start_state,
                         KeyEventMatch((Qt.Key_Space,)),
                         baseplot.do_space_pressed, start_state)

        filter.add_event(start_state,
                         KeyEventMatch((Qt.Key_Backspace,)),
                         baseplot.do_backspace_pressed, start_state)

        start_state = filter.new_state()
        handler = QtDragHandler(filter, Qt.LeftButton, start_state=start_state)
        self.connect(handler, SIG_START_TRACKING, baseplot.start_drag)
        self.connect(handler, SIG_MOVE, baseplot.move_drag)
        self.connect(handler, SIG_STOP_NOT_MOVING, baseplot.stop_drag)
        self.connect(handler, SIG_STOP_MOVING, baseplot.stop_drag)

        return setup_standard_tool_filter(filter, start_state)