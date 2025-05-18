import logging
from typing import Union, Iterator, Mapping
from etl.transformer.protocols import Parser

class FixedWidthParser(Parser):
    """
    Parses a NOAA GSOD .op file using fixed-width slices
    per the official readme.txt. Yields 21 base fields + 6 FRSHTT flags = 27.
    """
    # (start is inclusive; end is exclusive; 0-based indexing)
    COL_SPECS = [
        ("STN---",      0,   6),    #  1-6
        ("WBAN",        7,  12),    #  8-12
        ("YEARMODA",   14,  22),    # 15-22 (year+month+day)
        ("TEMP_value", 24,  30),    # 25-30
        ("TEMP_obs",   31,  33),    # 32-33
        ("DEWP_value", 35,  41),    # 36-41
        ("DEWP_obs",   42,  44),    # 43-44
        ("SLP_value",  46,  52),    # 47-52
        ("SLP_obs",    53,  55),    # 54-55
        ("STP_value",  57,  63),    # 58-63
        ("STP_obs",    64,  66),    # 65-66
        ("VISIB_value",68,  73),    # 69-73
        ("VISIB_obs",  74,  76),    # 75-76
        ("WDSP_value", 78,  83),    # 79-83
        ("WDSP_obs",   84,  86),    # 85-86
        ("MXSPD",      88,  93),    # 89-93
        ("GUST",       95, 100),    # 96-100
        ("MAX",       102, 108),    #103-108
        ("MIN",       110, 116),    #111-116
        ("PRCP",      118, 123),    #119-123
        ("SNDP",      125, 130),    #126-130
        ("FRSHTT",    132, 138),    #133-138
    ]

    def __init__(self, logger: Union[logging.Logger, None] = None) -> None:
        self.logger = logger or logging.getLogger(self.__class__.__name__)

    def parse(self, lines: Iterator[str]) -> Iterator[Mapping[str, str]]:
        # 1) skip header
        header = next(lines, None)
        if header:
            self.logger.debug(f"Discarding header: {header.strip()}")

        # 2) process data lines
        for lineno, raw_line in enumerate(lines, start=2):
            if not raw_line.strip():
                continue
            line = raw_line.rstrip("\n")

            # 3) slice out each of the 21 base fields
            record: dict[str, str] = {}
            for name, start, end in self.COL_SPECS:
                piece = line[start:end] if len(line) >= start else ""
                record[name] = piece.strip()

            # 4) expand the 6-char FRSHTT into six flag fields
            frs = record.pop("FRSHTT", "")
            if len(frs) != 6:
                self.logger.debug(
                    f"Line {lineno}: malformed FRSHTT (expected 6 chars, got {len(frs)})"
                )
                continue

            record["FRSHTT_fog"]     = frs[0]
            record["FRSHTT_rain"]    = frs[1]
            record["FRSHTT_snow"]    = frs[2]
            record["FRSHTT_hail"]    = frs[3]
            record["FRSHTT_thunder"] = frs[4]
            record["FRSHTT_tornado"] = frs[5]

            yield record
