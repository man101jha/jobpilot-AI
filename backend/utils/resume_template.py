# Resume styling constants for the ReportLab PDF generator
# Colors (R, G, B) — 0 to 1 scale
COLORS = {
    "name":        (0.10, 0.10, 0.30),   # Deep navy
    "accent":      (0.20, 0.40, 0.80),   # Modern blue accent
    "section":     (0.20, 0.40, 0.80),   # Section header color
    "rule":        (0.20, 0.40, 0.80),   # Divider line color
    "subtitle":    (0.35, 0.35, 0.55),   # Job title / company sub text
    "body":        (0.15, 0.15, 0.15),   # Main body text
    "light_gray":  (0.55, 0.55, 0.55),   # Dates, location
    "white":       (1.00, 1.00, 1.00),
    "page_bg":     (0.97, 0.97, 1.00),   # Very subtle off-white background
}

# Font sizes
FONT = {
    "name":        22,
    "contact":     9,
    "section":     11,
    "subheading":  10,
    "body":        9.5,
    "bullet":      9.5,
    "date":        9,
}

# Page margins (points)
MARGIN = {
    "left":   40,
    "right":  40,
    "top":    36,
    "bottom": 36,
}

# Spacing
SPACING = {
    "after_name":        6,
    "after_contact":     12,
    "before_section":    10,
    "after_section":     4,
    "after_subheading":  2,
    "after_bullet":      1,
    "bullet_indent":     12,
    "section_rule_width": 1.2,
}
