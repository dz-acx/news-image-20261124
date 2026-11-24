#!/usr/bin/env python3
"""
THE WORLD IN ONE DAY — Tuesday 24 November 2026
Pure-Python (stdlib only) 1024x1024 newspaper-style infographic generator.
"""

import math
import os
import struct
import zlib


# =============================================================================
# 1. CONFIGURATION, PALETTE & PAGE LAYOUT
# =============================================================================

WIDTH = 1024
HEIGHT = 1024

# Core palette
COLOR_PAPER = (247, 243, 233)        # Warm newsprint background
COLOR_PANEL_BG = (251, 248, 240)     # Subtle lighter card interior
COLOR_HEADER_BG = (234, 227, 212)    # Warm stone header band tint
COLOR_INK = (20, 20, 25)             # Primary dark ink
COLOR_INK_MUTED = (82, 78, 72)       # Secondary editorial ink
COLOR_RULE_LIGHT = (196, 188, 173)   # Subtle divider rule
COLOR_ACCENT_RED = (178, 34, 52)     # Editorial accent red
COLOR_ACCENT_BLUE = (30, 70, 140)    # Editorial accent blue

# Scene illustration palette
COLOR_SCENE_BG = (240, 236, 226)
COLOR_PROHIBIT_RED = (204, 28, 42)
COLOR_CHIP_BODY = (30, 34, 42)
COLOR_CHIP_BEVEL = (56, 62, 74)
COLOR_CHIP_DIE = (164, 174, 186)
COLOR_CHIP_DIE_INNER = (118, 128, 142)
COLOR_CHIP_PIN = (68, 74, 84)
COLOR_CHIP_PIN_TIP = (132, 138, 148)
COLOR_GOLD = (206, 168, 56)
COLOR_TABLE_TOP = (152, 106, 68)
COLOR_TABLE_FRONT = (112, 74, 46)
COLOR_TABLE_LEG = (88, 58, 36)
COLOR_POLE = (58, 62, 70)
COLOR_WHITE = (252, 252, 250)
COLOR_UA_BLUE = (0, 87, 183)
COLOR_UA_YELLOW = (247, 206, 20)
COLOR_RU_BLUE = (0, 57, 166)
COLOR_RU_RED = (210, 38, 34)
COLOR_US_RED = (186, 30, 44)
COLOR_US_BLUE = (22, 52, 118)
COLOR_EU_BLUE = (0, 51, 153)
COLOR_EU_GOLD = (255, 206, 20)
COLOR_SKY_TOP = (192, 216, 238)
COLOR_SKY_BOT = (232, 240, 246)
COLOR_SEA_TOP = (38, 86, 140)
COLOR_SEA_BOT = (28, 68, 118)
COLOR_WAVE = (228, 240, 250)
COLOR_ISLAND = (36, 42, 50)
COLOR_ISLAND_LIT = (62, 70, 82)
COLOR_JET = (24, 28, 36)

# Structured page layout constants (in pixels) for Step A and subsequent steps
MARGIN_X = 34
CONTENT_X = MARGIN_X
CONTENT_W = WIDTH - 2 * MARGIN_X     # 956 px

MASTHEAD = {
    "top_rule_y": 32,
    "title_y": 50,
    "title_scale": 6.0,
    "title_thickness": 4.4,
    "date_y": 110,
    "date_scale": 2.4,
    "date_thickness": 2.1,
    "double_rule_top_y": 144,
    "double_rule_bot_y": 151,
}

# Three equal-width panels: 3 * 308 + 2 * 16 = 956 px
PANEL_GAP = 16
PANEL_W = (CONTENT_W - 2 * PANEL_GAP) // 3  # 308 px
PANEL_Y = 172
PANEL_H = 330
PANEL_HEADER_H = 28

PANELS = [
    {
        "id": "panel_1",
        "num": "1",
        "kicker": "TECH & TRADE",
        "headline": "US BLACKLISTS MEGASPEED",
        "sub": "NVIDIA-LINKED CHIP FIRM HIT BY EXPORT CONTROLS",
        "x": CONTENT_X,
        "y": PANEL_Y,
        "w": PANEL_W,
        "h": PANEL_H,
        "header_h": PANEL_HEADER_H,
        "accent": COLOR_ACCENT_BLUE,
    },
    {
        "id": "panel_2",
        "num": "2",
        "kicker": "DIPLOMACY",
        "headline": "ZELENSKY URGES FOUR-PARTY TALKS",
        "sub": "KYIV READY TO MEET AS EARLY AS TUESDAY",
        "x": CONTENT_X + PANEL_W + PANEL_GAP,
        "y": PANEL_Y,
        "w": PANEL_W,
        "h": PANEL_H,
        "header_h": PANEL_HEADER_H,
        "accent": COLOR_ACCENT_RED,
    },
    {
        "id": "panel_3",
        "num": "3",
        "kicker": "EAST ASIA",
        "headline": "RUSSIAN JETS ENTER KOREA AIR ZONE",
        "sub": "SEOUL: NO AIRSPACE VIOLATION - JETS SCRAMBLED",
        "x": CONTENT_X + 2 * (PANEL_W + PANEL_GAP),
        "y": PANEL_Y,
        "w": PANEL_W,
        "h": PANEL_H,
        "header_h": PANEL_HEADER_H,
        "accent": COLOR_INK,
    },
]

# Section 1 ("BY THE NUMBERS") and Section 2 ("MORE OF THE DAY") layout & data
NUMBERS_STRIP = {
    "x": CONTENT_X,
    "y": 518,
    "w": CONTENT_W,
    "header_h": 24,
    "grid_y": 542,
    "grid_h": 176,
    "cols": 4,
    "rows": 2,
    "title": "BY THE NUMBERS",
}

BY_THE_NUMBERS_ITEMS = [
    ("7", "FIRMS ADDED TO THE US EXPORT BLACKLIST"),
    ("410", "DAYS SINCE THE LAST ADDITION TO THE US ENTITY LIST"),
    ("35", "STATE SECRETS LEAKED BY THE CONVICTED SPY OFFICIAL"),
    ("$150,000", "PAID TO THE SPY OFFICIAL BY A FOREIGN AGENCY"),
    ("41.9%", "OF CANADA'S AIR FORCE FLEET IS SERVICEABLE"),
    ("88", "F-35 JETS IN CANADA'S PURCHASE NOW UNDER REVIEW"),
    ("48", "TEAMS AT THE 2031 WOMEN'S WORLD CUP, A FIRST"),
    ("3", "MINUTES THE ULLEUNG EVACUATION WARNING LASTED"),
]

NEWS_SECTION = {
    "x": CONTENT_X,
    "y": 736,
    "w": CONTENT_W,
    "header_h": 24,
    "list_y": 763,
    "bottom_limit": 956,
    "title": "MORE OF THE DAY",
}

MORE_OF_THE_DAY_ITEMS = [
    (
        "4. CHINA SENTENCES SPY OFFICIAL TO DEATH",
        "- OFFICIAL SURNAMED MA LEAKED 35 STATE SECRETS TO A FOREIGN SPY AGENCY FOR OVER $150,000, BEIJING'S SECRETS WATCHDOG ANNOUNCED.",
    ),
    (
        "5. PENTAGON REBUKES CANADA",
        "- WASHINGTON FAULTS OTTAWA'S DEFENCE SHORTFALLS AND ITS REVIEW OF THE 88-JET F-35 PURCHASE IN A BLUNT FACT SHEET.",
    ),
    (
        "6. FIFA NAMES WOMEN'S WORLD CUP HOSTS",
        "- 2031: UNITED STATES, MEXICO, COSTA RICA AND JAMAICA. 2035: THE UNITED KINGDOM. BOTH BIDS UNOPPOSED.",
    ),
    (
        "7. NVIDIA BRINGS BACK ITS CEO",
        "- THE BOARD REINSTATES JENSEN HUANG LESS THAN TWO WEEKS AFTER HIS OUSTER, HOURS BEFORE THE MEGASPEED BLACKLIST LANDED.",
    ),
    (
        "8. SEOUL SUMMONS RUSSIAN ATTACHE",
        "- SOUTH KOREA LODGES A STRONG PROTEST OVER THE AIR-ZONE ENTRY NEAR ULLEUNG ISLAND.",
    ),
]

FOOTER = {
    "rule_y": 966,
    "text_y": 979,
    "text_scale": 1.65,
    "text_thickness": 1.4,
    "text": "ONE DAY - ONE PAGE - SOURCES: WIRE REPORTS OF 24 NOV 2026",
}


# =============================================================================
# 2. RGB FRAMEBUFFER & DRAWING PRIMITIVES
# =============================================================================

