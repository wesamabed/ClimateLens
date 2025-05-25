# etl/transformer/ipcc_transformer.py
import logging
import re
from pathlib import Path
from typing import List, Dict, Any

from pdfminer.high_level import extract_text

class IPCCTransformer:
    """
    Extract text from a PDF and yield chunks (≤250 words)
    with {section, paragraph, text}.
    """

    HEADER_FOOTER_RE = re.compile(r"^\s*(SPM|Summary for Policymakers|\d+)\s*$")
    SECTION_RE       = re.compile(
        r"""
        ^\s*(
              [A-Z]\.?\d*(?:\.\d+)*     # A. , B.2 , A.1.3
            | FAQ\s+\d+\.\d+            # FAQ 3.2
            | Figure\s+SPM\.\d+         # Figure SPM.2
        )\s*$""",
        re.X,
    )
    MAX_WORDS = 250

    def __init__(self, logger: logging.Logger) -> None:
        self.log = (logger or logging.getLogger(__name__)).getChild(self.__class__.__name__)

    # --------------------------------------------------------------------- #
    def transform(self, pdf_paths: List[Path]) -> List[Dict[str, Any]]:
        all_chunks: list[dict[str, Any]] = []
        for pdf in pdf_paths:
            self.log.info("Extracting text ⇒ %s", pdf)
            raw_text = extract_text(str(pdf))
            chunks   = self._process_text(raw_text)
            all_chunks.extend(chunks)

        self.log.info("IPCC transform: %d chunks", len(all_chunks))
        return all_chunks

    # --------------------------------------------------------------------- #
    def _process_text(self, raw: str) -> List[Dict[str, Any]]:
        current_section  = "unknown"
        paragraph_num    = 0
        para_buffer: list[str] = []
        chunks: list[dict[str, Any]] = []

        for line in raw.splitlines():
            line = line.strip()

            # ignore headers / footers
            if self.HEADER_FOOTER_RE.match(line):
                continue

            # section heading?
            m = self.SECTION_RE.match(line)
            if m:
                current_section = m.group(1)
                paragraph_num   = 0  # reset enumeration per section
                continue  # section titles don't become content paragraphs

            # blank line → flush buffer
            if not line:
                paragraph_num, para_buffer = self._flush_if_any(
                    para_buffer, current_section, paragraph_num, chunks
                )
                continue

            # accumulate line (merge short wraps)
            if para_buffer and len(para_buffer[-1]) < 60:
                para_buffer[-1] = para_buffer[-1] + " " + line
            else:
                para_buffer.append(line)

        # flush tail
        self._flush_if_any(para_buffer, current_section, paragraph_num, chunks)
        return chunks

    # ------------------------------------------------------------------ #
    def _flush_if_any(
        self,
        buf: list[str],
        section: str,
        paragraph_num: int,
        out: list[dict[str, Any]],
    ):
        if not buf:
            return paragraph_num, []

        paragraph_num += 1
        paragraph_text = " ".join(buf).strip()

        if section == "unknown":
            if paragraph_text.lower().startswith("introduction"):
                section = "0.Introduction"          
            else:
                # skip front-matter (authors, citation, etc.)
                self.log.debug("dropping front-matter paragraph %r", paragraph_text[:60])
                return paragraph_num, []            

        # split into ≤ MAX_WORDS chunks
        words = paragraph_text.split()
        for i in range(0, len(words), self.MAX_WORDS):
            chunk_words = words[i : i + self.MAX_WORDS]
            out.append(
                {
                    "section": section,
                    "paragraph": paragraph_num,
                    "text": " ".join(chunk_words),
                }
            )

        return paragraph_num, []

