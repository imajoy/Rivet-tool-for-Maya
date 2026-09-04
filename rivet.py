"""
rivet.py

Python conversion of the classic MEL "Rivet" script:
    Copyright (C) 2000-2001 Michael Bazhutkin - Copyright (C) 2000 studio Klassika
    Rivet (button) 1.0 - Creation Date: April 13, 2001

Use "rivet()" to constrain a locator to a polygon or NURBS surface:
    - Select two edges on a polygon object, then call rivet()
      (a mini curve-loft is built between the edges and sampled at its
      center -- the classic technique for pinning to a poly mesh).
    - Or select one surface point on a NURBS surface, then call rivet().

Parent your controls/geometry to the returned locator.

Converted for Maya 2018+ (Python 2.7 / Python 3, maya.cmds -- nothing in
this file requires Python 3). Functionally identical to the original MEL,
with two changes:
    1. The original connected a mesh's ".w" attribute into
       curveFromMeshEdge.inputMesh. That attribute doesn't exist on a mesh
       node (and doesn't in any version of Maya, as far as current
       documentation shows) -- the correct world-space mesh output is
       ".worldMesh[0]".
    2. Invalid selections are reported with a custom dark-themed PySide
       popup (matching the "Revert to Last Saved" tool's dialog style)
       instead of raising a Python exception, so running the tool with a
       bad selection shows a proper on-screen dialog rather than a
       Script-Editor-only traceback.
Everything else (node types, attributes, the aimConstraint trick) matches
the original.
"""

import re

import maya.cmds as cmds
import maya.OpenMayaUI as omui

try:
    from PySide2 import QtCore, QtWidgets
    from shiboken2 import wrapInstance
except ImportError:
    # Maya 2025+ ships PySide6/shiboken6 instead.
    from PySide6 import QtCore, QtWidgets
    from shiboken6 import wrapInstance


def _maya_main_window():
    """Return Maya's main window as a QWidget, for use as a dialog parent."""
    main_window_ptr = omui.MQtUtil.mainWindow()
    if main_window_ptr is None:
        return None
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


class _RivetWarningDialog(QtWidgets.QDialog):
    """
    Dark-themed warning popup for reporting an invalid Rivet selection.
    Styling matches the "Revert to Last Saved" tool's dialog: #242526
    background, icon + message row, centered OK button, "(c) AJOY"
    footer credit.
    """

    def __init__(self, message, parent=None):
        super(_RivetWarningDialog, self).__init__(parent)
        self.setWindowTitle("Rivet")
        self.setModal(True)
        self.setFixedWidth(340)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        self.setStyleSheet(
            """
            QDialog {
                background-color: #242526;
            }
            QLabel {
                color: #dcdcdc;
                font-size: 12px;
            }
            QLabel#footerLabel {
                color: #6e6e6e;
                font-size: 10px;
            }
            QPushButton {
                background-color: #3a3b3c;
                color: #dcdcdc;
                border: 1px solid #4a4b4c;
                border-radius: 4px;
                padding: 6px 20px;
            }
            QPushButton:hover {
                background-color: #46474a;
            }
            QPushButton:pressed {
                background-color: #2f3031;
            }
            """
        )

        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 12)
        root.setSpacing(16)

        message_row = QtWidgets.QHBoxLayout()
        message_row.setSpacing(14)

        icon_label = QtWidgets.QLabel()
        warning_icon = self.style().standardIcon(QtWidgets.QStyle.SP_MessageBoxWarning)
        icon_label.setPixmap(warning_icon.pixmap(32, 32))
        icon_label.setAlignment(QtCore.Qt.AlignTop)
        message_row.addWidget(icon_label)

        text_label = QtWidgets.QLabel(message)
        text_label.setWordWrap(True)
        message_row.addWidget(text_label, 1)

        root.addLayout(message_row)

        button_row = QtWidgets.QHBoxLayout()
        button_row.addStretch()
        ok_button = QtWidgets.QPushButton("OK")
        ok_button.setFixedWidth(90)
        ok_button.setDefault(True)
        ok_button.clicked.connect(self.accept)
        button_row.addWidget(ok_button)
        button_row.addStretch()
        root.addLayout(button_row)

        footer_label = QtWidgets.QLabel(u"\u00A9 AJOY")
        footer_label.setObjectName("footerLabel")
        footer_label.setAlignment(QtCore.Qt.AlignRight)
        root.addWidget(footer_label)


def _warn(message):
    """
    Report an invalid selection with the tool's custom dark PySide
    popup. Also echoes to cmds.warning() so the message is still
    visible in the Script Editor history.
    """
    cmds.warning(message)
    dialog = _RivetWarningDialog(message, parent=_maya_main_window())
    if hasattr(dialog, "exec_"):
        dialog.exec_()
    else:
        dialog.exec()


def _object_and_indices(component_name):
    """
    Split a component name like "pCubeShape1.e[3]" or
    "nurbsPlaneShape1.uv[0.5][0.25]" into the object name and a list of
    the numeric indices found inside the trailing [...] blocks.
    """
    object_name = component_name.split(".", 1)[0]
    indices = [float(value) for value in re.findall(r"\[([^\[\]]+)\]", component_name)]
    return object_name, indices