SUPERSAMPLE = 3
_DIV9_LUT = tuple((i + 4) // 9 for i in range(9 * 255 + 1))


class Canvas:
    """Deterministic RGB24 pixel framebuffer with supersampled vector primitives."""

    def __init__(self, width, height, bg_color=COLOR_PAPER, supersample=SUPERSAMPLE):
        self.out_width = int(width)
        self.out_height = int(height)
        self.ss = max(1, int(supersample))
        self.width = self.out_width * self.ss
        self.height = self.out_height * self.ss
        r, g, b = bg_color
        row = bytes((r, g, b)) * self.width
        self.buf = bytearray(row * self.height)
        self._glyph_cache = {}

    def set_pixel(self, x, y, color):
        """Set a single logical pixel (or ss x ss block) if within canvas bounds."""
        ss = self.ss
        if ss == 1:
            ix = int(x)
            iy = int(y)
            if 0 <= ix < self.width and 0 <= iy < self.height:
                idx = (iy * self.width + ix) * 3
                self.buf[idx] = color[0]
                self.buf[idx + 1] = color[1]
                self.buf[idx + 2] = color[2]
        else:
            x0 = int(round(x * ss))
            y0 = int(round(y * ss))
            self._fill_rect_ss(x0, y0, x0 + ss, y0 + ss, color)

    def blend_pixel(self, x, y, color, alpha):
        """Alpha-blend a color onto a logical pixel with deterministic rounding."""
        if alpha <= 0.0:
            return
        ss = self.ss
        ix0 = max(0, int(round(x * ss)))
        iy0 = max(0, int(round(y * ss)))
        ix1 = min(self.width, ix0 + ss)
        iy1 = min(self.height, iy0 + ss)
        if ix0 >= ix1 or iy0 >= iy1:
            return
        if alpha >= 1.0:
            self._fill_rect_ss(ix0, iy0, ix1, iy1, color)
            return
        inv = 1.0 - alpha
        cr, cg, cb = color
        buf = self.buf
        w = self.width
        for py in range(iy0, iy1):
            row_off = py * w
            for px in range(ix0, ix1):
                idx = (row_off + px) * 3
                buf[idx] = int(buf[idx] * inv + cr * alpha + 0.5)
                buf[idx + 1] = int(buf[idx + 1] * inv + cg * alpha + 0.5)
                buf[idx + 2] = int(buf[idx + 2] * inv + cb * alpha + 0.5)

    def _fill_rect_ss(self, x0, y0, x1, y1, color):
        """Fill an axis-aligned rectangle in supersampled pixel coordinates."""
        cx0 = max(0, x0)
        cy0 = max(0, y0)
        cx1 = min(self.width, x1)
        cy1 = min(self.height, y1)
        if cx0 >= cx1 or cy0 >= cy1:
            return
        span_w = cx1 - cx0
        row_bytes = bytes((color[0], color[1], color[2])) * span_w
        stride = self.width * 3
        buf = self.buf
        start_x = cx0 * 3
        end_x = cx1 * 3
        for py in range(cy0, cy1):
            row_off = py * stride
            buf[row_off + start_x : row_off + end_x] = row_bytes

    def fill_rect(self, x, y, w, h, color):
        """Fill an axis-aligned rectangle clipped to canvas bounds."""
        ss = self.ss
        x0 = int(round(x * ss))
        y0 = int(round(y * ss))
        x1 = int(round((x + w) * ss))
        y1 = int(round((y + h) * ss))
        self._fill_rect_ss(x0, y0, x1, y1, color)

    def draw_rect(self, x, y, w, h, color, thickness=1):
        """Draw an outlined axis-aligned rectangle (inward border)."""
        ss = self.ss
        x0 = int(round(x * ss))
        y0 = int(round(y * ss))
        x1 = int(round((x + w) * ss))
        y1 = int(round((y + h) * ss))
        t = max(1, int(round(thickness * ss)))
        self._fill_rect_ss(x0, y0, x1, y0 + t, color)
        self._fill_rect_ss(x0, y1 - t, x1, y1, color)
        self._fill_rect_ss(x0, y0, x0 + t, y1, color)
        self._fill_rect_ss(x1 - t, y0, x1, y1, color)

    def draw_hline(self, x0, x1, y, color, thickness=1):
        """Draw a crisp horizontal rule centered vertically at y."""
        ss = self.ss
        left = int(round(min(x0, x1) * ss))
        right = int(round(max(x0, x1) * ss))
        t = max(1, int(round(thickness * ss)))
        top = int(round(y * ss - t * 0.5))
        self._fill_rect_ss(left, top, right, top + t, color)

    def draw_vline(self, x, y0, y1, color, thickness=1):
        """Draw a crisp vertical rule centered horizontally at x."""
        ss = self.ss
        top = int(round(min(y0, y1) * ss))
        bot = int(round(max(y0, y1) * ss))
        t = max(1, int(round(thickness * ss)))
        left = int(round(x * ss - t * 0.5))
        self._fill_rect_ss(left, top, left + t, bot, color)

    def _draw_line_ss(self, x0, y0, x1, y1, color, thickness):
        """Draw an anti-aliased thick line segment in supersampled coordinates."""
        half_w = max(0.5, float(thickness) * 0.5)
        outer = half_w + 0.5
        inner = max(0.0, half_w - 0.5)
        outer_sq = outer * outer

        min_x = max(0, int(math.floor(min(x0, x1) - outer)))
        max_x = min(self.width - 1, int(math.ceil(max(x0, x1) + outer)))
        min_y = max(0, int(math.floor(min(y0, y1) - outer)))
        max_y = min(self.height - 1, int(math.ceil(max(y0, y1) + outer)))
        if min_x > max_x or min_y > max_y:
            return

        dx = x1 - x0
        dy = y1 - y0
        seg_len_sq = dx * dx + dy * dy

        buf = self.buf
        w = self.width
        cr, cg, cb = color

        if seg_len_sq < 1e-12:
            for py in range(min_y, max_y + 1):
                dy0 = py - y0
                dy0_sq = dy0 * dy0
                row_off = py * w
                for px in range(min_x, max_x + 1):
                    dx0 = px - x0
                    d_sq = dx0 * dx0 + dy0_sq
                    if d_sq >= outer_sq:
                        continue
                    d = math.sqrt(d_sq)
                    idx = (row_off + px) * 3
                    if d <= inner:
                        buf[idx] = cr
                        buf[idx + 1] = cg
                        buf[idx + 2] = cb
                    else:
                        alpha = outer - d
                        inv = 1.0 - alpha
                        buf[idx] = int(buf[idx] * inv + cr * alpha + 0.5)
                        buf[idx + 1] = int(buf[idx + 1] * inv + cg * alpha + 0.5)
                        buf[idx + 2] = int(buf[idx + 2] * inv + cb * alpha + 0.5)
            return

        inv_len_sq = 1.0 / seg_len_sq
        abs_dy = abs(dy)
        if abs_dy > 1e-6:
            slope = dx / dy
            x_pad = outer * math.sqrt(seg_len_sq) / abs_dy
        else:
            slope = 0.0
            x_pad = 0.0

        for py in range(min_y, max_y + 1):
            py_y0 = py - y0
            row_off = py * w
            if abs_dy > 1e-6:
                xc = x0 + py_y0 * slope
                r_min = max(min_x, int(math.floor(xc - x_pad)))
                r_max = min(max_x, int(math.ceil(xc + x_pad)))
            else:
                r_min = min_x
                r_max = max_x
            for px in range(r_min, r_max + 1):
                px_x0 = px - x0
                t = (px_x0 * dx + py_y0 * dy) * inv_len_sq
                if t < 0.0:
                    t = 0.0
                elif t > 1.0:
                    t = 1.0
                cx = px_x0 - t * dx
                cy = py_y0 - t * dy
                d_sq = cx * cx + cy * cy
                if d_sq >= outer_sq:
                    continue
                d = math.sqrt(d_sq)
                idx = (row_off + px) * 3
                if d <= inner:
                    buf[idx] = cr
                    buf[idx + 1] = cg
                    buf[idx + 2] = cb
                else:
                    alpha = outer - d
                    inv = 1.0 - alpha
                    buf[idx] = int(buf[idx] * inv + cr * alpha + 0.5)
                    buf[idx + 1] = int(buf[idx + 1] * inv + cg * alpha + 0.5)
                    buf[idx + 2] = int(buf[idx + 2] * inv + cb * alpha + 0.5)

    def draw_line(self, x0, y0, x1, y1, color, thickness=1.0):
        """Draw an anti-aliased thick line segment using capsule distance."""
        ss = self.ss
        self._draw_line_ss(x0 * ss, y0 * ss, x1 * ss, y1 * ss, color, thickness * ss)

    def draw_dashed_line(
        self, x0, y0, x1, y1, color, thickness=1.0, dash_len=8.0, gap_len=5.0
    ):
        """Draw a dashed line segment with configurable dash and gap lengths."""
        dx = x1 - x0
        dy = y1 - y0
        total_len = math.hypot(dx, dy)
        if total_len < 1e-9:
            self.draw_line(x0, y0, x1, y1, color, thickness)
            return
        ux = dx / total_len
        uy = dy / total_len
        step = max(1.0, float(dash_len) + float(gap_len))
        pos = 0.0
        while pos < total_len:
            end = min(total_len, pos + dash_len)
            self.draw_line(
                x0 + ux * pos,
                y0 + uy * pos,
                x0 + ux * end,
                y0 + uy * end,
                color,
                thickness,
            )
            pos += step

    def fill_circle(self, cx, cy, radius, color):
        """Draw an anti-aliased filled circle using fast interior spans."""
        ss = self.ss
        scx = cx * ss
        scy = cy * ss
        r = float(radius) * ss
        if r <= 0.0:
            return
        outer = r + 0.5
        inner = max(0.0, r - 0.5)
        outer_sq = outer * outer
        inner_sq = inner * inner

        min_y = max(0, int(math.floor(scy - outer)))
        max_y = min(self.height - 1, int(math.ceil(scy + outer)))
        w = self.width
        buf = self.buf
        cr, cg, cb = color
        pixel_bytes = bytes((cr, cg, cb))

        for py in range(min_y, max_y + 1):
            dy = py - scy
            dy_sq = dy * dy
            if dy_sq >= outer_sq:
                continue
            dx_outer = math.sqrt(outer_sq - dy_sq)
            x_left = max(0, int(math.floor(scx - dx_outer)))
            x_right = min(w - 1, int(math.ceil(scx + dx_outer)))

            solid_l = x_right + 1
            solid_r = x_left - 1
            if dy_sq < inner_sq:
                dx_inner = math.sqrt(inner_sq - dy_sq)
                solid_l = max(x_left, int(math.ceil(scx - dx_inner)))
                solid_r = min(x_right, int(math.floor(scx + dx_inner)))
                if solid_l <= solid_r:
                    row_off = py * w * 3
                    span = solid_r - solid_l + 1
                    buf[row_off + solid_l * 3 : row_off + (solid_r + 1) * 3] = (
                        pixel_bytes * span
                    )

            row_off = py * w
            left_end = min(x_right, solid_l - 1)
            for px in range(x_left, left_end + 1):
                d = math.hypot(px - scx, dy)
                if d < outer:
                    alpha = min(1.0, outer - d)
                    inv = 1.0 - alpha
                    idx = (row_off + px) * 3
                    buf[idx] = int(buf[idx] * inv + cr * alpha + 0.5)
                    buf[idx + 1] = int(buf[idx + 1] * inv + cg * alpha + 0.5)
                    buf[idx + 2] = int(buf[idx + 2] * inv + cb * alpha + 0.5)

            right_start = max(x_left, solid_r + 1)
            if right_start <= left_end:
                right_start = left_end + 1
            for px in range(right_start, x_right + 1):
                d = math.hypot(px - scx, dy)
                if d < outer:
                    alpha = min(1.0, outer - d)
                    inv = 1.0 - alpha
                    idx = (row_off + px) * 3
                    buf[idx] = int(buf[idx] * inv + cr * alpha + 0.5)
                    buf[idx + 1] = int(buf[idx + 1] * inv + cg * alpha + 0.5)
                    buf[idx + 2] = int(buf[idx + 2] * inv + cb * alpha + 0.5)

    def draw_circle(self, cx, cy, radius, color, thickness=1.0):
        """Draw an anti-aliased outlined circle of given radius and thickness."""
        ss = self.ss
        scx = cx * ss
        scy = cy * ss
        r = float(radius) * ss
        if r <= 0.0:
            return
        half_w = max(0.5, float(thickness) * ss * 0.5)
        outer = r + half_w + 0.5
        inner_bound = max(0.0, r - half_w - 0.5)
        outer_sq = outer * outer
        inner_bound_sq = inner_bound * inner_bound
        ring_outer = half_w + 0.5
        ring_inner = max(0.0, half_w - 0.5)

        min_y = max(0, int(math.floor(scy - outer)))
        max_y = min(self.height - 1, int(math.ceil(scy + outer)))
        w = self.width
        buf = self.buf
        cr, cg, cb = color

        for py in range(min_y, max_y + 1):
            dy = py - scy
            dy_sq = dy * dy
            if dy_sq >= outer_sq:
                continue
            dx_max = math.sqrt(outer_sq - dy_sq)
            x_left = max(0, int(math.floor(scx - dx_max)))
            x_right = min(w - 1, int(math.ceil(scx + dx_max)))

            skip_l = x_right + 1
            skip_r = x_left - 1
            if dy_sq < inner_bound_sq:
                dx_min = math.sqrt(inner_bound_sq - dy_sq)
                skip_l = max(x_left, int(math.ceil(scx - dx_min)))
                skip_r = min(x_right, int(math.floor(scx + dx_min)))

            row_off = py * w
            ranges = (
                ((x_left, skip_l - 1), (skip_r + 1, x_right))
                if skip_l <= skip_r
                else ((x_left, x_right),)
            )
            for rx0, rx1 in ranges:
                for px in range(rx0, rx1 + 1):
                    ring_d = abs(math.hypot(px - scx, dy) - r)
                    if ring_d >= ring_outer:
                        continue
                    idx = (row_off + px) * 3
                    if ring_d <= ring_inner:
                        buf[idx] = cr
                        buf[idx + 1] = cg
                        buf[idx + 2] = cb
                    else:
                        alpha = ring_outer - ring_d
                        inv = 1.0 - alpha
                        buf[idx] = int(buf[idx] * inv + cr * alpha + 0.5)
                        buf[idx + 1] = int(buf[idx + 1] * inv + cg * alpha + 0.5)
                        buf[idx + 2] = int(buf[idx + 2] * inv + cb * alpha + 0.5)

    def fill_polygon(self, points, color):
        """Fill an arbitrary polygon using scanline even-odd rasterization."""
        n = len(points)
        if n < 3:
            return
        ss = self.ss
        spts = [(p[0] * ss, p[1] * ss) for p in points]
        ys = [p[1] for p in spts]
        y_min = max(0, int(math.floor(min(ys))))
        y_max = min(self.height - 1, int(math.ceil(max(ys))))
        if y_min > y_max:
            return

        w = self.width
        buf = self.buf
        pixel_bytes = bytes((color[0], color[1], color[2]))

        for py in range(y_min, y_max + 1):
            sy = py + 0.5
            xs = []
            x0, y0 = spts[-1]
            for x1, y1 in spts:
                if (y0 <= sy < y1) or (y1 <= sy < y0):
                    t = (sy - y0) / (y1 - y0)
                    xs.append(x0 + t * (x1 - x0))
                x0, y0 = x1, y1
            if len(xs) < 2:
                continue
            xs.sort()
            row_off = py * w * 3
            for i in range(0, len(xs) - 1, 2):
                lx = max(0, int(math.ceil(xs[i] - 0.5)))
                rx = min(w - 1, int(math.floor(xs[i + 1] - 0.5)))
                if lx <= rx:
                    span = rx - lx + 1
                    buf[row_off + lx * 3 : row_off + (rx + 1) * 3] = (
                        pixel_bytes * span
                    )

    def _draw_polylines_sdf_ss(self, polylines_ss, color, thickness_ss):
        """Render one or more SS-coordinate polylines via union SDF coverage (no joint darkening)."""
        half_w = max(0.5, float(thickness_ss) * 0.5)
        outer = half_w + 0.5
        inner = max(0.0, half_w - 0.5)
        outer_sq = outer * outer

        xs = []
        ys = []
        for poly in polylines_ss:
            for px, py in poly:
                xs.append(px)
                ys.append(py)
        if not xs:
            return

        min_x = max(0, int(math.floor(min(xs) - outer)))
        max_x = min(self.width - 1, int(math.ceil(max(xs) + outer)))
        min_y = max(0, int(math.floor(min(ys) - outer)))
        max_y = min(self.height - 1, int(math.ceil(max(ys) + outer)))
        if min_x > max_x or min_y > max_y:
            return

        bw = max_x - min_x + 1
        bh = max_y - min_y + 1
        cov = [0.0] * (bw * bh)

        for poly in polylines_ss:
            n = len(poly)
            if n == 0:
                continue
            segs = (
                [(poly[0][0], poly[0][1], poly[0][0], poly[0][1])]
                if n == 1
                else [(poly[i][0], poly[i][1], poly[i + 1][0], poly[i + 1][1]) for i in range(n - 1)]
            )
            for ax, ay, bx, by in segs:
                smin_x = max(min_x, int(math.floor(min(ax, bx) - outer)))
                smax_x = min(max_x, int(math.ceil(max(ax, bx) + outer)))
                smin_y = max(min_y, int(math.floor(min(ay, by) - outer)))
                smax_y = min(max_y, int(math.ceil(max(ay, by) + outer)))
                if smin_x > smax_x or smin_y > smax_y:
                    continue
                dx = bx - ax
                dy = by - ay
                seg_len_sq = dx * dx + dy * dy
                if seg_len_sq < 1e-12:
                    for py in range(smin_y, smax_y + 1):
                        dy0 = py - ay
                        dy0_sq = dy0 * dy0
                        row_k = (py - min_y) * bw - min_x
                        for px in range(smin_x, smax_x + 1):
                            dx0 = px - ax
                            d_sq = dx0 * dx0 + dy0_sq
                            if d_sq >= outer_sq:
                                continue
                            d = math.sqrt(d_sq)
                            alpha = 1.0 if d <= inner else (outer - d)
                            k = row_k + px
                            if alpha > cov[k]:
                                cov[k] = alpha
                    continue

                inv_len_sq = 1.0 / seg_len_sq
                abs_dy = abs(dy)
                if abs_dy > 1e-6:
                    slope = dx / dy
                    x_pad = outer * math.sqrt(seg_len_sq) / abs_dy
                else:
                    slope = 0.0
                    x_pad = 0.0
                for py in range(smin_y, smax_y + 1):
                    py_ay = py - ay
                    row_k = (py - min_y) * bw - min_x
                    if abs_dy > 1e-6:
                        xc = ax + py_ay * slope
                        r_min = max(smin_x, int(math.floor(xc - x_pad)))
                        r_max = min(smax_x, int(math.ceil(xc + x_pad)))
                    else:
                        r_min = smin_x
                        r_max = smax_x
                    for px in range(r_min, r_max + 1):
                        px_ax = px - ax
                        t = (px_ax * dx + py_ay * dy) * inv_len_sq
                        if t < 0.0:
                            t = 0.0
                        elif t > 1.0:
                            t = 1.0
                        cx = px_ax - t * dx
                        cy = py_ay - t * dy
                        d_sq = cx * cx + cy * cy
                        if d_sq >= outer_sq:
                            continue
                        d = math.sqrt(d_sq)
                        alpha = 1.0 if d <= inner else (outer - d)
                        k = row_k + px
                        if alpha > cov[k]:
                            cov[k] = alpha

        buf = self.buf
        w = self.width
        cr, cg, cb = color
        for ly in range(bh):
            row_off = (min_y + ly) * w + min_x
            k_off = ly * bw
            for lx in range(bw):
                alpha = cov[k_off + lx]
                if alpha <= 0.0:
                    continue
                idx = (row_off + lx) * 3
                if alpha >= 1.0:
                    buf[idx] = cr
                    buf[idx + 1] = cg
                    buf[idx + 2] = cb
                else:
                    inv = 1.0 - alpha
                    buf[idx] = int(buf[idx] * inv + cr * alpha + 0.5)
                    buf[idx + 1] = int(buf[idx + 1] * inv + cg * alpha + 0.5)
                    buf[idx + 2] = int(buf[idx + 2] * inv + cb * alpha + 0.5)

    def draw_polyline(self, points, color, thickness=1.0, closed=False):
        """Draw connected line segments through a list of (x, y) vertices."""
        n = len(points)
        if n == 0:
            return
        ss = self.ss
        spts = [(p[0] * ss, p[1] * ss) for p in points]
        if closed and n >= 3:
            spts.append(spts[0])
        self._draw_polylines_sdf_ss([spts], color, thickness * ss)

    def draw_polygon(self, points, color, thickness=1.0):
        """Draw the outline of a closed polygon."""
        self.draw_polyline(points, color, thickness=thickness, closed=True)

    def draw_text(
        self, x, y, text, scale, color, thickness=None, align="left", letter_gap=None
    ):
        """Draw text using the built-in stroke font."""
        return draw_text(
            self,
            x,
            y,
            text,
            scale,
            color,
            thickness=thickness,
            align=align,
            letter_gap=FONT_LETTER_GAP if letter_gap is None else letter_gap,
        )

    def downsample(self):
        """Downsample the supersampled framebuffer to (out_width, out_height)."""
        if self.ss == 1:
            return self
        ss = self.ss
        out_w = self.out_width
        out_h = self.out_height
        out = Canvas(out_w, out_h, supersample=1)
        src = memoryview(self.buf)
        dst = out.buf
        ss_stride = self.width * 3
        out_stride = out_w * 3

        if ss == 3:
            from operator import add

            div9_get = _DIV9_LUT.__getitem__
            for y in range(out_h):
                r0_off = (y * 3) * ss_stride
                r1_off = r0_off + ss_stride
                r2_off = r1_off + ss_stride
                r0 = src[r0_off : r0_off + ss_stride]
                r1 = src[r1_off : r1_off + ss_stride]
                r2 = src[r2_off : r2_off + ss_stride]
                dst_row_off = y * out_stride
                dst_row = bytearray(out_stride)
                for c in (0, 1, 2):
                    s01 = map(add, r0[c::9], r0[c + 3 :: 9])
                    s23 = map(add, r0[c + 6 :: 9], r1[c::9])
                    s45 = map(add, r1[c + 3 :: 9], r1[c + 6 :: 9])
                    s67 = map(add, r2[c::9], r2[c + 3 :: 9])
                    total = map(
                        add,
                        map(add, map(add, s01, s23), map(add, s45, s67)),
                        r2[c + 6 :: 9],
                    )
                    dst_row[c::3] = bytes(map(div9_get, total))
                dst[dst_row_off : dst_row_off + out_stride] = dst_row
            return out

        # Generic ss x ss box filter fallback
        area = ss * ss
        half_area = area // 2
        w = self.width
        buf = self.buf
        for oy in range(out_h):
            sy0 = oy * ss
            dst_row_off = oy * out_stride
            for ox in range(out_w):
                sx0 = ox * ss
                sr = sg = sb = 0
                for dy in range(ss):
                    row_off = (sy0 + dy) * w + sx0
                    for dx in range(ss):
                        idx = (row_off + dx) * 3
                        sr += buf[idx]
                        sg += buf[idx + 1]
                        sb += buf[idx + 2]
                oidx = dst_row_off + ox * 3
                dst[oidx] = (sr + half_area) // area
                dst[oidx + 1] = (sg + half_area) // area
                dst[oidx + 2] = (sb + half_area) // area
        return out


# =============================================================================
# 3. HAND-WRITTEN STROKE FONT & TEXT LAYOUT
# =============================================================================

# Design grid: approximately 5 wide x 7 tall (y=0 cap top, y=7 baseline).
# Each glyph is (advance_width, [polyline, ...]).
FONT_CAP_HEIGHT = 7.0
FONT_LETTER_GAP = 1.52


def _arc_pts(cx, cy, rx, ry, a0_deg, a1_deg, steps=6):
    """Sample an elliptical arc cleanly from a0_deg to a1_deg."""
    a0 = math.radians(a0_deg)
    a1 = math.radians(a1_deg)
    return [
        (
            cx + rx * math.cos(a0 + (a1 - a0) * (i / steps)),
            cy + ry * math.sin(a0 + (a1 - a0) * (i / steps)),
        )
        for i in range(steps + 1)
    ]


def _qbez_pts(p0, p1, p2, steps=6):
    """Sample a quadratic Bezier curve from p0 through control p1 to p2."""
    pts = []
    for i in range(steps + 1):
        t = i / steps
        mt = 1.0 - t
        pts.append(
            (
                mt * mt * p0[0] + 2.0 * mt * t * p1[0] + t * t * p2[0],
                mt * mt * p0[1] + 2.0 * mt * t * p1[1] + t * t * p2[1],
            )
        )
    return pts


def _cbez_pts(p0, p1, p2, p3, steps=8):
    """Sample a cubic Bezier curve from p0 to p3 with controls p1 and p2."""
    pts = []
    for i in range(steps + 1):
        t = i / steps
        mt = 1.0 - t
        pts.append(
            (
                mt * mt * mt * p0[0]
                + 3.0 * mt * mt * t * p1[0]
                + 3.0 * mt * t * t * p2[0]
                + t * t * t * p3[0],
                mt * mt * mt * p0[1]
                + 3.0 * mt * mt * t * p1[1]
                + 3.0 * mt * t * t * p2[1]
                + t * t * t * p3[1],
            )
        )
    return pts


GLYPHS = {
    " ": (3.2, []),
    # Uppercase letters A-Z
    "A": (
        5.0,
        [
            [(0.0, 7.0), (2.5, 0.0), (5.0, 7.0)],
            [(0.9, 4.6), (4.1, 4.6)],
        ],
    ),
    "B": (
        4.8,
        [
            [(0.0, 7.0), (0.0, 0.0), (2.6, 0.0)]
            + _arc_pts(2.6, 1.65, 1.8, 1.65, -90, 90, 8)
            + [(0.0, 3.3)],
            [(2.7, 3.3)]
            + _arc_pts(2.7, 5.15, 2.1, 1.85, -90, 90, 8)
            + [(0.0, 7.0)],
        ],
    ),
    "C": (
        4.9,
        [
            _arc_pts(3.0, 1.9, 1.8, 1.9, -24, -90, 5)
            + [(1.8, 0.0)]
            + _arc_pts(1.8, 1.9, 1.8, 1.9, -90, -180, 6)
            + [(0.0, 5.1)]
            + _arc_pts(1.8, 5.1, 1.8, 1.9, 180, 90, 6)
            + [(3.0, 7.0)]
            + _arc_pts(3.0, 5.1, 1.8, 1.9, 90, 24, 5),
        ],
    ),
    "D": (
        4.9,
        [
            [(0.0, 7.0), (0.0, 0.0), (2.2, 0.0)]
            + _arc_pts(2.2, 2.0, 2.6, 2.0, -90, 0, 6)
            + [(4.8, 5.0)]
            + _arc_pts(2.2, 5.0, 2.6, 2.0, 0, 90, 6)
            + [(0.0, 7.0)],
        ],
    ),
    "E": (
        4.5,
        [
            [(4.5, 0.0), (0.0, 0.0), (0.0, 7.0), (4.5, 7.0)],
            [(0.0, 3.4), (3.6, 3.4)],
        ],
    ),
    "F": (
        4.4,
        [
            [(4.4, 0.0), (0.0, 0.0), (0.0, 7.0)],
            [(0.0, 3.4), (3.5, 3.4)],
        ],
    ),
    "G": (
        5.0,
        [
            _arc_pts(3.1, 1.9, 1.8, 1.9, -24, -90, 5)
            + [(1.8, 0.0)]
            + _arc_pts(1.8, 1.9, 1.8, 1.9, -90, -180, 6)
            + [(0.0, 5.1)]
            + _arc_pts(1.8, 5.1, 1.8, 1.9, 180, 90, 6)
            + _arc_pts(3.1, 5.1, 1.8, 1.9, 90, 0, 5)
            + [(4.9, 3.7), (2.8, 3.7)],
        ],
    ),
    "H": (
        4.8,
        [
            [(0.0, 0.0), (0.0, 7.0)],
            [(4.8, 0.0), (4.8, 7.0)],
            [(0.0, 3.4), (4.8, 3.4)],
        ],
    ),
    "I": (
        2.8,
        [
            [(0.2, 0.0), (2.6, 0.0)],
            [(1.4, 0.0), (1.4, 7.0)],
            [(0.2, 7.0), (2.6, 7.0)],
        ],
    ),
    "J": (
        4.4,
        [
            [(1.4, 0.0), (4.4, 0.0)],
            [(3.3, 0.0), (3.3, 5.0)] + _arc_pts(1.65, 5.0, 1.65, 2.0, 0, 155, 8),
        ],
    ),
    "K": (
        4.9,
        [
            [(0.0, 0.0), (0.0, 7.0)],
            [(4.7, 0.0), (0.0, 3.8)],
            [(1.5, 2.7), (4.9, 7.0)],
        ],
    ),
    "L": (
        4.4,
        [
            [(0.0, 0.0), (0.0, 7.0), (4.4, 7.0)],
        ],
    ),
    "M": (
        5.6,
        [
            [(0.0, 7.0), (0.0, 0.0), (2.8, 4.4), (5.6, 0.0), (5.6, 7.0)],
        ],
    ),
    "N": (
        4.9,
        [
            [(0.0, 7.0), (0.0, 0.0), (4.9, 7.0), (4.9, 0.0)],
        ],
    ),
    "O": (
        5.0,
        [
            _arc_pts(3.1, 1.9, 1.9, 1.9, -90, 0, 6)
            + _arc_pts(3.1, 5.1, 1.9, 1.9, 0, 90, 6)
            + _arc_pts(1.9, 5.1, 1.9, 1.9, 90, 180, 6)
            + _arc_pts(1.9, 1.9, 1.9, 1.9, 180, 270, 6)
            + [(3.1, 0.0)],
        ],
    ),
    "P": (
        4.7,
        [
            [(0.0, 7.0), (0.0, 0.0), (2.8, 0.0)]
            + _arc_pts(2.8, 1.85, 1.9, 1.85, -90, 90, 8)
            + [(0.0, 3.7)],
        ],
    ),
    "Q": (
        5.0,
        [
            _arc_pts(3.1, 1.9, 1.9, 1.9, -90, 0, 6)
            + _arc_pts(3.1, 5.1, 1.9, 1.9, 0, 90, 6)
            + _arc_pts(1.9, 5.1, 1.9, 1.9, 90, 180, 6)
            + _arc_pts(1.9, 1.9, 1.9, 1.9, 180, 270, 6)
            + [(3.1, 0.0)],
            [(3.0, 5.0), (5.1, 7.2)],
        ],
    ),
    "R": (
        4.9,
        [
            [(0.0, 7.0), (0.0, 0.0), (2.8, 0.0)]
            + _arc_pts(2.8, 1.8, 1.9, 1.8, -90, 90, 8)
            + [(0.0, 3.6)],
            [(2.6, 3.6), (4.9, 7.0)],
        ],
    ),
    "S": (
        4.7,
        [
            _arc_pts(2.35, 1.65, 2.25, 1.65, -22, -180, 9)
            + _cbez_pts((0.1, 1.65), (0.1, 3.45), (4.7, 3.45), (4.7, 5.25), 8)
            + _arc_pts(2.35, 5.25, 2.35, 1.75, 0, 155, 9),
        ],
    ),
    "T": (
        4.8,
        [
            [(0.0, 0.0), (4.8, 0.0)],
            [(2.4, 0.0), (2.4, 7.0)],
        ],
    ),
    "U": (
        4.9,
        [
            [(0.0, 0.0), (0.0, 4.9)]
            + _arc_pts(2.0, 4.9, 2.0, 2.1, 180, 90, 6)
            + _arc_pts(2.9, 4.9, 2.0, 2.1, 90, 0, 6)
            + [(4.9, 0.0)],
        ],
    ),
    "V": (
        5.0,
        [
            [(0.0, 0.0), (2.5, 7.0), (5.0, 0.0)],
        ],
    ),
    "W": (
        5.8,
        [
            [(0.0, 0.0), (1.3, 7.0), (2.9, 2.6), (4.5, 7.0), (5.8, 0.0)],
        ],
    ),
    "X": (
        4.8,
        [
            [(0.0, 0.0), (4.8, 7.0)],
            [(4.8, 0.0), (0.0, 7.0)],
        ],
    ),
    "Y": (
        4.8,
        [
            [(0.0, 0.0), (2.4, 3.5), (4.8, 0.0)],
            [(2.4, 3.5), (2.4, 7.0)],
        ],
    ),
    "Z": (
        4.8,
        [
            [(0.0, 0.0), (4.8, 0.0), (0.0, 7.0), (4.8, 7.0)],
        ],
    ),
    # Digits 0-9
    "0": (
        4.6,
        [
            _arc_pts(2.8, 1.9, 1.8, 1.9, -90, 0, 6)
            + _arc_pts(2.8, 5.1, 1.8, 1.9, 0, 90, 6)
            + _arc_pts(1.8, 5.1, 1.8, 1.9, 90, 180, 6)
            + _arc_pts(1.8, 1.9, 1.8, 1.9, 180, 270, 6)
            + [(2.8, 0.0)],
        ],
    ),
    "1": (
        3.4,
        [
            [(0.4, 1.5), (1.9, 0.0), (1.9, 7.0)],
            [(0.3, 7.0), (3.4, 7.0)],
        ],
    ),
    "2": (
        4.7,
        [
            _arc_pts(2.35, 1.75, 2.25, 1.75, -168, 32, 10)
            + [(0.0, 7.0), (4.7, 7.0)],
        ],
    ),
    "3": (
        4.7,
        [
            _arc_pts(2.35, 1.65, 2.15, 1.65, -155, 90, 9) + [(1.8, 3.3)],
            [(2.2, 3.3)] + _arc_pts(2.35, 5.15, 2.35, 1.85, -90, 155, 10),
        ],
    ),
    "4": (
        4.8,
        [
            [(3.6, 7.0), (3.6, 0.0), (0.0, 4.8), (4.8, 4.8)],
        ],
    ),
    "5": (
        4.7,
        [
            [(4.4, 0.0), (0.4, 0.0), (0.2, 3.1)]
            + _qbez_pts((0.2, 3.1), (1.2, 2.4), (2.35, 2.4), 4)
            + _arc_pts(2.35, 4.7, 2.25, 2.3, -90, 155, 10),
        ],
    ),
    "6": (
        4.7,
        [
            _arc_pts(2.4, 1.9, 2.1, 1.9, -28, -180, 6)
            + [(0.0, 5.05)]
            + _arc_pts(2.35, 5.05, 2.35, 1.95, 180, -180, 16),
        ],
    ),
    "7": (
        4.7,
        [
            [(0.0, 0.0), (4.7, 0.0), (1.5, 7.0)],
        ],
    ),
    "8": (
        4.7,
        [
            _arc_pts(2.35, 1.65, 2.15, 1.65, 90, 450, 14),
            _arc_pts(2.35, 5.15, 2.35, 1.85, -90, 270, 14),
        ],
    ),
    "9": (
        4.7,
        [
            _arc_pts(2.3, 5.1, 2.1, 1.9, 152, 0, 6)
            + [(4.7, 1.95)]
            + _arc_pts(2.35, 1.95, 2.35, 1.95, 0, -360, 16),
        ],
    ),
    # Punctuation: . , : ; ' - $ % + / ( ) ! ? &
    ".": (
        1.6,
        [
            [(0.8, 6.6), (0.8, 6.6)],
        ],
    ),
    ",": (
        1.8,
        [
            [(1.0, 6.3), (1.0, 6.8), (0.2, 8.0)],
        ],
    ),
    ":": (
        1.6,
        [
            [(0.8, 2.2), (0.8, 2.2)],
            [(0.8, 6.4), (0.8, 6.4)],
        ],
    ),
    ";": (
        1.8,
        [
            [(1.0, 2.2), (1.0, 2.2)],
            [(1.0, 6.2), (1.0, 6.8), (0.2, 8.0)],
        ],
    ),
    "'": (
        1.6,
        [
            [(0.9, 0.2), (0.7, 1.9)],
        ],
    ),
    "-": (
        3.6,
        [
            [(0.2, 3.6), (3.4, 3.6)],
        ],
    ),
    "$": (
        4.8,
        [
            _arc_pts(2.4, 1.95, 2.1, 1.35, -20, -180, 8)
            + _cbez_pts((0.3, 1.95), (0.3, 3.4), (4.6, 3.45), (4.6, 4.95), 8)
            + _arc_pts(2.4, 4.95, 2.2, 1.45, 0, 158, 8),
            [(2.4, -0.4), (2.4, 7.4)],
        ],
    ),
    "%": (
        5.2,
        [
            [(0.4, 6.8), (4.8, 0.2)],
            _arc_pts(1.0, 1.0, 0.8, 0.8, 0, 360, 12),
            _arc_pts(4.2, 6.0, 0.8, 0.8, 0, 360, 12),
        ],
    ),
    "+": (
        4.4,
        [
            [(0.2, 3.5), (4.2, 3.5)],
            [(2.2, 1.5), (2.2, 5.5)],
        ],
    ),
    "/": (
        3.6,
        [
            [(0.2, 7.0), (3.4, 0.0)],
        ],
    ),
    "(": (
        2.4,
        [
            _qbez_pts((2.2, 0.0), (0.4, 3.5), (2.2, 7.0), 8),
        ],
    ),
    ")": (
        2.4,
        [
            _qbez_pts((0.2, 0.0), (2.0, 3.5), (0.2, 7.0), 8),
        ],
    ),
    "!": (
        1.8,
        [
            [(0.9, 0.0), (0.9, 4.7)],
            [(0.9, 6.6), (0.9, 6.6)],
        ],
    ),
    "?": (
        4.6,
        [
            _arc_pts(2.35, 1.7, 2.15, 1.7, -168, 45, 9)
            + [(2.2, 4.1), (2.2, 5.0)],
            [(2.2, 6.6), (2.2, 6.6)],
        ],
    ),
    "&": (
        5.2,
        [
            [(5.0, 6.8)]
            + _cbez_pts((5.0, 6.8), (1.0, 2.7), (0.5, 1.5), (1.1, 0.6), 6)
            + _arc_pts(2.1, 1.15, 1.15, 1.05, -135, 55, 8)
            + _cbez_pts((2.8, 2.0), (0.6, 3.6), (0.1, 4.7), (0.3, 5.7), 6)
            + _arc_pts(2.1, 5.4, 1.85, 1.6, 165, 18, 8)
            + [(4.8, 4.4)],
        ],
    ),
}


def _lookup_glyph(ch):
    """Resolve a character to its (advance_width, polylines) glyph definition."""
    upper = ch.upper()
    if upper in GLYPHS:
        return GLYPHS[upper]
    return GLYPHS[" "]


def text_width(text, scale, letter_gap=FONT_LETTER_GAP):
    """Return the pixel width of a single line of text at the given scale."""
    if not text:
        return 0.0
    total_units = 0.0
    for i, ch in enumerate(text):
        adv, _ = _lookup_glyph(ch)
        total_units += adv
        if i + 1 < len(text):
            total_units += letter_gap
    return total_units * float(scale)


def text_height(scale):
    """Return the nominal cap height in pixels for a given scale."""
    return FONT_CAP_HEIGHT * float(scale)


def wrap_text(text, max_width, scale, letter_gap=FONT_LETTER_GAP):
    """Split text into lines that each fit within max_width pixels at scale."""
    if not text:
        return [""]
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        if not words:
            lines.append("")
            continue
        current = ""
        for word in words:
            candidate = word if not current else f"{current} {word}"
            if text_width(candidate, scale, letter_gap) <= max_width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                    current = ""
                if text_width(word, scale, letter_gap) <= max_width:
                    current = word
                else:
                    chunk = ""
                    for ch in word:
                        next_chunk = chunk + ch
                        if chunk and text_width(next_chunk, scale, letter_gap) > max_width:
                            lines.append(chunk)
                            chunk = ch
                        else:
                            chunk = next_chunk
                    current = chunk
        if current:
            lines.append(current)
    return lines


def _rasterize_glyph_mask(polylines, scale_ss, thick_ss, qx, qy):
    """Build a sparse [(dx, dy, alpha), ...] coverage mask for a glyph at SS scale."""
    half_w = max(0.5, float(thick_ss) * 0.5)
    outer = half_w + 0.5
    inner = max(0.0, half_w - 0.5)
    outer_sq = outer * outer

    scaled_polys = []
    xs = []
    ys = []
    for poly in polylines:
        sp = [(qx + px * scale_ss, qy + py * scale_ss) for px, py in poly]
        scaled_polys.append(sp)
        for sx, sy in sp:
            xs.append(sx)
            ys.append(sy)
    if not xs:
        return []

    min_x = int(math.floor(min(xs) - outer))
    max_x = int(math.ceil(max(xs) + outer))
    min_y = int(math.floor(min(ys) - outer))
    max_y = int(math.ceil(max(ys) + outer))
    bw = max_x - min_x + 1
    bh = max_y - min_y + 1
    cov = [0.0] * (bw * bh)

    for sp in scaled_polys:
        n = len(sp)
        segs = (
            [(sp[0][0], sp[0][1], sp[0][0], sp[0][1])]
            if n == 1
            else [(sp[i][0], sp[i][1], sp[i + 1][0], sp[i + 1][1]) for i in range(n - 1)]
        )
        for ax, ay, bx, by in segs:
            smin_x = max(min_x, int(math.floor(min(ax, bx) - outer)))
            smax_x = min(max_x, int(math.ceil(max(ax, bx) + outer)))
            smin_y = max(min_y, int(math.floor(min(ay, by) - outer)))
            smax_y = min(max_y, int(math.ceil(max(ay, by) + outer)))
            dx = bx - ax
            dy = by - ay
            seg_len_sq = dx * dx + dy * dy
            if seg_len_sq < 1e-12:
                for py in range(smin_y, smax_y + 1):
                    dy0 = py - ay
                    dy0_sq = dy0 * dy0
                    row_k = (py - min_y) * bw - min_x
                    for px in range(smin_x, smax_x + 1):
                        dx0 = px - ax
                        d_sq = dx0 * dx0 + dy0_sq
                        if d_sq < outer_sq:
                            d = math.sqrt(d_sq)
                            alpha = 1.0 if d <= inner else (outer - d)
                            k = row_k + px
                            if alpha > cov[k]:
                                cov[k] = alpha
                continue
            inv_len_sq = 1.0 / seg_len_sq
            for py in range(smin_y, smax_y + 1):
                py_ay = py - ay
                row_k = (py - min_y) * bw - min_x
                for px in range(smin_x, smax_x + 1):
                    px_ax = px - ax
                    t = (px_ax * dx + py_ay * dy) * inv_len_sq
                    if t < 0.0:
                        t = 0.0
                    elif t > 1.0:
                        t = 1.0
                    cx = px_ax - t * dx
                    cy = py_ay - t * dy
                    d_sq = cx * cx + cy * cy
                    if d_sq < outer_sq:
                        d = math.sqrt(d_sq)
                        alpha = 1.0 if d <= inner else (outer - d)
                        k = row_k + px
                        if alpha > cov[k]:
                            cov[k] = alpha

    sparse = []
    for ly in range(bh):
        py = min_y + ly
        k_off = ly * bw
        for lx in range(bw):
            alpha = cov[k_off + lx]
            if alpha > 0.0:
                sparse.append((min_x + lx, py, alpha))
    return sparse


def _draw_glyph_cached(canvas, ch, gx_ss, gy_ss, scale_ss, thick_ss, color):
    """Blit a cached subpixel-accurate SDF glyph mask onto canvas."""
    _, polylines = _lookup_glyph(ch)
    if not polylines:
        return
    ix = math.floor(gx_ss)
    iy = math.floor(gy_ss)
    qx_bin = int((gx_ss - ix) * 4.0)
    qy_bin = int((gy_ss - iy) * 4.0)
    key = (ch.upper(), round(scale_ss, 4), round(thick_ss, 4), qx_bin, qy_bin)
    mask = canvas._glyph_cache.get(key)
    if mask is None:
        mask = _rasterize_glyph_mask(
            polylines, scale_ss, thick_ss, (qx_bin + 0.5) * 0.25, (qy_bin + 0.5) * 0.25
        )
        canvas._glyph_cache[key] = mask

    buf = canvas.buf
    w = canvas.width
    h = canvas.height
    cr, cg, cb = color
    for dx, dy, alpha in mask:
        px = ix + dx
        py = iy + dy
        if 0 <= px < w and 0 <= py < h:
            idx = (py * w + px) * 3
            if alpha >= 1.0:
                buf[idx] = cr
                buf[idx + 1] = cg
                buf[idx + 2] = cb
            else:
                inv = 1.0 - alpha
                buf[idx] = int(buf[idx] * inv + cr * alpha + 0.5)
                buf[idx + 1] = int(buf[idx + 1] * inv + cg * alpha + 0.5)
                buf[idx + 2] = int(buf[idx + 2] * inv + cb * alpha + 0.5)


def draw_text(
    canvas,
    x,
    y,
    text,
    scale,
    color,
    thickness=None,
    align="left",
    letter_gap=FONT_LETTER_GAP,
):
    """Render stroke-font text onto canvas at (x, y) with optional alignment."""
    if not text:
        return 0.0
    s = float(scale)
    t = max(1.0, s * 0.72) if thickness is None else float(thickness)
    total_w = text_width(text, s, letter_gap)

    if align == "center":
        cursor_x = float(x) - total_w * 0.5
    elif align == "right":
        cursor_x = float(x) - total_w
    else:
        cursor_x = float(x)

    ss = canvas.ss
    s_ss = s * ss
    t_ss = t * ss
    base_y_ss = float(y) * ss
    for ch in text:
        adv, _ = _lookup_glyph(ch)
        _draw_glyph_cached(canvas, ch, cursor_x * ss, base_y_ss, s_ss, t_ss, color)
        cursor_x += (adv + letter_gap) * s
    return total_w


# =============================================================================
# 4. PURE-PYTHON PNG ENCODER (ZLIB + STRUCT)
# =============================================================================

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
PNG_ZLIB_LEVEL = 9


def _png_chunk(chunk_type, data):
    """Build a single PNG chunk with big-endian length and CRC32."""
    crc = zlib.crc32(chunk_type)
    crc = zlib.crc32(data, crc) & 0xFFFFFFFF
    return struct.pack(">I", len(data)) + chunk_type + data + struct.pack(">I", crc)


def encode_png(canvas):
    """Encode an RGB24 Canvas deterministically as PNG bytes."""
    width = canvas.width
    height = canvas.height
    stride = width * 3
    buf = memoryview(canvas.buf)

    # Filter type 0 (None) prepended to every scanline
    raw = bytearray((stride + 1) * height)
    dst_stride = stride + 1
    for row in range(height):
        dst_off = row * dst_stride
        raw[dst_off] = 0
        src_off = row * stride
        raw[dst_off + 1 : dst_off + dst_stride] = buf[src_off : src_off + stride]

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    idat = zlib.compress(bytes(raw), level=PNG_ZLIB_LEVEL)

    return b"".join(
        (
            PNG_SIGNATURE,
            _png_chunk(b"IHDR", ihdr),
            _png_chunk(b"IDAT", idat),
            _png_chunk(b"IEND", b""),
        )
    )


def write_png(canvas, filepath):
    """Write encoded PNG bytes to filepath."""
    png_bytes = encode_png(canvas)
    with open(filepath, "wb") as f:
        f.write(png_bytes)
    return len(png_bytes)


# =============================================================================
# 5. PAGE SECTIONS: MASTHEAD, PANELS, PLACEHOLDERS & FOOTER
# =============================================================================

def draw_masthead(canvas):
    """Draw the newspaper masthead: top rule, title, date, and double rule."""
    cx = WIDTH * 0.5
    left = CONTENT_X
    right = CONTENT_X + CONTENT_W

    # Top rule line (bold bar + subtle hairline underneath)
    canvas.fill_rect(left, MASTHEAD["top_rule_y"], CONTENT_W, 3, COLOR_INK)
    canvas.fill_rect(left, MASTHEAD["top_rule_y"] + 5, CONTENT_W, 1, COLOR_INK)

    # Main masthead title with display tracking
    draw_text(
        canvas,
        cx,
        MASTHEAD["title_y"],
        "THE WORLD IN ONE DAY",
        scale=MASTHEAD["title_scale"],
        color=COLOR_INK,
        thickness=MASTHEAD["title_thickness"],
        align="center",
        letter_gap=2.15,
    )

    # Subtitle date in accent red with subtle flanking rules
    date_str = "TUESDAY 24 NOVEMBER 2026"
    date_gap = 1.80
    date_w = text_width(date_str, MASTHEAD["date_scale"], letter_gap=date_gap)
    date_mid_y = MASTHEAD["date_y"] + text_height(MASTHEAD["date_scale"]) * 0.5
    flank_gap = 18
    left_flank_end = int(cx - date_w * 0.5 - flank_gap)
    right_flank_start = int(cx + date_w * 0.5 + flank_gap)
    if left_flank_end > left + 20:
        canvas.draw_hline(left, left_flank_end, date_mid_y, COLOR_RULE_LIGHT, thickness=1)
        canvas.draw_hline(right_flank_start, right, date_mid_y, COLOR_RULE_LIGHT, thickness=1)

    draw_text(
        canvas,
        cx,
        MASTHEAD["date_y"],
        date_str,
        scale=MASTHEAD["date_scale"],
        color=COLOR_ACCENT_RED,
        thickness=MASTHEAD["date_thickness"],
        align="center",
        letter_gap=date_gap,
    )

    # Double rule line under the masthead
    canvas.fill_rect(left, MASTHEAD["double_rule_top_y"], CONTENT_W, 3, COLOR_INK)
    canvas.fill_rect(left, MASTHEAD["double_rule_bot_y"], CONTENT_W, 1, COLOR_INK)


def draw_panel_frames(canvas):
    """Draw the three empty bordered placeholder panel boxes with header bands."""
    for panel in PANELS:
        x = panel["x"]
        y = panel["y"]
        w = panel["w"]
        h = panel["h"]
        hdr_h = panel["header_h"]
        accent = panel["accent"]

        # Panel body fill
        canvas.fill_rect(x, y, w, h, COLOR_PANEL_BG)

        # Thin header band with top accent stripe and bottom divider
        canvas.fill_rect(x, y, w, hdr_h, COLOR_HEADER_BG)
        canvas.fill_rect(x, y, w, 4, accent)
        canvas.fill_rect(x, y + hdr_h - 1, w, 1, COLOR_INK)

        # Crisp outer border
        canvas.draw_rect(x, y, w, h, COLOR_INK, thickness=2)


def _lerp_color(c0, c1, t):
    """Deterministically interpolate between two RGB color tuples."""
    u = max(0.0, min(1.0, float(t)))
    return (
        int(c0[0] + (c1[0] - c0[0]) * u + 0.5),
        int(c0[1] + (c1[1] - c0[1]) * u + 0.5),
        int(c0[2] + (c1[2] - c0[2]) * u + 0.5),
    )


def _fill_vgradient(canvas, x, y, w, h, top_color, bot_color):
    """Fill a rectangle with a smooth vertical RGB gradient."""
    ss = canvas.ss
    ix0 = int(round(x * ss))
    ix1 = int(round((x + w) * ss))
    iy0 = int(round(y * ss))
    iy1 = int(round((y + h) * ss))
    ih = iy1 - iy0
    if ih <= 0:
        return
    denom = max(1, ih - 1)
    for row in range(ih):
        col = _lerp_color(top_color, bot_color, row / denom)
        canvas._fill_rect_ss(ix0, iy0 + row, ix1, iy0 + row + 1, col)


def _draw_dashed_arc(
    canvas,
    cx,
    cy,
    radius,
    start_deg,
    end_deg,
    color,
    thickness=2.2,
    dash_len=9.0,
    gap_len=6.0,
):
    """Draw a smooth circular dashed arc between start_deg and end_deg."""
    r = float(radius)
    if r <= 0.0:
        return
    a0 = math.radians(start_deg)
    a1 = math.radians(end_deg)
    total_ang = abs(a1 - a0)
    total_len = r * total_ang
    if total_len < 1e-6:
        return
    direction = 1.0 if a1 >= a0 else -1.0
    step = max(1.0, float(dash_len) + float(gap_len))
    pos = 0.0
    while pos < total_len:
        end_pos = min(total_len, pos + dash_len)
        seg_len = end_pos - pos
        substeps = max(3, int(math.ceil(seg_len / 2.0)))
        pts = []
        for i in range(substeps + 1):
            arc_s = pos + seg_len * (i / substeps)
            ang = a0 + direction * (arc_s / r)
            pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
        canvas.draw_polyline(pts, color, thickness=thickness, closed=False)
        pos += step


def _draw_panel_header_label(canvas, panel):
    """Draw the panel number badge and short kicker label in the header band."""
    x = panel["x"]
    y = panel["y"]
    accent = panel["accent"]

    # Small colored number badge on the left of the header band
    badge_x = x + 10
    badge_y = y + 7
    badge_w = 20
    badge_h = 17
    canvas.fill_rect(badge_x, badge_y, badge_w, badge_h, accent)
    draw_text(
        canvas,
        badge_x + badge_w * 0.5,
        badge_y + 3.4,
        panel["num"],
        scale=1.45,
        color=COLOR_WHITE,
        thickness=1.6,
        align="center",
    )

    # Kicker word beside the badge
    draw_text(
        canvas,
        badge_x + badge_w + 9,
        badge_y + 3.4,
        panel["kicker"],
        scale=1.45,
        color=COLOR_INK,
        thickness=1.45,
        align="left",
        letter_gap=1.65,
    )


def _draw_panel_text(canvas, panel, text_top_y):
    """Draw the word-wrapped headline and red sub-line in the lower part of a panel."""
    pad_x = 14
    tx = panel["x"] + pad_x
    max_w = panel["w"] - 2 * pad_x

    hl_scale = 2.55
    hl_thick = 2.35
    hl_gap = 1.62
    hl_step = 25.5
    hl_lines = wrap_text(panel["headline"], max_w, hl_scale, letter_gap=hl_gap)

    cur_y = float(text_top_y) - 2.0
    for line in hl_lines:
        draw_text(
            canvas,
            tx,
            cur_y,
            line,
            scale=hl_scale,
            color=COLOR_INK,
            thickness=hl_thick,
            align="left",
            letter_gap=hl_gap,
        )
        cur_y += hl_step

    # Comfortable vertical gap between headline and red sub-line
    cur_y += 6.5
    sub_scale = 1.5
    sub_thick = 1.38
    sub_gap = 1.56
    sub_step = 18.0
    sub_lines = wrap_text(panel["sub"], max_w, sub_scale, letter_gap=sub_gap)
    for line in sub_lines:
        draw_text(
            canvas,
            tx,
            cur_y,
            line,
            scale=sub_scale,
            color=COLOR_ACCENT_RED,
            thickness=sub_thick,
            align="left",
            letter_gap=sub_gap,
        )
        cur_y += sub_step


def _draw_scene_chip(canvas, x0, y0, w, h):
    """Panel 1 scene: bold computer chip with pins under a red prohibition sign."""
    canvas.fill_rect(x0, y0, w, h, COLOR_SCENE_BG)

    cx = x0 + w * 0.5
    cy = y0 + h * 0.5

    body_half = 39
    pin_len = 14
    pin_thick = 4
    pin_offsets = (-25, -15, -5, 5, 15, 25)

    # Short pins sticking out on all four sides
    for off in pin_offsets:
        # Top pins
        canvas.fill_rect(
            cx + off - pin_thick * 0.5,
            cy - body_half - pin_len,
            pin_thick,
            pin_len + 2,
            COLOR_CHIP_PIN,
        )
        canvas.fill_rect(
            cx + off - pin_thick * 0.5,
            cy - body_half - pin_len,
            pin_thick,
            3,
            COLOR_CHIP_PIN_TIP,
        )
        # Bottom pins
        canvas.fill_rect(
            cx + off - pin_thick * 0.5,
            cy + body_half - 2,
            pin_thick,
            pin_len + 2,
            COLOR_CHIP_PIN,
        )
        canvas.fill_rect(
            cx + off - pin_thick * 0.5,
            cy + body_half + pin_len - 3,
            pin_thick,
            3,
            COLOR_CHIP_PIN_TIP,
        )
        # Left pins
        canvas.fill_rect(
            cx - body_half - pin_len,
            cy + off - pin_thick * 0.5,
            pin_len + 2,
            pin_thick,
            COLOR_CHIP_PIN,
        )
        canvas.fill_rect(
            cx - body_half - pin_len,
            cy + off - pin_thick * 0.5,
            3,
            pin_thick,
            COLOR_CHIP_PIN_TIP,
        )
        # Right pins
        canvas.fill_rect(
            cx + body_half - 2,
            cy + off - pin_thick * 0.5,
            pin_len + 2,
            pin_thick,
            COLOR_CHIP_PIN,
        )
        canvas.fill_rect(
            cx + body_half + pin_len - 3,
            cy + off - pin_thick * 0.5,
            3,
            pin_thick,
            COLOR_CHIP_PIN_TIP,
        )

    # Dark square chip body with crisp bevel
    body_size = body_half * 2
    canvas.fill_rect(cx - body_half, cy - body_half, body_size, body_size, COLOR_CHIP_BODY)
    canvas.draw_rect(cx - body_half, cy - body_half, body_size, body_size, COLOR_INK, thickness=2)
    canvas.draw_rect(
        cx - body_half + 4,
        cy - body_half + 4,
        body_size - 8,
        body_size - 8,
        COLOR_CHIP_BEVEL,
        thickness=1,
    )
    # Pin-1 corner orientation dot
    canvas.fill_circle(cx - body_half + 10, cy - body_half + 10, 2.5, COLOR_GOLD)

    # Lighter inner square (silicon die)
    die_half = 22
    die_size = die_half * 2
    canvas.fill_rect(cx - die_half, cy - die_half, die_size, die_size, COLOR_CHIP_DIE)
    canvas.draw_rect(cx - die_half, cy - die_half, die_size, die_size, COLOR_INK, thickness=2)
    canvas.draw_rect(
        cx - die_half + 7,
        cy - die_half + 7,
        die_size - 14,
        die_size - 14,
        COLOR_CHIP_DIE_INNER,
        thickness=1,
    )

    # Bold red prohibition sign (thick red circle + thick diagonal slash)
    prohibit_r = 66.0
    slash_d = prohibit_r * math.sqrt(0.5)
    # Subtle light separation halo first so the red pops cleanly off the dark chip
    canvas.draw_circle(cx, cy, prohibit_r, COLOR_SCENE_BG, thickness=14.5)
    canvas.draw_line(
        cx - slash_d,
        cy - slash_d,
        cx + slash_d,
        cy + slash_d,
        COLOR_SCENE_BG,
        thickness=14.5,
    )
    # Main red prohibition ring and diagonal slash
    canvas.draw_circle(cx, cy, prohibit_r, COLOR_PROHIBIT_RED, thickness=10.5)
    canvas.draw_line(
        cx - slash_d,
        cy - slash_d,
        cx + slash_d,
        cy + slash_d,
        COLOR_PROHIBIT_RED,
        thickness=10.5,
    )

    canvas.draw_rect(x0, y0, w, h, COLOR_RULE_LIGHT, thickness=1)


def _draw_flag_ukraine(canvas, fx, fy, fw, fh):
    """Draw the Ukraine flag: top half blue, bottom half yellow."""
    half_h = fh // 2
    canvas.fill_rect(fx, fy, fw, half_h, COLOR_UA_BLUE)
    canvas.fill_rect(fx, fy + half_h, fw, fh - half_h, COLOR_UA_YELLOW)


def _draw_flag_russia(canvas, fx, fy, fw, fh):
    """Draw the Russia flag: three horizontal stripes white, blue, red."""
    y1 = fy + round(fh / 3.0)
    y2 = fy + round(2.0 * fh / 3.0)
    canvas.fill_rect(fx, fy, fw, y1 - fy, COLOR_WHITE)
    canvas.fill_rect(fx, y1, fw, y2 - y1, COLOR_RU_BLUE)
    canvas.fill_rect(fx, y2, fw, fy + fh - y2, COLOR_RU_RED)


def _draw_flag_usa(canvas, fx, fy, fw, fh):
    """Draw the USA flag: red/white stripes with a blue canton in top-left."""
    stripes = 7
    for i in range(stripes):
        sy0 = fy + round(i * fh / stripes)
        sy1 = fy + round((i + 1) * fh / stripes)
        col = COLOR_US_RED if i % 2 == 0 else COLOR_WHITE
        canvas.fill_rect(fx, sy0, fw, sy1 - sy0, col)

    canton_w = round(fw * 0.44)
    canton_h = round(4.0 * fh / stripes)
    canvas.fill_rect(fx, fy, canton_w, canton_h, COLOR_US_BLUE)

    # Crisp grid of tiny white stars inside the blue canton
    rows = 3
    cols = 4
    for r in range(rows):
        star_y = fy + (r + 0.5) * (canton_h / rows)
        for c in range(cols):
            star_x = fx + (c + 0.5) * (canton_w / cols)
            canvas.fill_circle(star_x, star_y, 0.9, COLOR_WHITE)


def _draw_flag_eu(canvas, fx, fy, fw, fh):
    """Draw the European Union flag: solid blue with a circle of yellow stars."""
    canvas.fill_rect(fx, fy, fw, fh, COLOR_EU_BLUE)
    ecx = fx + fw * 0.5
    ecy = fy + fh * 0.5
    ring_r = min(fw, fh) * 0.31
    for i in range(12):
        ang = (2.0 * math.pi * i) / 12.0 - math.pi * 0.5
        sx = ecx + ring_r * math.cos(ang)
        sy = ecy + ring_r * math.sin(ang)
        canvas.fill_circle(sx, sy, 1.35, COLOR_EU_GOLD)


def _draw_scene_talks(canvas, x0, y0, w, h):
    """Panel 2 scene: negotiation table seen from front with four flags on poles."""
    cx = x0 + w * 0.5

    # Clean backdrop wall and subtle floor band
    horizon_y = y0 + 114
    canvas.fill_rect(x0, y0, w, horizon_y - y0, (242, 239, 231))
    canvas.fill_rect(x0, horizon_y, w, y0 + h - horizon_y, (230, 224, 212))
    canvas.draw_hline(x0, x0 + w, horizon_y, (212, 205, 193), thickness=1)

    # Floor shadow rule under table legs
    floor_y = y0 + 162
    canvas.draw_hline(cx - 124, cx + 124, floor_y, (176, 169, 156), thickness=2)

    # Table legs
    leg_top = y0 + 140
    leg_h = floor_y - leg_top
    leg_w = 18
    for lx in (cx - 108, cx + 90):
        canvas.fill_rect(lx, leg_top, leg_w, leg_h, COLOR_TABLE_LEG)
        canvas.draw_rect(lx, leg_top, leg_w, leg_h, COLOR_INK, thickness=1)

    # Horizontal flat-topped table surface (slight front-view trapezoid)
    top_back_y = y0 + 110
    top_front_y = y0 + 129
    back_half = 114
    front_half = 128
    table_top_poly = [
        (cx - back_half, top_back_y),
        (cx + back_half, top_back_y),
        (cx + front_half, top_front_y),
        (cx - front_half, top_front_y),
    ]
    canvas.fill_polygon(table_top_poly, COLOR_TABLE_TOP)
    canvas.draw_polygon(table_top_poly, COLOR_INK, thickness=1.6)

    # Table front apron / thickness
    apron_h = 11
    canvas.fill_rect(cx - front_half, top_front_y, front_half * 2, apron_h, COLOR_TABLE_FRONT)
    canvas.draw_rect(cx - front_half, top_front_y, front_half * 2, apron_h, COLOR_INK, thickness=2)

    # Four small flags on thin poles standing on the tabletop, side by side
    flag_w = 46
    flag_h = 30
    flag_gap = 14
    total_group_w = 4 * flag_w + 3 * flag_gap
    group_left = cx - total_group_w * 0.5
    stand_y = y0 + 119
    pole_top_y = y0 + 30
    flag_y = y0 + 35

    flag_drawers = (
        _draw_flag_ukraine,
        _draw_flag_russia,
        _draw_flag_usa,
        _draw_flag_eu,
    )

    for idx, draw_flag_fn in enumerate(flag_drawers):
        pole_x = group_left + idx * (flag_w + flag_gap)
        fx = int(round(pole_x + 1))

        # Tabletop stand base
        canvas.fill_rect(pole_x - 8, stand_y - 1, 16, 4, (56, 48, 42))
        canvas.fill_rect(pole_x - 5, stand_y - 4, 10, 3, (88, 78, 70))

        # Thin vertical pole + small gold finial
        canvas.draw_line(pole_x, stand_y - 3, pole_x, pole_top_y, COLOR_POLE, thickness=2.0)
        canvas.fill_circle(pole_x, pole_top_y - 1.5, 2.4, COLOR_GOLD)

        # Flag rectangle + crisp 1px border
        draw_flag_fn(canvas, fx, flag_y, flag_w, flag_h)
        canvas.draw_rect(fx, flag_y, flag_w, flag_h, (34, 36, 42), thickness=1)

    canvas.draw_rect(x0, y0, w, h, COLOR_RULE_LIGHT, thickness=1)


def _transform_points(points, cx, cy, angle_deg):
    """Rotate local (x, y) points by angle_deg and translate to (cx, cy)."""
    rad = math.radians(angle_deg)
    ca = math.cos(rad)
    sa = math.sin(rad)
    return [(cx + px * ca - py * sa, cy + px * sa + py * ca) for px, py in points]


def _draw_scene_kadiz(canvas, x0, y0, w, h):
    """Panel 3 scene: fighter jet in sky, dashed KADIZ arc, sea with waves, Ulleung island."""
    horizon_y = y0 + 114
    sea_h = (y0 + h) - horizon_y

    # Sky and sea gradients
    _fill_vgradient(canvas, x0, y0, w, horizon_y - y0, COLOR_SKY_TOP, COLOR_SKY_BOT)
    _fill_vgradient(canvas, x0, horizon_y, w, sea_h, COLOR_SEA_TOP, COLOR_SEA_BOT)
    canvas.draw_hline(x0, x0 + w, horizon_y, (24, 56, 98), thickness=1)

    # Short white wave strokes across the sea
    waves = (
        (x0 + 18, horizon_y + 13, 22),
        (x0 + 62, horizon_y + 24, 26),
        (x0 + 24, horizon_y + 39, 20),
        (x0 + 108, horizon_y + 16, 24),
        (x0 + 96, horizon_y + 44, 28),
        (x0 + 148, horizon_y + 31, 18),
        (x0 + 52, horizon_y + 50, 18),
    )
    for wx, wy, wlen in waves:
        canvas.draw_line(wx, wy, wx + wlen, wy, COLOR_WAVE, thickness=1.6)

    # Small dark rocky island mound (Ulleung) rising from the sea on the right
    ix = x0 + 216
    iy_base = horizon_y + 22
    island_poly = [
        (ix - 38, iy_base),
        (ix - 24, horizon_y + 2),
        (ix - 12, horizon_y - 10),
        (ix + 2, horizon_y - 18),
        (ix + 16, horizon_y - 8),
        (ix + 28, horizon_y + 5),
        (ix + 38, iy_base),
    ]
    canvas.fill_polygon(island_poly, COLOR_ISLAND)
    # Sunlit left-ridge facet for depth
    island_lit_poly = [
        (ix - 34, iy_base),
        (ix - 24, horizon_y + 2),
        (ix - 12, horizon_y - 10),
        (ix + 2, horizon_y - 18),
        (ix - 4, horizon_y + 4),
        (ix - 10, iy_base),
    ]
    canvas.fill_polygon(island_lit_poly, COLOR_ISLAND_LIT)
    # Crisp shoreline surf stroke beneath the island
    canvas.draw_line(ix - 41, iy_base, ix + 41, iy_base, COLOR_WAVE, thickness=1.6)

    # ULLEUNG label beneath the island in the sea
    draw_text(
        canvas,
        ix,
        iy_base + 11,
        "ULLEUNG",
        scale=1.35,
        color=COLOR_WHITE,
        thickness=1.45,
        align="center",
    )

    # Dashed KADIZ arc sweeping across the sky
    _draw_dashed_arc(
        canvas,
        cx=x0 + 284,
        cy=y0 + 290,
        radius=276.0,
        start_deg=220.0,
        end_deg=268.0,
        color=COLOR_ACCENT_RED,
        thickness=2.4,
        dash_len=9.0,
        gap_len=6.0,
    )
    # KADIZ label near the dashed arc
    draw_text(
        canvas,
        x0 + 224,
        y0 + 50,
        "KADIZ",
        scale=1.45,
        color=COLOR_ACCENT_RED,
        thickness=1.55,
        align="center",
    )

    # Subtle trailing flight-path dashes behind the jet
    canvas.draw_dashed_line(
        x0 + 16,
        y0 + 54,
        x0 + 54,
        y0 + 49,
        (246, 249, 252),
        thickness=1.6,
        dash_len=7.0,
        gap_len=5.0,
    )

    # Bold fighter-jet silhouette (pointed nose, swept wings, tail fins)
    jet_upper = [
        (42.0, 0.0),
        (22.0, -3.5),
        (10.0, -5.0),
        (-6.0, -30.5),
        (-15.0, -30.5),
        (-13.0, -7.8),
        (-21.0, -7.2),
        (-30.0, -17.5),
        (-36.0, -16.5),
        (-31.0, -5.5),
        (-34.5, -2.5),
        (-30.0, 0.0),
    ]
    jet_local = jet_upper + [(px, -py) for px, py in reversed(jet_upper[1:-1])]
    jet_pts = _transform_points(jet_local, x0 + 98, y0 + 44, angle_deg=-7.0)
    canvas.fill_polygon(jet_pts, COLOR_JET)
    canvas.draw_polygon(jet_pts, COLOR_JET, thickness=1.0)

    canvas.draw_rect(x0, y0, w, h, COLOR_RULE_LIGHT, thickness=1)


def draw_panel_artwork(canvas):
    """Draw header labels, illustrated scenes, and headlines/sub-lines for the 3 panels."""
    scene_drawers = {
        "panel_1": _draw_scene_chip,
        "panel_2": _draw_scene_talks,
        "panel_3": _draw_scene_kadiz,
    }
    scene_pad_x = 12
    scene_top_off = 38
    scene_h = 174
    text_top_off = 225

    for panel in PANELS:
        _draw_panel_header_label(canvas, panel)
        sx = panel["x"] + scene_pad_x
        sy = panel["y"] + scene_top_off
        sw = panel["w"] - 2 * scene_pad_x
        scene_drawers[panel["id"]](canvas, sx, sy, sw, scene_h)
        _draw_panel_text(canvas, panel, panel["y"] + text_top_off)


def _draw_section_header(canvas, x, y, width, title):
    """Draw a newspaper section header: bold ink title followed by a crisp rule line."""
    title_scale = 2.05
    title_thick = 2.20
    title_gap = 1.90
    title_w = text_width(title, title_scale, letter_gap=title_gap)
    mid_y = y + text_height(title_scale) * 0.5

    draw_text(
        canvas,
        x,
        y,
        title,
        scale=title_scale,
        color=COLOR_INK,
        thickness=title_thick,
        align="left",
        letter_gap=title_gap,
    )

    rule_x0 = int(round(x + title_w + 12))
    rule_x1 = int(round(x + width))
    if rule_x1 > rule_x0 + 10:
        canvas.draw_hline(rule_x0, rule_x1, mid_y, COLOR_INK, thickness=2)


def _wrap_styled_words(runs, max_width, scale, letter_gap=FONT_LETTER_GAP):
    """Word-wrap mixed-style (text, color, thickness) runs into lines within max_width."""
    styled_words = []
    for text, color, thickness in runs:
        for word in text.split():
            styled_words.append((word, color, thickness))
    if not styled_words:
        return []

    lines = []
    current_line = []
    current_plain = ""
    for item in styled_words:
        word = item[0]
        candidate = word if not current_plain else f"{current_plain} {word}"
        if text_width(candidate, scale, letter_gap) <= max_width or not current_line:
            current_line.append(item)
            current_plain = candidate
        else:
            lines.append(current_line)
            current_line = [item]
            current_plain = word
    if current_line:
        lines.append(current_line)
    return lines


def _draw_styled_line(canvas, x, y, styled_words, scale, letter_gap=FONT_LETTER_GAP):
    """Render a single line of mixed-style (word, color, thickness) tokens."""
    s = float(scale)
    ss = canvas.ss
    s_ss = s * ss
    space_adv, _ = _lookup_glyph(" ")
    cursor_x = float(x)
    base_y_ss = float(y) * ss

    for idx, (word, color, thickness) in enumerate(styled_words):
        if idx > 0:
            cursor_x += (space_adv + letter_gap) * s
        t_ss = float(thickness) * ss
        for ch in word:
            adv, _ = _lookup_glyph(ch)
            _draw_glyph_cached(canvas, ch, cursor_x * ss, base_y_ss, s_ss, t_ss, color)
            cursor_x += (adv + letter_gap) * s


def draw_numbers_strip(canvas):
    """Draw Section 1: BY THE NUMBERS header and 4x2 key figures grid."""
    sec = NUMBERS_STRIP
    x = sec["x"]
    w = sec["w"]
    grid_y = sec["grid_y"]
    grid_h = sec["grid_h"]
    cols = sec["cols"]
    rows = sec["rows"]

    _draw_section_header(canvas, x, sec["y"], w, sec["title"])

    # Light card interior and subtle outer rule border
    canvas.fill_rect(x, grid_y, w, grid_h, COLOR_PANEL_BG)
    canvas.draw_rect(x, grid_y, w, grid_h, COLOR_RULE_LIGHT, thickness=1)

    col_w = w // cols
    row_h = grid_h // rows

    # Tidy thin dividers between columns and rows
    for c in range(1, cols):
        vx = x + c * col_w
        canvas.draw_vline(vx, grid_y + 1, grid_y + grid_h - 1, COLOR_RULE_LIGHT, thickness=1)
    for r in range(1, rows):
        hy = grid_y + r * row_h
        canvas.draw_hline(x + 1, x + w - 1, hy, COLOR_RULE_LIGHT, thickness=1)

    pad_x = 12
    cell_text_w = col_w - 2 * pad_x
    num_scale = 3.55
    num_thick = 3.25
    num_gap = 1.68
    cap_scale = 1.37
    cap_thick = 1.28
    cap_gap = 1.54
    cap_step = 14.5

    for idx, (number_str, caption_str) in enumerate(BY_THE_NUMBERS_ITEMS):
        r = idx // cols
        c = idx % cols
        cell_x = x + c * col_w
        cell_y = grid_y + r * row_h
        tx = cell_x + pad_x

        # Large bold accent-red figure
        draw_text(
            canvas,
            tx,
            cell_y + 7.5,
            number_str,
            scale=num_scale,
            color=COLOR_ACCENT_RED,
            thickness=num_thick,
            align="left",
            letter_gap=num_gap,
        )

        # Small ink caption wrapped to cell width with clean separation
        cap_lines = wrap_text(caption_str, cell_text_w, cap_scale, letter_gap=cap_gap)
        cur_y = cell_y + 43.0
        for line in cap_lines:
            draw_text(
                canvas,
                tx,
                cur_y,
                line,
                scale=cap_scale,
                color=COLOR_INK,
                thickness=cap_thick,
                align="left",
                letter_gap=cap_gap,
            )
            cur_y += cap_step


def draw_news_columns(canvas):
    """Draw Section 2: MORE OF THE DAY header and 5 numbered brief items."""
    sec = NEWS_SECTION
    x = sec["x"]
    w = sec["w"]

    _draw_section_header(canvas, x, sec["y"], w, sec["title"])

    item_scale = 1.72
    item_gap_char = 1.56
    bold_thick = 1.98
    reg_thick = 1.24
    line_step = 18.8
    item_gap = 11.4

    cur_y = float(sec["list_y"]) + 1.0
    cap_h = text_height(item_scale)

    for headline_str, detail_str in MORE_OF_THE_DAY_ITEMS:
        runs = [
            (headline_str, COLOR_INK, bold_thick),
            (detail_str, COLOR_INK, reg_thick),
        ]
        lines = _wrap_styled_words(runs, w, item_scale, letter_gap=item_gap_char)
        for line_idx, styled_words in enumerate(lines):
            _draw_styled_line(
                canvas,
                x,
                cur_y + line_idx * line_step,
                styled_words,
                item_scale,
                letter_gap=item_gap_char,
            )
        item_height = (len(lines) - 1) * line_step + cap_h
        cur_y += item_height + item_gap


def draw_footer(canvas):
    """Draw the bottom footer rule and small centered attribution line."""
    canvas.fill_rect(CONTENT_X, FOOTER["rule_y"], CONTENT_W, 2, COLOR_INK)
    draw_text(
        canvas,
        WIDTH * 0.5,
        FOOTER["text_y"],
        FOOTER["text"],
        scale=FOOTER["text_scale"],
        color=COLOR_INK_MUTED,
        thickness=FOOTER["text_thickness"],
        align="center",
        letter_gap=1.60,
    )


# =============================================================================
# 6. MAIN ENTRYPOINT
# =============================================================================

def render_page():
    """Assemble and return the 1024x1024 newspaper infographic Canvas."""
    canvas = Canvas(WIDTH, HEIGHT, bg_color=COLOR_PAPER, supersample=SUPERSAMPLE)
    draw_masthead(canvas)
    draw_panel_frames(canvas)
    draw_panel_artwork(canvas)
    draw_numbers_strip(canvas)
    draw_news_columns(canvas)
    draw_footer(canvas)
    return canvas.downsample()


def main():
    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    if not output_dir:
        output_dir = "out"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "entry.png")

    canvas = render_page()
    byte_size = write_png(canvas, output_path)
    print(f"Wrote {output_path} ({byte_size} bytes)")


if __name__ == "__main__":
    main()
