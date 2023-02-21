from dataclasses import dataclass, field
from typing import Any, Optional

from dacite import from_dict


@dataclass
class Test:
    a: Optional[Any]
    b: Optional[dict]


a = from_dict(data_class=Test, data={'a':{}})
if a.a is not None:
    print("hello")