def rivet(name=None):
    """
    Create a rivet locator based on the current selection.

    Selection must be either:
        - exactly two polygon edges on the same mesh, or
        - exactly one NURBS surface point (Surface Point component)

    Args:
        name (str, optional): rename the resulting locator to this name.

    Returns:
        str: name of the created locator transform, or None if the
            selection was invalid. On an invalid selection, Maya's
            standard warning popup is shown and nothing is created.
    """
    point_on_surface = None

    # expand=True forces individually-listed components rather than a
    # compacted range string (e.g. "pCube1.e[3:4]"), which the size==2
    # check below depends on.
    edges = cmds.filterExpand(selectionMask=32, expand=True) or []

    cmds.undoInfo(openChunk=True)
    try:
        if edges:
            if len(edges) != 2:
                _warn("Rivet: select exactly two polygon edges.")
                return None

            node_object, idx1 = _object_and_indices(edges[0])
            other_object, idx2 = _object_and_indices(edges[1])
            if node_object != other_object:
                _warn("Rivet: both edges must belong to the same mesh.")
                return None
            edge_index_1 = int(idx1[0])
            edge_index_2 = int(idx2[0])

            curve_from_edge_1 = cmds.createNode("curveFromMeshEdge", name="rivetCurveFromMeshEdge1")
            cmds.setAttr(curve_from_edge_1 + ".isHistoricallyInteresting", 1)
            cmds.setAttr(curve_from_edge_1 + ".edgeIndex[0]", edge_index_1)

            curve_from_edge_2 = cmds.createNode("curveFromMeshEdge", name="rivetCurveFromMeshEdge2")
            cmds.setAttr(curve_from_edge_2 + ".isHistoricallyInteresting", 1)
            cmds.setAttr(curve_from_edge_2 + ".edgeIndex[0]", edge_index_2)

            loft = cmds.createNode("loft", name="rivetLoft1")
            cmds.setAttr(loft + ".inputCurve", size=2)
            cmds.setAttr(loft + ".uniform", 1)
            cmds.setAttr(loft + ".reverseSurfaceNormals", 1)

            point_on_surface = cmds.createNode("pointOnSurfaceInfo", name="rivetPointOnSurfaceInfo1")
            cmds.setAttr(point_on_surface + ".turnOnPercentage", 1)
            cmds.setAttr(point_on_surface + ".parameterU", 0.5)
            cmds.setAttr(point_on_surface + ".parameterV", 0.5)

            cmds.connectAttr(loft + ".outputSurface", point_on_surface + ".inputSurface", force=True)
            cmds.connectAttr(curve_from_edge_1 + ".outputCurve", loft + ".inputCurve[0]")
            cmds.connectAttr(curve_from_edge_2 + ".outputCurve", loft + ".inputCurve[1]")
            # .worldMesh[0] is the corrected attribute -- see module docstring.
            cmds.connectAttr(node_object + ".worldMesh[0]", curve_from_edge_1 + ".inputMesh")
            cmds.connectAttr(node_object + ".worldMesh[0]", curve_from_edge_2 + ".inputMesh")

        else:
            points = cmds.filterExpand(selectionMask=41, expand=True) or []
            if not points:
                _warn("Rivet: select two polygon edges, or one point on a NURBS surface.")
                return None
            if len(points) != 1:
                _warn("Rivet: select exactly one surface point.")
                return None

            node_object, uv = _object_and_indices(points[0])
            u, v = uv[0], uv[1]

            point_on_surface = cmds.createNode("pointOnSurfaceInfo", name="rivetPointOnSurfaceInfo1")
            cmds.setAttr(point_on_surface + ".turnOnPercentage", 0)
            cmds.setAttr(point_on_surface + ".parameterU", u)
            cmds.setAttr(point_on_surface + ".parameterV", v)

            cmds.connectAttr(node_object + ".worldSpace[0]", point_on_surface + ".inputSurface", force=True)

        # --- Locator + aim constraint (identical for both branches) ---
        locator_transform = cmds.createNode("transform", name="rivet1")
        cmds.createNode("locator", name=locator_transform + "Shape", parent=locator_transform)

        aim_constraint = cmds.createNode(
            "aimConstraint", name=locator_transform + "_rivetAimConstraint1", parent=locator_transform
        )
        cmds.setAttr(aim_constraint + ".target[0].targetWeight", 1)
        cmds.setAttr(aim_constraint + ".aimVector", 0, 1, 0, type="double3")
        cmds.setAttr(aim_constraint + ".upVector", 0, 0, 1, type="double3")
        for attr in ("v", "tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"):
            cmds.setAttr(aim_constraint + "." + attr, keyable=False, channelBox=False)

        # Note: constraintParentInverseMatrix is deliberately left unconnected.
        # Because target[0].targetParentMatrix also stays at identity, feeding
        # the surface normal directly into targetTranslate makes the constraint
        # aim along that normal *direction* rather than toward a fixed point --
        # this is the original script's trick, preserved as-is.
        cmds.connectAttr(point_on_surface + ".position", locator_transform + ".translate")
        cmds.connectAttr(point_on_surface + ".normal", aim_constraint + ".target[0].targetTranslate")
        cmds.connectAttr(point_on_surface + ".tangentV", aim_constraint + ".worldUpVector")
        cmds.connectAttr(aim_constraint + ".constraintRotateX", locator_transform + ".rotateX")
        cmds.connectAttr(aim_constraint + ".constraintRotateY", locator_transform + ".rotateY")
        cmds.connectAttr(aim_constraint + ".constraintRotateZ", locator_transform + ".rotateZ")

        if name:
            locator_transform = cmds.rename(locator_transform, name)

        cmds.select(locator_transform, replace=True)
        return locator_transform

    finally:
        cmds.undoInfo(closeChunk=True)


if __name__ == "__main__":
    rivet()
