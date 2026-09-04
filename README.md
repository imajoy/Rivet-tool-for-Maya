# Rivet — Poly & NURBS Surface Pinning Tool for Maya

<p align="center">
  <strong>A modern Python conversion of the classic Maya Rivet workflow.</strong>
</p>

<p align="center">
  <a href="https://github.com/imajoy/rivet-maya">GitHub</a>
  ·
  <a href="https://ajoyp.gumroad.com/l/cmljjj">Gumroad</a>
</p>

---

## Overview

**Rivet** creates a locator that stays attached to a live polygon mesh or
NURBS surface.

It is useful for attaching controls, props, buttons, secondary geometry,
or other rigging elements to a deforming surface without requiring skin
weighting.

This project is a **Python conversion and reimplementation of the classic
Rivet MEL workflow originally created by Michael Bazhutkin / studio
Klassika in 2000–2001**. The original copyright attribution is retained
in the source and license.

The Python version is designed to provide the same classic rivet workflow
inside modern Maya Python environments, with improved selection validation
and a custom Maya-friendly warning dialog.

---

## ✨ Features

### Polygon Mesh Rivet

Select exactly **two polygon edges on the same mesh** and create a rivet
locator at the center of the resulting surface construction.

The tool builds a small curve loft between the selected edges and uses the
center of that loft to drive the rivet.

### NURBS Surface Rivet

Select exactly **one point on a NURBS surface** and create a rivet locator
directly at that surface position.

### Live Surface Follow

The generated locator remains connected to the surface, allowing controls,
props, geometry, or other rig elements parented under it to follow the
surface as it deforms.

### Automatic Orientation

The rivet uses surface position, normal, and tangent information to orient
the locator relative to the surface.

### Smart Selection Validation

The tool checks the current component selection before creating the rivet.

Invalid selections are reported through a custom warning dialog instead of
leaving only a Python traceback in the Script Editor.

### Maya-Friendly UI

Invalid-selection warnings use a dark PySide interface designed to fit
naturally into the Maya environment.

### PySide2 / PySide6 Support

The tool uses:

- **PySide2** when available
- **PySide6** as a fallback for newer Maya versions

### Named Rivets

You can optionally provide a custom name when creating a rivet:

```python
rivet.rivet("myRivet")
