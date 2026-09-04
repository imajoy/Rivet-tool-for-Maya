# Rivet — Poly & NURBS Surface Pinning Tool for Maya

**Rivet** creates a locator that stays attached to a live polygon mesh or
NURBS surface.

It is useful for attaching controls, props, buttons, secondary geometry,
or other rig elements to a deforming surface without requiring skin
weighting.

This is a Python conversion of the classic **Rivet** MEL script originally
created by **Michael Bazhutkin / studio Klassika (2000–2001)**.

The Python version preserves the original rivet technique while adding
Maya-friendly Python implementation and improved error handling.

---

## Features

### Polygon Mesh Rivet

Select **two polygon edges on the same mesh** and run:

```python
rivet.rivet()
