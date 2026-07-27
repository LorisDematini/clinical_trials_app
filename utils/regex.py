import re

NCT_ID_PATTERN = re.compile(r"^NCT\d{8}$")

DOI_PATTERN = re.compile(
    r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+"
)

PHASE_PATTERN = re.compile(
    r"\bphase\s+([IVX\d]+(?:\s*[,/]\s*[IVX\d]+)?)\b",
    re.I,
)


TOTAL_PATTERN = re.compile(
    r"""
        (?<![\w.])(?<![\w,])
        ([\d][\d,]*)
        (?![.,])
        (?:\s+(?:screened|enrolled|randomized|randomised|treated|eligible|included|evaluable|analyzed|analysed))*
        (?:\s+[A-Za-z]+(?:-[A-Za-z]+)*)*
        \s+
        (?:patients?|participants?|subjects?|individuals?)\b
    """,
    re.I | re.X,
)

DATE = r"""
(?:\d{1,2},?\s+)?
(?:early[- ]|mid[- ]|late[- ])?
(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|
Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|
Nov(?:ember)?|Dec(?:ember)?)
\s+
(?:\d{1,2},?\s+)?
\d{4}
"""
# Of 1657 patients screened between 13 December 2018 and 9 February 2021,
DATE_PATTERN = re.compile(
    rf"""
    (?:between|from)\s+
    ({DATE})
    \s*,?\s*
    (?:and|to|through)
    \s*,?\s*
    ({DATE})
    """,
    re.I | re.X,
)

DESIGN_PATTERNS = [
    "randomized",
    "randomised",
    "double-blind",
    "double blind",
    "single-blind",
    "open-label",
    "placebo-controlled",
    "placebo controlled",
    " controlled",
    "multicenter",
    "multi-center",
    "single-arm",
    "double-arm",
    "three-arm",
]