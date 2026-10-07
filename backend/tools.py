"""Tools the Campus Customs shop agent can call, plus the Portkey client.

Everything here reads the catalogue/inventory **read-only**; the agent can look
things up but never change stock, prices, or user data. Tools return typed
models from models.py so the agent (and the chat UI) get structured product data.
"""

from __future__ import annotations

import json
import os
import sqlite3
from contextlib import closing
from pathlib import Path

from openai import OpenAI

from models import ProductCard, ProductSearchResult, SizeStock, StockResult

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent  # hw4/
DB_PATH = ROOT / "data" / "campus_customs.db"

SIZE_ORDER = ["XS", "S", "M", "L", "XL", "XXL"]
MAX_RESULTS = 8
PORTKEY_BASE_URL = os.getenv("PORTKEY_BASE_URL", "https://api.portkey.ai/v1")


# ---------------------------------------------------------------- data access

def _connect() -> sqlite3.Connection:
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found at {DB_PATH}")
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def _sizes_for(conn: sqlite3.Connection, product_id: str) -> list[SizeStock]:
    rows = conn.execute(
        "SELECT size, quantity FROM inventory WHERE product_id = ?", (product_id,)
    ).fetchall()
    sizes = [SizeStock(size=r["size"], quantity=r["quantity"]) for r in rows]
    sizes.sort(key=lambda s: SIZE_ORDER.index(s.size) if s.size in SIZE_ORDER else 99)
    return sizes


def _card(conn: sqlite3.Connection, row: sqlite3.Row) -> ProductCard:
    sizes = _sizes_for(conn, row["product_id"])
    return ProductCard(
        product_id=row["product_id"],
        name=row["name"],
        garment_type=row["garment_type"],
        description=row["description"],
        colors=json.loads(row["colors"]),
        image_url=f"/media/{row['image_file_path']}",
        price=row["price"],
        inventory=sizes,
        total_stock=sum(s.quantity for s in sizes),
    )


# ------------------------------------------------------------------ the tools

def search_products(
    query: str,
    garment_type: str | None = None,
    max_price: float | None = None,
    min_price: float | None = None,
    in_stock_only: bool = False,
    sort: str | None = None,
    limit: int = MAX_RESULTS,
) -> ProductSearchResult:
    """Search the Campus Customs catalogue.

    Every word in `query` must appear somewhere in the item (name, garment type,
    description, colors, or search tags). Use the optional filters to narrow down.

    Args:
        query: Keywords, e.g. "navy hoodie", "Davenport crewneck", "fencing". Empty = browse all.
        garment_type: Loose category filter, e.g. "hoodie", "t-shirt", "crewneck", "quarter-zip".
        max_price: Only items at or below this price (USD).
        min_price: Only items at or above this price (USD).
        in_stock_only: If true, only items with at least one size in stock.
        sort: "price_asc" (cheapest first), "price_desc" (most expensive first), or
            "name". Use "price_asc" for "cheapest / most affordable" questions.
        limit: Max products to return (1-8).
    """
    limit = max(1, min(int(limit or MAX_RESULTS), MAX_RESULTS))
    words = [w for w in query.lower().split() if w]
    with closing(_connect()) as conn:
        rows = conn.execute("SELECT * FROM catalogue ORDER BY name").fetchall()
        matches: list[sqlite3.Row] = []
        for row in rows:
            haystack = " ".join(
                [
                    row["name"],
                    row["garment_type"],
                    row["description"],
                    row["colors"],
                    row["search_tags"],
                ]
            ).lower()
            if words and not all(w in haystack for w in words):
                continue
            if garment_type and garment_type.lower() not in row["garment_type"].lower():
                continue
            if max_price is not None and row["price"] > max_price:
                continue
            if min_price is not None and row["price"] < min_price:
                continue
            matches.append(row)

        cards = [_card(conn, row) for row in matches]

    if in_stock_only:
        cards = [c for c in cards if c.total_stock > 0]

    if sort == "price_asc":
        cards.sort(key=lambda c: c.price)
    elif sort == "price_desc":
        cards.sort(key=lambda c: c.price, reverse=True)
    elif sort == "name":
        cards.sort(key=lambda c: c.name.lower())

    return ProductSearchResult(
        query=query,
        total_matches=len(cards),
        returned=min(len(cards), limit),
        products=cards[:limit],
    )


