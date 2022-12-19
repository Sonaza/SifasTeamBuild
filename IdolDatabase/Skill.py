# Copyright (c) 2019, The Holy Constituency of the Summer Triangle All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and
#    the following disclaimerin the documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Edited from: https://github.com/summertriangle-dev/arposandra/blob/master/libcard2/dataclasses.py

# import struct
from collections import namedtuple
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict, Any
# from weakref import ref

# from dataclasses_json import dataclass_json, config as JSONConfig

from .SkillEnum import TT

# @dataclass_json
@dataclass
class Skill(object):
    @dataclass
    class TargetType(object):
        id: int
        self_only: bool
        not_self: bool
        apply_count: int

        owner_party: bool
        owner_school: bool
        owner_year: bool
        owner_subunit: bool
        owner_attribute: bool
        owner_role: bool

        fixed_attributes: List[int] = field(default_factory=list)
        fixed_members: List[int] = field(default_factory=list)
        fixed_subunits: List[int] = field(default_factory=list)
        fixed_schools: List[int] = field(default_factory=list)
        fixed_years: List[int] = field(default_factory=list)
        fixed_roles: List[int] = field(default_factory=list)

        def is_all_but(self):
            return (self.fixed_attributes and len(self.fixed_attributes) >= 4) or (
                self.fixed_roles and len(self.fixed_roles) > 3
            )

    @dataclass
    class Condition(object):
        condition_type: int
        condition_value: int

    Effect = namedtuple(
        "Effect",
        (
            "target_parameter",
            "effect_type",
            "effect_value",
            "scale_type",
            "calc_type",
            "timing",
            "finish_type",
            "finish_value",
        ),
    )

    id: int
    name: str
    description: str

    skill_type: int
    sp_gauge_point: int
    icon_asset_path: str
    thumbnail_asset_path: str
    rarity: int

    trigger_type: int
    trigger_probability: int

    target: TargetType
    target_2: Optional[TargetType]
    conditions: List[Condition] = field(default_factory=list)
    levels: List[Effect] = field(default_factory=list)
    levels_2: Optional[List[Effect]] = field(default_factory=lambda: None)

    is_squashed: bool = field(init=False, default=False)

    def has_complex_trigger(self):
        return self.trigger_type != TT.Non

    def get_tl_set(self):
        a = {self.name, self.description}
        return a

