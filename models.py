from dataclasses import dataclass, field
from typing import Union, Tuple


@dataclass
class Headline:
    title: str
    category: str
    url: str
    internal_url: str
    paywall: bool | None

    def __eq__(self, o: object) -> bool:
        if isinstance(o, Headline):
            return self.url == o.url and self.category == o.category
        raise NotImplementedError("Attempt to compare with non Headline")

    def __hash__(self) -> int:
        return hash(tuple(sorted(self.__dict__.items())))


@dataclass
class Article:
    title: str
    summary: str
    img: str
    url: str
    paragraphs: [Union[str, Tuple[str, str]]]  # str=text, (str, str)=url,text
    published_on: str = None
    updated_on: str = None
    see_also: [str] = field(default_factory=list)
