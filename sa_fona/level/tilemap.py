"""Tile-based level geometry: rendering and collision data.

Manages multiple layers (background, midground, foreground) where each
layer is a 2D grid of integer tile IDs.  Tile ID 0 means empty.
Collision categories are data-driven from the level JSON.

When a tileset surface is provided, tiles are rendered via 4-bit
auto-tiling: each solid tile's appearance is selected based on its
cardinal neighbors (UP=1, DOWN=2, LEFT=4, RIGHT=8).
"""

from __future__ import annotations

import pygame

# All tiles are 16x16 pixels.
TILE_SIZE: int = 16

# Auto-tile bitmask flags.
_AT_UP = 1
_AT_DOWN = 2
_AT_LEFT = 4
_AT_RIGHT = 8

# Placeholder colors for different collision categories.
_TILE_COLORS: dict[str, tuple[int, int, int]] = {
    "solid": (150, 150, 150),
    "one_way": (200, 200, 200),
    "hazard": (200, 50, 50),
    "breakable_slam": (180, 150, 50),
}
_DEFAULT_TILE_COLOR: tuple[int, int, int] = (120, 120, 120)

# Top-edge highlight colors for exposed terrain tiles.
# Warm tone for outdoor and talayot levels; cool tone for cave levels.
HIGHLIGHT_COLOR_OUTDOOR: tuple[int, int, int] = (235, 220, 180)
HIGHLIGHT_COLOR_CAVE: tuple[int, int, int] = (180, 190, 200)


