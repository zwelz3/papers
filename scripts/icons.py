"""Inline SVG icon marks used across the site.

Sources: LinkedIn from Font Awesome Free (icons CC BY 4.0); GitHub, ORCID and
Creative Commons from Simple Icons (CC0). Attribution is noted in the README.
"""

# Inline SVG marks so the footer works offline and inherits the text color.
# Sources: LinkedIn from Font Awesome Free (CC BY 4.0); GitHub and ORCID from
# Simple Icons (CC0). See README for attribution.
ICONS = {
    "linkedin": (
        '<svg viewBox="0 0 448 512" aria-hidden="true" focusable="false"><path fill="currentColor" d="M416 32L31.9 32C14.3 32 0 46.5 0 64.3L0 447.7C0 465.5 14.3 480 31.9 480L416 480c17.6 0 32-14.5 32-32.3l0-383.4C448 46.5 433.6 32 416 32zM135.4 416l-66.4 0 0-213.8 66.5 0 0 213.8-.1 0zM102.2 96a38.5 38.5 0 1 1 0 77 38.5 38.5 0 1 1 0-77zM384.3 416l-66.4 0 0-104c0-24.8-.5-56.7-34.5-56.7-34.6 0-39.9 27-39.9 54.9l0 105.8-66.4 0 0-213.8 63.7 0 0 29.2 .9 0c8.9-16.8 30.6-34.5 62.9-34.5 67.2 0 79.7 44.3 79.7 101.9l0 117.2z"/></svg>'
    ),
    "github": (
        '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path fill="currentColor" d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/></svg>'
    ),
    "orcid": (
        '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path fill="currentColor" d="M12 0C5.372 0 0 5.372 0 12s5.372 12 12 12 12-5.372 12-12S18.628 0 12 0zM7.369 4.378c.525 0 .947.431.947.947s-.422.947-.947.947a.95.95 0 0 1-.947-.947c0-.525.422-.947.947-.947zm-.722 3.038h1.444v10.041H6.647V7.416zm3.562 0h3.9c3.712 0 5.344 2.653 5.344 5.025 0 2.578-2.016 5.025-5.325 5.025h-3.919V7.416zm1.444 1.303v7.444h2.297c3.272 0 4.022-2.484 4.022-3.722 0-2.016-1.284-3.722-4.097-3.722h-2.222z"/></svg>'
    ),
}


# --- content licenses -------------------------------------------------------
# Papers are licensed separately from the build code (see LICENSE-CONTENT.md).
LICENSES = {
    "CC0-1.0":         ("CC0 1.0",           "https://creativecommons.org/publicdomain/zero/1.0/"),
    "CC-BY-4.0":       ("CC BY 4.0",         "https://creativecommons.org/licenses/by/4.0/"),
    "CC-BY-SA-4.0":    ("CC BY-SA 4.0",      "https://creativecommons.org/licenses/by-sa/4.0/"),
    "CC-BY-ND-4.0":    ("CC BY-ND 4.0",      "https://creativecommons.org/licenses/by-nd/4.0/"),
    "CC-BY-NC-4.0":    ("CC BY-NC 4.0",      "https://creativecommons.org/licenses/by-nc/4.0/"),
    "CC-BY-NC-ND-4.0": ("CC BY-NC-ND 4.0",   "https://creativecommons.org/licenses/by-nc-nd/4.0/"),
    "ARR":             ("All rights reserved", ""),
}

CC_ICON = (
    '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false" class="cc-mark">'
    '<path fill="currentColor" d="M11.983 0c-3.292 0-6.19 1.217-8.428 3.485C1.25 5.819 0 8.844 0 12c0 3.189 1.217 6.148 3.522 8.45C5.827 22.75 8.822 24 11.983 24c3.16 0 6.222-1.25 8.593-3.583C22.815 18.214 24 15.287 24 12c0-3.255-1.186-6.214-3.458-8.483C18.238 1.217 15.275 0 11.983 0zm.033 2.17c2.7 0 5.103 1.02 6.98 2.893 1.843 1.841 2.83 4.274 2.83 6.937 0 2.696-.954 5.063-2.798 6.872-1.943 1.906-4.444 2.926-7.012 2.926-2.601 0-5.038-1.019-6.914-2.893-1.877-1.875-2.93-4.34-2.93-6.905 0-2.597 1.053-5.063 2.93-6.97 1.844-1.874 4.214-2.86 6.914-2.86zM8.68 8.278C6.723 8.278 5.165 9.66 5.165 12c0 2.38 1.465 3.722 3.581 3.722 1.358 0 2.516-.744 3.155-1.874l-1.491-.758c-.333.798-.839 1.037-1.478 1.037-1.105 0-1.61-.917-1.61-2.126 0-1.21.426-2.127 1.61-2.127.32 0 .96.173 1.332.97l1.597-.838c-.68-1.236-1.837-1.728-3.181-1.728zm6.932 0c-1.957 0-3.514 1.382-3.514 3.722 0 2.38 1.464 3.722 3.58 3.722 1.359 0 2.516-.744 3.155-1.874l-1.49-.758c-.333.798-.84 1.037-1.478 1.037-1.105 0-1.611-.917-1.611-2.126 0-1.21.426-2.127 1.61-2.127.32 0 .96.173 1.332.97l1.597-.838c-.68-1.236-1.837-1.728-3.181-1.728z"/></svg>'
)