def suggest_alternatives(
    product_id: str, size: str | None = None, limit: int = 4
) -> ProductSearchResult:
    """Find in-stock items similar to `product_id` — for when it (or a requested
    size) is out of stock. Returns same-garment-type products that are in stock
    (in `size` if given), excluding the original, cheapest first.

    Args:
        product_id: The item that's unavailable (id or name).
        size: If given, only alternatives that have this size in stock.
        limit: Max alternatives (1-8).
    """
    limit = max(1, min(int(limit or 4), MAX_RESULTS))
    want = size.strip().upper() if size else None
    with closing(_connect()) as conn:
        original = _resolve(conn, product_id)
        rows = conn.execute("SELECT * FROM catalogue ORDER BY name").fetchall()
        cards = [_card(conn, row) for row in rows]

    category = (original.garment_type.lower() if original else "").split()
    key = category[-1] if category else ""  # e.g. "hoodie", "crewneck", "t-shirt"

    alts: list[ProductCard] = []
    for c in cards:
        if original and c.product_id == original.product_id:
            continue
        if key and key not in c.garment_type.lower():
            continue
        if want:
            if any(s.size.upper() == want and s.quantity > 0 for s in c.inventory):
                alts.append(c)
        elif c.total_stock > 0:
            alts.append(c)

    alts.sort(key=lambda c: c.price)
    return ProductSearchResult(
        query=f"alternatives to {product_id}" + (f" in {want}" if want else ""),
        total_matches=len(alts),
        returned=min(len(alts), limit),
        products=alts[:limit],
    )


def get_product(product_id: str) -> ProductCard | None:
    """Fetch one product by its product_id, with full per-size stock.

    Use this after search_products when the shopper asks about a specific item's
    sizes, availability, colors, or price. Returns None if the id is unknown.
    """
    with closing(_connect()) as conn:
        return _resolve(conn, product_id)


def _resolve(conn: sqlite3.Connection, product_ref: str) -> ProductCard | None:
    """Look a product up by exact id, or fall back to a unique name match so the
    agent can pass either an id or the name it showed the shopper."""
    row = conn.execute(
        "SELECT * FROM catalogue WHERE product_id = ?", (product_ref,)
    ).fetchone()
    if row is None:
        like = f"%{product_ref.strip()}%"
        hits = conn.execute(
            "SELECT * FROM catalogue WHERE name LIKE ? OR product_id LIKE ?", (like, like)
        ).fetchall()
        if len(hits) == 1:
            row = hits[0]
    return _card(conn, row) if row else None


def check_stock(product_id: str, size: str | None = None) -> StockResult:
    """Look up live price and stock for one product, straight from the database.

    Call this for any price or stock/availability question — never guess numbers.
    Pass `size` when the shopper asks about a specific size to get a direct
    in-stock / out-of-stock answer for it. `product_id` accepts the catalogue id
    (e.g. "fencing-left-chest-hoodie") or the product's name.

    Args:
        product_id: The catalogue slug or the product name.
        size: Optional size to check, one of XS, S, M, L, XL, XXL.
    """
    with closing(_connect()) as conn:
        card = _resolve(conn, product_id)

    if card is None:
        return StockResult(
            found=False,
            message=f"No product matched '{product_id}' in the catalogue.",
        )

    in_stock = [s.size for s in card.inventory if s.quantity > 0]
    out_stock = [s.size for s in card.inventory if s.quantity == 0]

    result = StockResult(
        found=True,
        product_id=card.product_id,
        name=card.name,
        price=card.price,
        sizes=card.inventory,
        total_stock=card.total_stock,
        in_stock_sizes=in_stock,
        out_of_stock_sizes=out_stock,
    )

    if size:
        want = size.strip().upper()
        match = next((s for s in card.inventory if s.size.upper() == want), None)
        result.requested_size = want
        if match is None:
            result.requested_in_stock = False
            result.requested_quantity = None
            result.message = (
                f"{card.name} isn't offered in size {want}. "
                f"Sizes in stock: {', '.join(in_stock) or 'none'}."
            )
        elif match.quantity > 0:
            result.requested_in_stock = True
            result.requested_quantity = match.quantity
            result.message = (
                f"{card.name} in size {want}: {match.quantity} in stock at "
                f"${card.price:g}."
            )
        else:
            result.requested_in_stock = False
            result.requested_quantity = 0
            result.message = (
                f"{card.name} in size {want} is OUT OF STOCK. "
                f"In stock: {', '.join(in_stock) or 'no sizes right now'}."
            )
    else:
        if card.total_stock == 0:
            result.message = f"{card.name} (${card.price:g}) is out of stock in every size."
        else:
            parts = ", ".join(f"{s.size} ({s.quantity})" for s in card.inventory if s.quantity > 0)
            result.message = f"{card.name} (${card.price:g}) — in stock: {parts}."

    return result


# ----------------------------------------------------------------- model client

def portkey_client() -> OpenAI:
    """OpenAI-compatible client pointed at the Portkey gateway.

    The key is read from PORTKEY_API_KEY (loaded from the project .env). It is
    never hard-coded, logged, or returned.
    """
    key = os.getenv("PORTKEY_API_KEY")
    if not key:
        raise RuntimeError(
            "PORTKEY_API_KEY is missing. Add it to the project-root .env "
            "(PORTKEY_API_KEY=your-key-here) before starting the backend."
        )
    return OpenAI(
        api_key=key,
        base_url=PORTKEY_BASE_URL,
        default_headers={"x-portkey-api-key": key},
    )
