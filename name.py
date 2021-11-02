"""A class that holds a name."""
from __future__ import annotations
from abc import ABC

from dataclasses import dataclass, field
from functools import total_ordering
import math
from typing import (
    DefaultDict,
    Dict,
    List,
    Literal,
    Tuple,
    ClassVar,
    cast,
)
from enum import Enum, auto
from collections import defaultdict
import random
from namegen.namechoose import generate, nat_lookup, MASCULINE, FEMININE
import operator


@total_ordering
@dataclass
class Name:
    parts: List[str]
    sort_order: Tuple[int, ...]
    seperator: ClassVar[str] = " "
    case_sensitive: ClassVar[bool] = False

    def __init__(
        self, parts: List[str], sort_order: None | Tuple[int, ...] = None
    ):
        if sort_order is None:
            self.sort_order = tuple(range(0, len(parts)))
        else:
            self.sort_order = sort_order
        self.parts = parts

    def _sort_str(self) -> str:
        ret = ""
        for index in self.sort_order:
            ret += "".join([x for x in self.parts[index]])
        return ret if Name.case_sensitive else ret.lower()

    def __eq__(self, other: object):
        if not isinstance(other, Name):
            return NotImplemented
        return self._sort_str() == other._sort_str()

    def __lt__(self, other: object):
        if not isinstance(other, Name):
            return NotImplemented
        return self._sort_str() < other._sort_str()

    def __str__(self) -> str:
        return Name.seperator.join(self.parts)

    def __repr__(self) -> str:
        return f"Name(parts={self.parts!r},sort_order={self.sort_order!r})"


@dataclass
class Relationship:
    type: Literal[
        "Parent", "Child", "Sibling", "Pibling", "Nibling", "Cousin", "Friend"
    ]
    weight: float
    rel_from: str
    rel_to: str


@dataclass
class Maslow_Need(ABC):
    class TYPES(Enum):
        PHYSIOLOGICAL = auto()
        SAFETY = auto()
        BELONGING = auto()
        ESTEEM = auto()
        COGNITIVE = auto()
        AESTHETIC = auto()
        SELFACTUALIZATION = auto()
        TRANSCENDENCE = auto()

        def __str__(self):
            return self.name

        def __repr__(self):
            return self.name

    type: TYPES = field(repr=False)
    weight: float | Literal["DEFAULT"]


@dataclass
class Need(Maslow_Need):
    subtype: str

    def __init__(
        self,
        need_type: Maslow_Need.TYPES,
        subtype: str,
        weight: float | Literal["DEFAULT"],
    ):
        self.subtype = subtype
        super().__init__(type=need_type, weight=weight)


class NeedFactory:
    registered_needs: Dict[Maslow_Need.TYPES, Tuple[str, ...]] = dict()

    def register_need(
        self, name: Maslow_Need.TYPES, subtypes: Tuple[str, ...]
    ):
        self.registered_needs[name] = tuple([x.upper() for x in subtypes])

    def create_need(
        self,
        type: Maslow_Need.TYPES,
        subtype: str,
        weight: float | Literal["DEFAULT"] = "DEFAULT",
    ) -> Need:
        subtype = subtype.upper()
        if subtype not in self.registered_needs[type]:
            raise ValueError(
                f"{subtype} is not in allowed types:"
                f" {self.registered_needs[type]}"
            )
        return Need(type, subtype, weight)


class WEIGHTS:
    NORMAL_1_10 = ((1, 10), (1, 2, 2.62, 4.24, 6.85, 6.85, 4.24, 2.62, 2, 1))
    NORMAL_3_18 = (
        (3, 18),
        (
            0.46,
            1.39,
            2.78,
            4.63,
            6.94,
            9.72,
            11.57,
            12.50,
            12.50,
            11.57,
            9.72,
            6.94,
            4.63,
            2.78,
            1.39,
            0.46,
        ),
    )


def compress_range(num: int):
    return int(math.sqrt(num * 15))


