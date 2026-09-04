# Rivet — Poly & NURBS Surface Pinning Tool for Maya

<p align="center">
  <strong>Attach controls, props, and geometry to live Maya surfaces with a simple Rivet locator.</strong>
</p>

<p align="center">
  <a href="https://github.com/imajoy/rivet-maya">GitHub</a>
  ·
  <a href="https://ajoyp.gumroad.com">More AJOY Tools</a>
</p>

<p align="center">
  <a href="https://www.youtube.com/shorts/pPo6WNQBRcA">
    <img src="https://i.ytimg.com/vi/pPo6WNQBRcA/hqdefault.jpg"
         alt="▶ Watch Rivet — Poly & NURBS Surface Pinning Tool for Maya"
         width="900">
  </a>
</p>

<p align="center">
  <strong>▶ Watch the Video Demo</strong>
</p>

---

## Overview

**Rivet** creates a locator that stays attached to a live polygon mesh or
NURBS surface.

It is useful for attaching controls, props, buttons, secondary geometry,
or other rigging elements to a deforming surface without requiring skin
weighting.

This project is a **Python conversion and reimplementation of the classic
Maya Rivet MEL workflow originally created by Michael Bazhutkin / studio
Klassika in 2000–2001**.

The Python version brings the Rivet workflow into Maya's Python environment
with improved selection validation, modern PySide support, and a corrected
world-space mesh connection.

---

## Installation

### 1. Download

Download `rivet.py` from this repository:

### 2. Place the Script

Place `rivet.py` in a directory available to Maya's Python path.

### Import and Run

Open Maya's **Script Editor** and switch to the **Python** tab.

Select the required components in Maya, then run:

```python
import importlib
import rivet
importlib.reload(rivet)
rivet.rivet()
```

## Features

### Polygon Mesh Rivet

Select **exactly two polygon edges on the same mesh** and create a rivet
locator at the center of the surface construction.

The tool creates a mini curve loft between the selected edges and samples its
center to position the rivet.

### NURBS Surface Rivet

Select **exactly one point on a NURBS surface** and create a rivet locator
directly at that surface point.

### Live Surface Follow

The generated locator remains connected to the surface.

Any control, prop, geometry, or other object parented under the locator can
follow the surface as it deforms.

### Automatic Orientation

The rivet uses the surface position, normal, and tangent information to
orient the locator relative to the surface.

### Smart Selection Validation

The tool validates the current selection before creating the rivet.

Invalid selections display a custom warning dialog instead of producing an
unhandled error in the Maya Script Editor.

### PySide2 / PySide6 Support

The tool supports both:

- **PySide2**
- **PySide6**

This allows the same script to work across Maya versions using the available
Qt environment.

### Custom Rivet Names

The rivet can optionally be given a custom name:

```python
rivet.rivet("myRivet")
