import re
from typing import Any, List, Optional, Set

from TexSoup import RArg, TexCmd, TexNode, TexSoup, TokenWithPosition

from explanations.types import Bibitem


def _extract_label(bibitem: TexCmd) -> Optional[str]:
    for arg in bibitem.args:
        if isinstance(arg, RArg):
            return str(arg.value)
    return None


def extract_bibitems(tex: str) -> List[Bibitem]:
    extractor = BibitemExtractor()
    return extractor.extract(tex)


TEX_BREAK = r"\n\s*?\n"


def _clean_bibitem_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _contains_break(text: str) -> bool:
    return bool(re.search(TEX_BREAK, text))


def _get_text_before_break(text: str) -> str:
    return re.split(TEX_BREAK, text, maxsplit=1)[0]


class BibitemExtractor:
    def __init__(self) -> None:
        self.current_bibitem_label: Optional[str] = None
        self.bibitem_text = ""
        self.nodes_scanned: Set[TexNode] = set()
        self.bibitems: List[Bibitem] = []

    def extract(self, tex: str) -> List[Bibitem]:
        self.bibitems = []
        soup = TexSoup(tex)
        for bibitem in soup.find_all("bibitem"):
            parent = bibitem.parent
            if parent not in self.nodes_scanned:
                self.nodes_scanned.add(parent)
                for content in parent.contents:
                    self._process_content(content)
        self._finalize_bibitem()
        return self.bibitems

    def _process_content(self, content: Any) -> None:
        if isinstance(content, TexNode):
            cmd = content.expr
            if (isinstance(cmd, TexCmd)) and cmd.name == "bibitem":
                if self.current_bibitem_label is not None:
                    self._finalize_bibitem()
                self.current_bibitem_label = _extract_label(cmd)
                return

        content_text: Optional[str] = None
        if isinstance(content, TexNode) and content.string is not None:
            content_text = content.string
        elif isinstance(content, TokenWithPosition):
            content_text = str(content)

        if self.current_bibitem_label is not None and content_text is not None:
            if _contains_break(content_text):
                content_text = _get_text_before_break(content_text)
                self.bibitem_text += content_text
                self._finalize_bibitem()
            else:
                self.bibitem_text += content_text

    def _finalize_bibitem(self) -> None:
        if self.current_bibitem_label is not None:
            cleaned_text = _clean_bibitem_text(self.bibitem_text)
            bibitem = Bibitem(self.current_bibitem_label, cleaned_text)
            self.bibitems.append(bibitem)

        self.current_bibitem_label = None
        self.bibitem_text = ""