@dataclass
class Person:
    class STAT_TYPES(Enum):
        STRENGTH = auto()
        DEXTERITY = auto()
        CONSTITUTION = auto()
        INTELLIGENCE = auto()
        WISDOM = auto()
        CHARISMA = auto()
        PREDICTABILITY = auto()
        LAWFULLNESS = auto()

        def __str__(self):
            return self.name

        def __repr__(self):
            return self.name

    @staticmethod
    def __gen_stat_dict() -> Dict[Person.STAT_TYPES, int]:
        ret: Dict[Person.STAT_TYPES, int] = dict()
        stat: Person.STAT_TYPES
        for stat in Person.STAT_TYPES:
            _range, _weights = WEIGHTS.NORMAL_3_18
            ret[stat] = random.choices(
                range(_range[0], _range[1] + 1),
                weights=_weights,
                k=1,
            )[0]
            # reduce odds of those significantly outside of normal range 6-14
            if (
                stat != Person.STAT_TYPES.PREDICTABILITY
                or Person.STAT_TYPES.LAWFULLNESS
                and random.randint(
                    0, 4 * len(Person.STAT_TYPES.__members__) - 2
                )
                == 0
            ):
                ret[stat] = compress_range(ret[stat])
        return ret

    def __get_alignment(
        self,
    ) -> Tuple[
        Literal["LAWFUL", "NEUTRAL", "CHAOTIC"],
        Literal["GOOD", "NEUTRAL", "EVIL"],
    ]:
        # 3-8
        # 8-13
        # 13-18
        pred_stat = self.stats[Person.STAT_TYPES.PREDICTABILITY]
        law_stat = self.stats[Person.STAT_TYPES.LAWFULLNESS]
        pred = ""
        law = ""
        if pred_stat >= 13:
            pred = "NEUTRAL"
        elif pred_stat >= 8:
            pred = "LAWFUL"
        else:
            pred = "CHAOTIC"
        if law_stat >= 13:
            law = "GOOD"
        elif law_stat >= 8:
            law = "NEUTRAL"
        else:
            law = "EVIL"
        return (pred, law)

    name: Name
    relationships: List[Relationship] = field(default_factory=list)
    demands: DefaultDict[Maslow_Need.TYPES, List[Maslow_Need]] = field(
        default_factory=lambda: cast(
            DefaultDict[Maslow_Need.TYPES, List[Maslow_Need]],
            defaultdict(list),
        )
    )
    stats: Dict[STAT_TYPES, int] = field(default_factory=__gen_stat_dict)
    alignment: Tuple[str, str] = ("", "")

    def __post_init__(self):
        self.alignment = self.__get_alignment()


needFactory = NeedFactory()
needFactory.register_need(
    Maslow_Need.TYPES.PHYSIOLOGICAL,
    ("Food", "Drink", "Shelter", "Climate", "Sleep"),
)
needFactory.register_need(
    Maslow_Need.TYPES.SAFETY, ("Security", "Order", "Stability")
)
needFactory.register_need(
    Maslow_Need.TYPES.BELONGING, ("Friendship", "Trust", "Affiliating")
)
needFactory.register_need(
    Maslow_Need.TYPES.ESTEEM, ("Achievement", "Mastery", "Status", "Prestige")
)
needFactory.register_need(
    Maslow_Need.TYPES.COGNITIVE, ("Knowledge", "Curiosity")
)
needFactory.register_need(Maslow_Need.TYPES.AESTHETIC, ("Art", "Music"))
needFactory.register_need(Maslow_Need.TYPES.SELFACTUALIZATION, ("Growth",))
needFactory.register_need(
    Maslow_Need.TYPES.TRANSCENDENCE, ("Spiritual", "Religious", "Scientific")
)

people: List[Person] = list()
for _ in range(1, 100):
    # gender=MASCULINE
    name: List[str]
    romanised: List[str]
    name, romanised, gender, nationality, parts = generate(
        nationality=nat_lookup("Fantasy"), verbosity=0
    )
    if len(romanised) > 0:
        name_parts: List[str] = romanised
    else:
        name_parts = name

    pair: List[Tuple[str, ...]] = list()
    for i, _ in enumerate(name_parts):  # type ignore
        pair.append((parts[i], str(i)))

    pair = sorted(pair, key=operator.itemgetter(0))
    pair_sort_order = tuple([int(x[1]) for x in pair])

    p = Person(name=Name(name_parts, sort_order=pair_sort_order))
    p.demands[Maslow_Need.TYPES.PHYSIOLOGICAL].append(
        needFactory.create_need(
            Maslow_Need.TYPES.PHYSIOLOGICAL, subtype="Food"
        )
    )
    p.demands[Maslow_Need.TYPES.PHYSIOLOGICAL].append(
        needFactory.create_need(
            Maslow_Need.TYPES.PHYSIOLOGICAL, subtype="Drink"
        )
    )
    people.append(p)
people.sort(key=lambda h: (h.name))
print(*people, sep="\n")
