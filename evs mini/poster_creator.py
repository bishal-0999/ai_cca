"""
poster_creator.py
=================
Creates a premium, beautiful environmental awareness poster using Pillow.

Design inspired by modern award-winning poster layouts:
- Rich dark-to-medium green gradient background
- Large glowing hero emoji (Earth) at top center with light rays
- Bold white headline on gradient
- Gold decorative divider
- Semi-transparent frosted white card for message + tips
- Dark footer band with gold italic slogan
- Botanical leaf corner decorations
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math
import os

# ── Canvas size ────────────────────────────────────────────────────────────────
W = 900    # width in pixels
H = 1200   # height in pixels (portrait)

# ── Color palette ──────────────────────────────────────────────────────────────
C_BG_TOP      = (15,  60,  20)   # very dark forest green
C_BG_MID      = (27,  94,  32)   # dark green
C_BG_BOT      = (38, 110,  44)   # medium green
C_WHITE       = (255, 255, 255)
C_CREAM       = (248, 252, 240)
C_GOLD        = (255, 200,  60)
C_GOLD_DARK   = (180, 130,  20)
C_DARK_TEXT   = (20,  55,  22)
C_LIGHT_GREEN = (180, 230, 185)
C_FOOTER_BG   = (12,  48,  16)


def _load_font(size: int, bold: bool = False):
    """Try to load a nice system font; fall back to Pillow default."""
    candidates = []
    if bold:
        candidates = [
            "/System/Library/Fonts/Helvetica.ttc",
            "/Library/Fonts/Arial Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
        ]
    else:
        candidates = [
            "/System/Library/Fonts/Helvetica.ttc",
            "/Library/Fonts/Arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "C:/Windows/Fonts/arial.ttf",
        ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def _wrap_text(text: str, font, max_width: int, draw: ImageDraw.ImageDraw):
    """Wrap text into lines that fit within max_width pixels."""
    words = text.split()
    lines, current = [], ""
    for word in words:
        test = (current + " " + word).strip()
        w = draw.textbbox((0, 0), test, font=font)[2]
        if w <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _draw_gradient_bg(img: Image.Image):
    """Smooth vertical gradient background: dark top → medium green bottom."""
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        if t < 0.5:
            # top half: BG_TOP → BG_MID
            s = t / 0.5
            r = int(C_BG_TOP[0] + (C_BG_MID[0] - C_BG_TOP[0]) * s)
            g = int(C_BG_TOP[1] + (C_BG_MID[1] - C_BG_TOP[1]) * s)
            b = int(C_BG_TOP[2] + (C_BG_MID[2] - C_BG_TOP[2]) * s)
        else:
            # bottom half: BG_MID → BG_BOT
            s = (t - 0.5) / 0.5
            r = int(C_BG_MID[0] + (C_BG_BOT[0] - C_BG_MID[0]) * s)
            g = int(C_BG_MID[1] + (C_BG_BOT[1] - C_BG_MID[1]) * s)
            b = int(C_BG_MID[2] + (C_BG_BOT[2] - C_BG_MID[2]) * s)
        draw.line([(0, y), (W, y)], fill=(r, g, b))


def _draw_glow(img: Image.Image, cx: int, cy: int, radius: int,
               color=(80, 180, 80), alpha_max: int = 60):
    """Draw a soft radial glow by compositing a blurred circle."""
    glow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow_layer)
    for r in range(radius, 0, -max(1, radius // 20)):
        a = int(alpha_max * (1 - r / radius) ** 1.5)
        gd.ellipse([(cx - r, cy - r), (cx + r, cy + r)],
                   fill=(color[0], color[1], color[2], a))
    glow_blur = glow_layer.filter(ImageFilter.GaussianBlur(radius // 5))
    img.alpha_composite(glow_blur)


def _draw_rays(img: Image.Image, cx: int, cy: int,
               ray_len: int = 220, n_rays: int = 16):
    """Draw golden light rays radiating from a center point."""
    ray_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(ray_layer)
    for i in range(n_rays):
        angle = math.radians(i * 360 / n_rays)
        # Each ray is a thin triangle
        spread = math.radians(6)
        a1 = angle - spread
        a2 = angle + spread
        tip_x  = cx + int(math.cos(angle) * ray_len)
        tip_y  = cy + int(math.sin(angle) * ray_len)
        left_x = cx + int(math.cos(a1) * 30)
        left_y = cy + int(math.sin(a1) * 30)
        rght_x = cx + int(math.cos(a2) * 30)
        rght_y = cy + int(math.sin(a2) * 30)
        rd.polygon([(tip_x, tip_y), (left_x, left_y), (rght_x, rght_y)],
                   fill=(255, 210, 80, 35))
    blurred = ray_layer.filter(ImageFilter.GaussianBlur(6))
    img.alpha_composite(blurred)


def _draw_corner_leaves(img: Image.Image):
    """Draw botanical leaf clusters in the four corners."""
    leaf_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(leaf_layer)

    def leaf(cx, cy, size, angle_deg, color=(50, 140, 55, 200)):
        """Draw a single elliptical leaf rotated at angle_deg."""
        # Create a tiny image for the rotated leaf
        leaf_img = Image.new("RGBA", (size * 3, size * 3), (0, 0, 0, 0))
        li = ImageDraw.Draw(leaf_img)
        li.ellipse([(size, size // 2), (size * 2, size * 2 + size // 2)],
                   fill=color)
        rotated = leaf_img.rotate(angle_deg, expand=True)
        rx, ry = rotated.size
        leaf_layer.alpha_composite(rotated, (cx - rx // 2, cy - ry // 2))

    # ── Top-left corner ──
    pairs_tl = [
        (50,  70, 55, 30,  (35, 120, 45, 220)),
        (90,  40, 45, 60,  (50, 145, 55, 200)),
        (20, 120, 40, 10,  (40, 130, 50, 180)),
        (110, 90, 35, 80,  (60, 155, 65, 160)),
        (140, 50, 30, 45,  (45, 135, 50, 140)),
    ]
    for (x, y, s, a, c) in pairs_tl:
        leaf(x, y, s, a, c)

    # ── Top-right corner ──
    pairs_tr = [
        (W - 50,  70, 55, -30, (35, 120, 45, 220)),
        (W - 90,  40, 45, -60, (50, 145, 55, 200)),
        (W - 20, 120, 40, -10, (40, 130, 50, 180)),
        (W - 110, 90, 35, -80, (60, 155, 65, 160)),
        (W - 140, 50, 30, -45, (45, 135, 50, 140)),
    ]
    for (x, y, s, a, c) in pairs_tr:
        leaf(x, y, s, a, c)

    # ── Bottom-left corner ──
    pairs_bl = [
        (50,  H - 70,  55, -30, (35, 120, 45, 220)),
        (90,  H - 40,  45, -60, (50, 145, 55, 200)),
        (20,  H - 120, 40, -10, (40, 130, 50, 180)),
        (110, H - 90,  35, -80, (60, 155, 65, 160)),
        (140, H - 50,  30, -45, (45, 135, 50, 140)),
    ]
    for (x, y, s, a, c) in pairs_bl:
        leaf(x, y, s, a, c)

    # ── Bottom-right corner ──
    pairs_br = [
        (W - 50,  H - 70,  55, 30,  (35, 120, 45, 220)),
        (W - 90,  H - 40,  45, 60,  (50, 145, 55, 200)),
        (W - 20,  H - 120, 40, 10,  (40, 130, 50, 180)),
        (W - 110, H - 90,  35, 80,  (60, 155, 65, 160)),
        (W - 140, H - 50,  30, 45,  (45, 135, 50, 140)),
    ]
    for (x, y, s, a, c) in pairs_br:
        leaf(x, y, s, a, c)

    img.alpha_composite(leaf_layer)


def _draw_gold_divider(draw: ImageDraw.ImageDraw, y: int, margin: int = 80):
    """Draw a decorative gold horizontal divider line with a center diamond."""
    # Left line
    draw.rectangle([margin, y - 1, W // 2 - 30, y + 1], fill=C_GOLD)
    # Right line
    draw.rectangle([W // 2 + 30, y - 1, W - margin, y + 1], fill=C_GOLD)
    # Center diamond ◆
    cx, cy, s = W // 2, y, 8
    draw.polygon([(cx, cy - s), (cx + s, cy), (cx, cy + s), (cx - s, cy)],
                 fill=C_GOLD)
    # Small dots
    for dx in [-45, 45]:
        draw.ellipse([(W // 2 + dx - 3, y - 3), (W // 2 + dx + 3, y + 3)],
                     fill=C_GOLD)


def _draw_frosted_card(img: Image.Image, x0: int, y0: int,
                       x1: int, y1: int, radius: int = 22, alpha: int = 230):
    """Draw a semi-transparent frosted white rounded rectangle."""
    card = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd   = ImageDraw.Draw(card)
    cd.rounded_rectangle([x0, y0, x1, y1], radius=radius,
                          fill=(255, 255, 255, alpha),
                          outline=(180, 230, 185, 180), width=2)
    img.alpha_composite(card)


def _draw_text_centered(draw, text, font, y, color, max_width,
                        line_spacing=8):
    """Draw centered, wrapped text. Returns the y position after last line."""
    # We need a temporary draw for wrapping measurement
    lines = _wrap_text(text, font, max_width, draw)
    bbox_h = draw.textbbox((0, 0), "Ag", font=font)
    lh = (bbox_h[3] - bbox_h[1]) + line_spacing
    for line in lines:
        bx = draw.textbbox((0, 0), line, font=font)
        lw = bx[2] - bx[0]
        draw.text(((W - lw) // 2, y), line, font=font, fill=color)
        y += lh
    return y


# ─────────────────────────────────────────────────────────────────────────────
def create_poster(topic: str, headline: str, message: str,
                  slogan: str, language: str) -> Image.Image:
    """
    Create a premium environmental awareness poster.

    Returns a PIL Image (RGB, 900×1200 px).
    """

    # ── 1. Base canvas (RGBA so we can alpha-composite layers) ──
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))

    # ── 2. Gradient background ──
    _draw_gradient_bg(img)

    # ── 3. Botanical corner leaves ──
    _draw_corner_leaves(img)

    # ── 4. Glow + rays around hero Earth emoji ──
    hero_cy = 210
    _draw_glow(img, W // 2, hero_cy, radius=220,
               color=(100, 210, 100), alpha_max=55)
    _draw_rays(img,  W // 2, hero_cy, ray_len=230, n_rays=18)

    # ── 5. Draw onto RGBA canvas ──
    draw = ImageDraw.Draw(img)

    # ── 6. Hero Earth emoji ──
    earth_font = _load_font(140)
    draw.text((W // 2, hero_cy), "🌍",
              font=earth_font, fill=C_WHITE, anchor="mm")

    # ── 7. HEADLINE ──
    gap = 30
    headline_y = hero_cy + 120

    headline_font = _load_font(52, bold=True)
    headline_lines = _wrap_text(headline, headline_font, W - 100, draw)
    lh_hl = 62
    for line in headline_lines:
        bx = draw.textbbox((0, 0), line, font=headline_font)
        lw = bx[2] - bx[0]
        # Subtle text shadow
        draw.text(((W - lw) // 2 + 2, headline_y + 2), line,
                  font=headline_font, fill=(0, 0, 0, 80))
        draw.text(((W - lw) // 2, headline_y), line,
                  font=headline_font, fill=C_WHITE)
        headline_y += lh_hl

    # ── 8. Gold decorative divider ──
    divider_y = headline_y + gap
    _draw_gold_divider(draw, divider_y)

    # ── 9. Frosted card background ──
    card_top    = divider_y + 28
    card_bottom = H - 160
    card_margin = 50
    _draw_frosted_card(img, card_margin, card_top,
                       W - card_margin, card_bottom, radius=24, alpha=228)

    # Re-create draw after compositing
    draw = ImageDraw.Draw(img)

    # ── 10. Awareness message ──
    msg_y    = card_top + 32
    msg_font = _load_font(22)
    msg_lines = _wrap_text(message, msg_font, W - card_margin * 2 - 60, draw)
    lh_msg = 34
    for line in msg_lines:
        bx = draw.textbbox((0, 0), line, font=msg_font)
        lw = bx[2] - bx[0]
        draw.text(((W - lw) // 2, msg_y), line, font=msg_font, fill=C_DARK_TEXT)
        msg_y += lh_msg

    # ── 11. Thin green divider between message and tips ──
    msg_y += 14
    draw.rectangle([card_margin + 60, msg_y, W - card_margin - 60, msg_y + 2],
                   fill=(100, 180, 105, 160))
    msg_y += 18

    # ── 12. Three tips with leaf bullets ──
    tip_font   = _load_font(20)
    tip_emojis = ["🌱", "♻️", "💧"]
    tip_margin = card_margin + 70
    lh_tip     = 38

    for i, tip in enumerate([None, None, None]):  # placeholder loop
        pass  # we draw below using real tips passed in via closure

    # Store reference for tips (passed as closure workaround)
    # Tips are injected via caller; we use a global placeholder
    # → they are drawn in the main flow below

    msg_y += 5

    # ── Return img so caller can inject tips ──
    # (Tips injected by _finalize_poster called below)
    return img, draw, msg_y, tip_font, tip_margin, lh_tip, tip_emojis, \
           card_bottom, card_margin


def create_poster(topic: str, headline: str, message: str,
                  slogan: str, language: str) -> Image.Image:
    """
    Create a premium environmental awareness poster.
    Returns a PIL Image (RGB, 900×1200 px).
    """

    # ── 1. Base canvas ──
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))

    # ── 2. Gradient background ──
    _draw_gradient_bg(img)

    # ── 3. Botanical corner leaves ──
    _draw_corner_leaves(img)

    # ── 4. Glow + rays ──
    hero_cy = 205
    _draw_glow(img, W // 2, hero_cy, radius=210,
               color=(90, 200, 95), alpha_max=50)
    _draw_rays(img, W // 2, hero_cy, ray_len=240, n_rays=18)

    draw = ImageDraw.Draw(img)

    # ── 5. Hero Earth emoji ──
    earth_font = _load_font(130)
    draw.text((W // 2, hero_cy), "🌍",
              font=earth_font, fill=C_WHITE, anchor="mm")

    # ── 6. HEADLINE ──
    hl_top  = hero_cy + 115
    hl_font = _load_font(50, bold=True)
    hl_lines = _wrap_text(headline.upper(), hl_font, W - 90, draw)
    lh_hl   = 60
    hl_y    = hl_top

    for line in hl_lines:
        bx = draw.textbbox((0, 0), line, font=hl_font)
        lw = bx[2] - bx[0]
        # Drop shadow
        draw.text(((W - lw) // 2 + 2, hl_y + 2), line,
                  font=hl_font, fill=(0, 30, 5))
        # Main text
        draw.text(((W - lw) // 2, hl_y), line, font=hl_font, fill=C_WHITE)
        hl_y += lh_hl

    # ── 7. Gold divider ──
    div_y = hl_y + 18
    _draw_gold_divider(draw, div_y)

    # ── 8. Frosted card ──
    card_top    = div_y + 26
    card_bottom = H - 152
    card_x0     = 48
    card_x1     = W - 48
    _draw_frosted_card(img, card_x0, card_top, card_x1, card_bottom,
                       radius=26, alpha=225)
    draw = ImageDraw.Draw(img)  # refresh draw after composite

    # ── 9. "AWARENESS MESSAGE" label inside card ──
    lbl_font = _load_font(13, bold=True)
    lbl_text = "✦  AWARENESS MESSAGE  ✦"
    bx       = draw.textbbox((0, 0), lbl_text, font=lbl_font)
    draw.text(((W - (bx[2] - bx[0])) // 2, card_top + 18),
              lbl_text, font=lbl_font, fill=(80, 150, 85))

    # ── 10. Message text ──
    msg_y    = card_top + 46
    msg_font = _load_font(21)
    msg_lines = _wrap_text(message, msg_font, W - card_x0 * 2 - 60, draw)
    lh_msg   = 33

    for line in msg_lines:
        bx = draw.textbbox((0, 0), line, font=msg_font)
        lw = bx[2] - bx[0]
        draw.text(((W - lw) // 2, msg_y), line,
                  font=msg_font, fill=C_DARK_TEXT)
        msg_y += lh_msg

    # ── 11. Divider inside card ──
    msg_y += 12
    draw.rectangle([card_x0 + 50, msg_y, card_x1 - 50, msg_y + 1],
                   fill=(150, 200, 155))
    msg_y += 16

    # ── 12. "SIMPLE TIPS" label ──
    lbl2 = "✦  3 SIMPLE TIPS  ✦"
    bx2  = draw.textbbox((0, 0), lbl2, font=lbl_font)
    draw.text(((W - (bx2[2] - bx2[0])) // 2, msg_y),
              lbl2, font=lbl_font, fill=(80, 150, 85))
    msg_y += 26

    # ── 13. Tips ──
    tip_font   = _load_font(19)
    tip_emojis = ["🌱", "♻️", "💧"]
    lh_tip     = 44
    tip_max_w  = W - card_x0 * 2 - 110
    tips_list  = slogan  # placeholder — real tips injected below

    # (tips come from parameter — we need them as a list)
    # The function signature doesn't include tips… let me add them:
    # ✅ See note: tips are passed separately via monkey-patch workaround
    # We'll store them in a module-level variable set by app.py

    # Actually, let me just accept tips as a parameter properly —
    # The signature is updated below; this inner block is superseded.
    pass

    return img.convert("RGB")


# ── FINAL clean implementation ─────────────────────────────────────────────────

def create_poster(topic: str, headline: str, message: str,
                  tips: list, slogan: str, language: str) -> Image.Image:
    """
    Create a premium environmental awareness poster.

    Parameters:
    -----------
    topic    : Topic name (shown in footer badge)
    headline : Main bold headline
    message  : Awareness message (2–3 sentences)
    tips     : List of 3 tip strings
    slogan   : Catchy slogan
    language : Language of the content

    Returns a PIL Image (RGB, 900×1200 px).
    """

    # ── 1. Canvas ──
    img  = Image.new("RGBA", (W, H), (0, 0, 0, 255))

    # ── 2. Gradient ──
    _draw_gradient_bg(img)

    # ── 3. Corner leaves ──
    _draw_corner_leaves(img)

    # ── 4. Hero glow + rays ──
    hero_cy = 200
    _draw_glow(img, W // 2, hero_cy, radius=220,
               color=(90, 195, 95), alpha_max=55)
    _draw_rays(img, W // 2, hero_cy, ray_len=245, n_rays=18)

    draw = ImageDraw.Draw(img)

    # ── 5. Earth emoji hero ──
    e_font = _load_font(128)
    draw.text((W // 2, hero_cy), "🌍", font=e_font, anchor="mm")

    # ── 6. Headline (uppercase, white, bold, centered) ──
    hl_font  = _load_font(48, bold=True)
    hl_lines = _wrap_text(headline.upper(), hl_font, W - 80, draw)
    hl_y     = hero_cy + 112

    for line in hl_lines:
        bx = draw.textbbox((0, 0), line, font=hl_font)
        lw = bx[2] - bx[0]
        # shadow
        draw.text(((W - lw) // 2 + 2, hl_y + 2), line,
                  font=hl_font, fill=(0, 25, 5))
        # text
        draw.text(((W - lw) // 2, hl_y), line,
                  font=hl_font, fill=C_WHITE)
        hl_y += 58

    # ── 7. Gold divider ──
    div_y = hl_y + 16
    _draw_gold_divider(draw, div_y)

    # ── 8. Frosted card ──
    CX0 = 46
    CX1 = W - 46
    CT  = div_y + 24
    CB  = H - 148

    _draw_frosted_card(img, CX0, CT, CX1, CB, radius=26, alpha=228)
    draw = ImageDraw.Draw(img)

    inner_w  = CX1 - CX0 - 70
    inner_cx = W // 2

    # ── 9. "AWARENESS MESSAGE" section label ──
    lbl_font = _load_font(12, bold=True)
    lbl1 = "✦   AWARENESS MESSAGE   ✦"
    bx   = draw.textbbox((0, 0), lbl1, font=lbl_font)
    draw.text(((W - (bx[2] - bx[0])) // 2, CT + 16),
              lbl1, font=lbl_font, fill=(70, 140, 75))

    # ── 10. Message ──
    msg_y    = CT + 42
    msg_font = _load_font(20)
    msg_lines = _wrap_text(message, msg_font, inner_w, draw)

    for line in msg_lines:
        bx = draw.textbbox((0, 0), line, font=msg_font)
        lw = bx[2] - bx[0]
        draw.text(((W - lw) // 2, msg_y), line,
                  font=msg_font, fill=C_DARK_TEXT)
        msg_y += 32

    # ── 11. Thin separator ──
    msg_y += 10
    draw.rectangle([CX0 + 60, msg_y, CX1 - 60, msg_y + 1],
                   fill=(160, 205, 165))
    msg_y += 14

    # ── 12. "SIMPLE TIPS" section label ──
    lbl2 = "✦   3 SIMPLE TIPS   ✦"
    bx2  = draw.textbbox((0, 0), lbl2, font=lbl_font)
    draw.text(((W - (bx2[2] - bx2[0])) // 2, msg_y),
              lbl2, font=lbl_font, fill=(70, 140, 75))
    msg_y += 28

    # ── 13. Tips ──
    tip_font   = _load_font(19)
    tip_emojis = ["🌱", "♻️", "💧"]
    tip_x0     = CX0 + 60
    tip_max_w  = CX1 - CX0 - 120

    for i, tip in enumerate(tips[:3]):
        emoji     = tip_emojis[i]
        # Draw emoji bullet
        draw.text((tip_x0, msg_y + 2), emoji, font=_load_font(20))
        # Draw tip text (wrapped if needed)
        tip_lines = _wrap_text(tip, tip_font, tip_max_w - 36, draw)
        ty = msg_y
        for tl in tip_lines:
            draw.text((tip_x0 + 36, ty), tl, font=tip_font, fill=C_DARK_TEXT)
            ty += 28
        msg_y = ty + 10

    # ── 14. Dark footer band ──
    footer_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(footer_layer)
    fd.rounded_rectangle([0, H - 140, W, H], radius=0,
                         fill=(*C_FOOTER_BG, 245))
    img.alpha_composite(footer_layer)
    draw = ImageDraw.Draw(img)

    # Gold top border of footer
    draw.rectangle([0, H - 142, W, H - 139], fill=C_GOLD)

    # ── 15. Slogan in footer ──
    slogan_font  = _load_font(28, bold=True)
    slogan_lines = _wrap_text(f'"{slogan}"', slogan_font, W - 80, draw)
    slogan_total = len(slogan_lines) * 40
    slogan_y     = H - 140 + (140 - slogan_total) // 2 - 10

    for line in slogan_lines:
        bx = draw.textbbox((0, 0), line, font=slogan_font)
        lw = bx[2] - bx[0]
        # Gold shadow
        draw.text(((W - lw) // 2 + 1, slogan_y + 1), line,
                  font=slogan_font, fill=C_GOLD_DARK)
        # Gold text
        draw.text(((W - lw) // 2, slogan_y), line,
                  font=slogan_font, fill=C_GOLD)
        slogan_y += 40

    # ── 16. Topic + language badge just above footer ──
    badge_font = _load_font(14, bold=True)
    badge_text = f"  Topic: {topic}   •   Language: {language}  "
    bx         = draw.textbbox((0, 0), badge_text, font=badge_font)
    bw         = bx[2] - bx[0] + 20
    bh         = 28
    bx0        = (W - bw) // 2
    by0        = H - 148 - bh - 6
    # Badge background
    badge_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd          = ImageDraw.Draw(badge_layer)
    bd.rounded_rectangle([bx0, by0, bx0 + bw, by0 + bh],
                         radius=14, fill=(76, 175, 80, 220))
    img.alpha_composite(badge_layer)
    draw = ImageDraw.Draw(img)
    tbx  = draw.textbbox((0, 0), badge_text, font=badge_font)
    draw.text(((W - (tbx[2] - tbx[0])) // 2, by0 + 7),
              badge_text, font=badge_font, fill=C_WHITE)

    # ── 17. Leaf emoji strip in footer (decorative) ──
    leaf_font = _load_font(20)
    leaf_y    = H - 30
    for lx in range(30, W - 30, 44):
        draw.text((lx, leaf_y), "🌿", font=leaf_font, anchor="mm")

    # ── 18. Convert to RGB and return ──
    return img.convert("RGB")
