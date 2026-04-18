"""Boss entity implementations and registry.

The boss registry maps boss IDs (strings) to their concrete BossEntity
subclass.  BossScene (and any future code that needs to instantiate a
boss by ID) should use ``get_boss_class()`` instead of importing a
concrete boss class directly.

New bosses are registered by adding an entry to ``_BOSS_REGISTRY``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sa_fona.entities.boss_entity import BossEntity

from sa_fona.entities.bosses.bou_de_pedra import BouDePedra

_BOSS_REGISTRY: dict[str, type[BossEntity]] = {
    "bou_de_pedra": BouDePedra,
}


def get_boss_class(boss_id: str) -> type[BossEntity]:
    """Look up a boss class by its identifier.

    Args:
        boss_id: The boss ID string (e.g. "bou_de_pedra").

    Returns:
        The concrete BossEntity subclass for that ID.

    Raises:
        ValueError: If the boss ID is not registered.
    """
    cls = _BOSS_REGISTRY.get(boss_id)
    if cls is None:
        registered = ", ".join(sorted(_BOSS_REGISTRY.keys()))
        raise ValueError(
            f"Unknown boss_id: {boss_id!r}. "
            f"Registered bosses: {registered}"
        )
    return cls