class TileMap:
    """Tile-based level geometry: rendering and collision data.

    Manages multiple layers: background, midground (collision), foreground.
    Tiles are 16x16 pixels.

    Attributes:
        tile_size: Side length of each square tile in pixels.
    """

    tile_size: int = TILE_SIZE

    def __init__(self, tile_data: dict, tileset_surface: pygame.Surface | None = None) -> None:
        """Initialise the tilemap from parsed level JSON data.

        Args:
            tile_data: Parsed level JSON dict containing ``layers``,
                ``dimensions``, and ``collision_types``.
            tileset_surface: Optional tileset image for real rendering.
                Ignored in placeholder mode (current implementation).
        """
        dims = tile_data["dimensions"]
        self._width_tiles: int = dims["width"]
        self._height_tiles: int = dims["height"]

        # Deep-copy layers so mutations don't affect the source dict.
        self._layers: dict[str, list[list[int]]] = {}
        for name, grid in tile_data.get("layers", {}).items():
            self._layers[name] = [list(row) for row in grid]

        # Collision categories: maps category name to set of tile IDs.
        raw_collision = tile_data.get("collision_types", {})
        self._collision_types: dict[str, set[int]] = {
            category: set(ids) for category, ids in raw_collision.items()
        }

        self._tileset_surface = tileset_surface
        self._tileset_tiles: list[pygame.Surface] = []
        if tileset_surface is not None:
            self._slice_tileset(tileset_surface)

        # Build a lookup: tile_id -> collision category (for coloring).
        self._tile_id_to_category: dict[int, str] = {}
        for category, ids in self._collision_types.items():
            for tid in ids:
                self._tile_id_to_category[tid] = category

        # All non-zero tile IDs treated as "solid neighbors" for auto-tiling.
        self._solid_ids: set[int] = set()
        for ids in self._collision_types.values():
            self._solid_ids.update(ids)

        self._autotile_layers: dict[str, list[list[int]]] = {}
        if self._tileset_tiles:
            for layer_name, grid in self._layers.items():
                self._autotile_layers[layer_name] = self._compute_autotile(grid)

        # Choose top-edge highlight color based on tileset ID.
        tileset_id = tile_data.get("metadata", {}).get("tileset", "")
        if "cave" in tileset_id:
            self._highlight_color: tuple[int, int, int] = HIGHLIGHT_COLOR_CAVE
        else:
            self._highlight_color = HIGHLIGHT_COLOR_OUTDOOR

    # ── Collision queries ──────────────────────────────────────────

    def get_collision_rects(self, layer: str = "solid") -> list[pygame.Rect]:
        """Return axis-aligned bounding boxes for all tiles of a collision type.

        Args:
            layer: Collision category name (e.g. ``"solid"``, ``"one_way"``).

        Returns:
            List of ``pygame.Rect`` objects, one per matching tile.
        """
        tile_ids = self._collision_types.get(layer, set())
        if not tile_ids:
            return []

        rects: list[pygame.Rect] = []
        # Collision is checked against the midground layer.
        midground = self._layers.get("midground", [])
        for row_idx, row in enumerate(midground):
            for col_idx, tid in enumerate(row):
                if tid in tile_ids:
                    rects.append(pygame.Rect(
                        col_idx * TILE_SIZE,
                        row_idx * TILE_SIZE,
                        TILE_SIZE,
                        TILE_SIZE,
                    ))
        return rects

    # ── Tile accessors ─────────────────────────────────────────────

    def get_tile_at(self, x: int, y: int, layer: str) -> int:
        """Return the tile ID at grid position (x, y) in the given layer.

        Args:
            x: Column index (0-based).
            y: Row index (0-based).
            layer: Layer name (e.g. ``"midground"``).

        Returns:
            The integer tile ID, or 0 if out of bounds or layer missing.
        """
        grid = self._layers.get(layer)
        if grid is None:
            return 0
        if 0 <= y < len(grid) and 0 <= x < len(grid[y]):
            return grid[y][x]
        return 0

    def set_tile_at(self, x: int, y: int, layer: str, tile_id: int) -> None:
        """Set the tile ID at grid position (x, y) in the given layer.

        Args:
            x: Column index (0-based).
            y: Row index (0-based).
            layer: Layer name.
            tile_id: New tile ID to set.

        Raises:
            KeyError: If the layer does not exist.
            IndexError: If (x, y) is out of bounds.
        """
        grid = self._layers.get(layer)
        if grid is None:
            raise KeyError(f"Layer '{layer}' does not exist")
        if not (0 <= y < len(grid) and 0 <= x < len(grid[y])):
            raise IndexError(f"Tile position ({x}, {y}) out of bounds")
        grid[y][x] = tile_id

    # ── Tileset helpers ───────────────────────────────────────────

    def _slice_tileset(self, surface: pygame.Surface) -> None:
        """Slice a horizontal tileset strip into individual tile surfaces."""
        num = surface.get_width() // TILE_SIZE
        for i in range(num):
            rect = pygame.Rect(i * TILE_SIZE, 0, TILE_SIZE, TILE_SIZE)
            self._tileset_tiles.append(surface.subsurface(rect).copy())

    def _compute_autotile(self, grid: list[list[int]]) -> list[list[int]]:
        """Pre-compute auto-tile variant index for every cell in a grid."""
        h = len(grid)
        w = len(grid[0]) if h else 0
        result: list[list[int]] = []
        for row_idx in range(h):
            row_result: list[int] = []
            for col_idx in range(w):
                tid = grid[row_idx][col_idx]
                if tid == 0:
                    row_result.append(0)
                    continue
                mask = 0
                # Up neighbor (out-of-bounds = solid)
                if row_idx == 0 or grid[row_idx - 1][col_idx] in self._solid_ids:
                    mask |= _AT_UP
                # Down
                if row_idx == h - 1 or grid[row_idx + 1][col_idx] in self._solid_ids:
                    mask |= _AT_DOWN
                # Left
                if col_idx == 0 or grid[row_idx][col_idx - 1] in self._solid_ids:
                    mask |= _AT_LEFT
                # Right
                if col_idx == w - 1 or grid[row_idx][col_idx + 1] in self._solid_ids:
                    mask |= _AT_RIGHT
                row_result.append(mask)
            result.append(row_result)
        return result

    # ── Rendering ──────────────────────────────────────────────────

    def render_layer(
        self,
        surface: pygame.Surface,
        layer: str,
        camera_offset: tuple[int, int],
    ) -> None:
        """Render visible tiles of a layer onto the surface.

        Only tiles within the camera viewport are drawn (culling).
        For the midground layer, a 1px bright highlight line is drawn
        on the top edge of tiles that have no solid tile directly above
        (exposed terrain), giving depth and definition to platforms.

        Args:
            surface: Target pygame Surface.
            layer: Layer name to render.
            camera_offset: ``(offset_x, offset_y)`` -- the camera's top-left
                position in world coordinates.
        """
        grid = self._layers.get(layer)
        if grid is None:
            return

        cam_x, cam_y = camera_offset
        surf_w, surf_h = surface.get_size()

        # Calculate visible tile range.
        start_col = max(0, cam_x // TILE_SIZE)
        start_row = max(0, cam_y // TILE_SIZE)
        end_col = min(self._width_tiles, (cam_x + surf_w) // TILE_SIZE + 1)
        end_row = min(self._height_tiles, (cam_y + surf_h) // TILE_SIZE + 1)

        # Pre-fetch midground grid for top-edge highlight check.
        midground_grid = self._layers.get("midground")
        draw_highlights = layer == "midground" and midground_grid is not None

        for row_idx in range(start_row, end_row):
            for col_idx in range(start_col, end_col):
                tid = grid[row_idx][col_idx]
                if tid == 0:
                    continue

                screen_x = col_idx * TILE_SIZE - cam_x
                screen_y = row_idx * TILE_SIZE - cam_y

                if self._tileset_tiles:
                    at_grid = self._autotile_layers.get(layer)
                    if at_grid is not None:
                        mask = at_grid[row_idx][col_idx]
                    else:
                        mask = 0
                    idx = mask % len(self._tileset_tiles)
                    surface.blit(self._tileset_tiles[idx], (screen_x, screen_y))
                else:
                    color = self._color_for_tile(tid)
                    pygame.draw.rect(
                        surface, color,
                        (screen_x, screen_y, TILE_SIZE, TILE_SIZE),
                    )

                # Top-edge highlight: draw a 1px line at the top of midground
                # tiles whose tile directly above is empty (air).
                if draw_highlights:
                    tile_above = 0
                    if row_idx > 0:
                        tile_above = midground_grid[row_idx - 1][col_idx]
                    if tile_above == 0:
                        pygame.draw.line(
                            surface,
                            self._highlight_color,
                            (screen_x, screen_y),
                            (screen_x + TILE_SIZE - 1, screen_y),
                        )

    def _color_for_tile(self, tile_id: int) -> tuple[int, int, int]:
        """Determine the placeholder color for a tile ID.

        Args:
            tile_id: The tile identifier.

        Returns:
            An (R, G, B) color tuple.
        """
        category = self._tile_id_to_category.get(tile_id)
        if category is not None:
            return _TILE_COLORS.get(category, _DEFAULT_TILE_COLOR)
        return _DEFAULT_TILE_COLOR

    # ── Collision helpers ─────────────────────────────────────────

    def is_solid_at(self, tile_x: int, tile_y: int) -> bool:
        """Check whether the tile at grid position (tile_x, tile_y) is solid.

        Looks up the midground layer tile and checks if its ID belongs to
        the "solid" collision category.

        Args:
            tile_x: Column index (0-based).
            tile_y: Row index (0-based).

        Returns:
            True if the tile is solid, False otherwise (including out of
            bounds, which counts as non-solid / air).
        """
        tile_id = self.get_tile_at(tile_x, tile_y, "midground")
        if tile_id == 0:
            return False
        solid_ids = self._collision_types.get("solid", set())
        return tile_id in solid_ids

    # ── Dimension properties ───────────────────────────────────────

    @property
    def width_pixels(self) -> int:
        """Total level width in pixels."""
        return self._width_tiles * TILE_SIZE

    @property
    def height_pixels(self) -> int:
        """Total level height in pixels."""
        return self._height_tiles * TILE_SIZE

    @property
    def width_tiles(self) -> int:
        """Level width in tiles."""
        return self._width_tiles

    @property
    def height_tiles(self) -> int:
        """Level height in tiles."""
        return self._height_tiles