def resolve_license(value, cfg: dict):
    """Accept an identifier string, an explicit {name,url} map, or None."""
    if not value:
        value = cfg.get("default_license")
    if not value:
        return None
    if isinstance(value, dict):
        name, url = value.get("name", ""), value.get("url", "")
        return (name, url) if name else None
    key = str(value).strip()
    if key in LICENSES:
        return LICENSES[key]
    return (key, "")  # unknown identifier: show it verbatim, no link


def render_license(entry, author: str, year: str) -> str:
    if not entry:
        return ""
    name, url = entry
    who = html.escape(author) if author else ""
    copy = f"&copy; {year} {who}".strip() if year or who else ""
    is_cc = name.upper().startswith("CC")
    mark = CC_ICON if is_cc else ""
    if url:
        lic = (f'<a href="{url}" rel="license noopener" target="_blank">'
               f"{mark}{html.escape(name)}</a>")
    else:
        lic = html.escape(name)
    sep = ". " if copy else ""
    return f'<p class="footer-license">{copy}{sep}{lic}</p>'

ICON_LABELS = {"linkedin": "LinkedIn", "github": "GitHub", "orcid": "ORCID"}

CC_ICON = (
    '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false" class="cc-mark">'
    '<path fill="currentColor" d="M11.983 0c-3.292 0-6.19 1.217-8.428 3.485C1.25 5.819 0 8.844 0 12c0 3.189 1.217 6.148 3.522 8.45C5.827 22.75 8.822 24 11.983 24c3.16 0 6.222-1.25 8.593-3.583C22.815 18.214 24 15.287 24 12c0-3.255-1.186-6.214-3.458-8.483C18.238 1.217 15.275 0 11.983 0zm.033 2.17c2.7 0 5.103 1.02 6.98 2.893 1.843 1.841 2.83 4.274 2.83 6.937 0 2.696-.954 5.063-2.798 6.872-1.943 1.906-4.444 2.926-7.012 2.926-2.601 0-5.038-1.019-6.914-2.893-1.877-1.875-2.93-4.34-2.93-6.905 0-2.597 1.053-5.063 2.93-6.97 1.844-1.874 4.214-2.86 6.914-2.86zM8.68 8.278C6.723 8.278 5.165 9.66 5.165 12c0 2.38 1.465 3.722 3.581 3.722 1.358 0 2.516-.744 3.155-1.874l-1.491-.758c-.333.798-.839 1.037-1.478 1.037-1.105 0-1.61-.917-1.61-2.126 0-1.21.426-2.127 1.61-2.127.32 0 .96.173 1.332.97l1.597-.838c-.68-1.236-1.837-1.728-3.181-1.728zm6.932 0c-1.957 0-3.514 1.382-3.514 3.722 0 2.38 1.464 3.722 3.58 3.722 1.359 0 2.516-.744 3.155-1.874l-1.49-.758c-.333.798-.84 1.037-1.478 1.037-1.105 0-1.611-.917-1.611-2.126 0-1.21.426-2.127 1.61-2.127.32 0 .96.173 1.332.97l1.597-.838c-.68-1.236-1.837-1.728-3.181-1.728z"/></svg>'
)


# Theme-toggle glyphs (sun / moon), drawn simply rather than borrowed.
SUN_ICON = (
    '<svg class="icon-sun" viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
    '<circle cx="12" cy="12" r="4.2" fill="currentColor"/>'
    '<g stroke="currentColor" stroke-width="1.9" stroke-linecap="round">'
    '<path d="M12 2.2v2.4M12 19.4v2.4M2.2 12h2.4M19.4 12h2.4"/>'
    '<path d="M5.1 5.1l1.7 1.7M17.2 17.2l1.7 1.7M18.9 5.1l-1.7 1.7M6.8 17.2l-1.7 1.7"/>'
    "</g></svg>"
)

MOON_ICON = (
    '<svg class="icon-moon" viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
    '<path fill="currentColor" d="M20.7 14.6A8.6 8.6 0 0 1 9.4 3.3a0.7 0.7 0 0 0-.9-.9'
    ' 9.9 9.9 0 1 0 13.1 13.1 0.7 0.7 0 0 0-.9-.9z"/></svg>'
)

THEME_TOGGLE = (
    '<button class="theme-toggle" type="button" aria-label="Toggle light or dark theme" '
    'title="Toggle theme">' + SUN_ICON + MOON_ICON + "</button>"
)
