"""Campus Customs shop agent (PydanticAI, OpenAI Responses API via Portkey).

The system prompt lives in prompts/prompt.md and is loaded at build time. The
model slug comes from MODEL_NAME (default gpt-5.6-luna, routed through OpenAI by
Portkey per the project's AGENTS.md).
"""

from __future__ import annotations

import json
import os
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext
from pydantic_ai.messages import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    TextPart,
    ToolCallPart,
    ToolReturnPart,
    UserPromptPart,
)
from pydantic_ai.models.openai import OpenAIResponsesModel
from pydantic_ai.providers.openai import OpenAIProvider

import tools
from models import (
    AgentResult,
    AuditEntry,
    ChatTurn,
    PageContext,
    ProductCard,
    ProductSearchResult,
    StockResult,
    ToolStep,
    UserInfo,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent  # hw4/
PROMPT_PATH = HERE / "prompts" / "prompt.md"
AUDIT_PATH = ROOT / "output" / "audit_trail.json"

load_dotenv(ROOT / ".env")
load_dotenv(ROOT.parent / ".env")  # project-root .env holds PORTKEY_API_KEY

MODEL_NAME = os.getenv("MODEL_NAME", "gpt-5.6-luna")

MAX_CARDS = 8  # most product cards we hand back to the UI for one reply
MAX_HISTORY_MESSAGES = 20  # prior messages replayed to the agent for memory

_audit_lock = threading.Lock()


@dataclass
class ChatDeps:
    """Per-conversation context passed into the agent run.

    `user` is the signed-in shopper (None for guests); `page` is what they're
    currently viewing on the site. Both are surfaced to the model through the
    dynamic instructions below, so it knows who it's talking to and what "this
    one" refers to.
    """

    user: UserInfo | None = None
    page: PageContext | None = None


# ------------------------------------------------------------- tool wrappers

def _search_products(
    query: str,
    garment_type: str | None = None,
    max_price: float | None = None,
    min_price: float | None = None,
    in_stock_only: bool = False,
    sort: str | None = None,
    limit: int = 8,
) -> ProductSearchResult:
    """Search the Campus Customs catalogue by keyword, with optional filters.

    Args:
        query: Keywords; every word must match (name, type, description, colors, tags). Empty = browse.
        garment_type: Loose category, e.g. "hoodie", "t-shirt", "crewneck", "quarter-zip".
        max_price: Only items at or below this price (USD).
        min_price: Only items at or above this price (USD).
        in_stock_only: If true, only items with at least one size in stock.
        sort: "price_asc" (cheapest first), "price_desc", or "name". Use "price_asc"
            for "cheapest / most affordable" questions.
        limit: Max products to return (1-8).
    """
    return tools.search_products(
        query=query,
        garment_type=garment_type,
        max_price=max_price,
        min_price=min_price,
        in_stock_only=in_stock_only,
        sort=sort,
        limit=limit,
    )


def _suggest_alternatives(
    product_id: str, size: str | None = None, limit: int = 4
) -> ProductSearchResult:
    """In-stock items similar to one that's unavailable. Call this when an item or
    a requested size is out of stock, then offer the results.

    Args:
        product_id: The unavailable item (id or name).
        size: If given, only alternatives with this size in stock.
        limit: Max alternatives (1-8).
    """
    return tools.suggest_alternatives(product_id=product_id, size=size, limit=limit)


def _get_product(product_id: str) -> ProductCard | None:
    """Look up one product by product_id, with full per-size stock. None if unknown.

    Args:
        product_id: The catalogue slug, e.g. "basic-hoodie-big-yale".
    """
    return tools.get_product(product_id=product_id)


def _check_stock(product_id: str, size: str | None = None) -> StockResult:
    """Live price and stock for one product from the database. Call this for ANY
    price or stock question; never guess numbers. Pass `size` for a direct
    in-stock / out-of-stock answer on that size.

    Args:
        product_id: The catalogue slug or the product name.
        size: Optional size to check (XS, S, M, L, XL, XXL).
    """
    return tools.check_stock(product_id=product_id, size=size)


def _async_client(sync_client):
    from openai import AsyncOpenAI

    return AsyncOpenAI(
        api_key=sync_client.api_key,
        base_url=str(sync_client.base_url),
        default_headers={"x-portkey-api-key": sync_client.api_key},
    )


@lru_cache(maxsize=1)
def build_agent() -> Agent:
    client = tools.portkey_client()  # clear error if PORTKEY_API_KEY is missing
    model = OpenAIResponsesModel(
        MODEL_NAME, provider=OpenAIProvider(openai_client=_async_client(client))
    )
    agent = Agent(
        model,
        deps_type=ChatDeps,
        instructions=PROMPT_PATH.read_text(encoding="utf-8"),
        retries=2,
    )

    # Dynamic instructions: who we're chatting with + what they're looking at.
    @agent.instructions
    def _who_and_where(ctx: RunContext[ChatDeps]) -> str:
        lines: list[str] = []
        user = ctx.deps.user
        if user:
            who = user.first_name or user.name
            lines.append(
                f"You are chatting with a signed-in shopper: {who} (email: {user.email}). "
                "You may greet them by first name. Only ever discuss THIS shopper's own "
                "information — never another customer's."
            )
        else:
            lines.append("You are chatting with a guest (not signed in).")

        page = ctx.deps.page
        if page and page.product_id:
            name = page.product_name or page.product_id
            lines.append(
                f"The shopper is currently viewing this product page: {name} "
                f"(product_id: {page.product_id}). If they say 'this', 'this one', "
                f"'it', or ask e.g. 'do you have this in pink?', they mean that item — "
                f"call your tools with product_id {page.product_id}."
            )
        return "\n".join(lines)

    agent.tool_plain(name="search_products")(_search_products)
    agent.tool_plain(name="get_product")(_get_product)
    agent.tool_plain(name="check_stock")(_check_stock)
    agent.tool_plain(name="suggest_alternatives")(_suggest_alternatives)
    return agent


def _to_message_history(turns: list[ChatTurn]) -> list[ModelMessage]:
    """Rebuild prior turns as pydantic-ai messages so the agent remembers the
    conversation. Only role + text are replayed (product cards aren't needed for
    memory). Capped to the most recent messages."""
    recent = turns[-MAX_HISTORY_MESSAGES:]
    history: list[ModelMessage] = []
    for turn in recent:
        if not turn.content:
            continue
        if turn.role == "user":
            history.append(ModelRequest(parts=[UserPromptPart(content=turn.content)]))
        elif turn.role == "assistant":
            history.append(ModelResponse(parts=[TextPart(content=turn.content)]))
    return history


# --------------------------------------------------------------- run + collect

def _collect(messages: list) -> tuple[list[ProductCard], list[str]]:
    """Pull the product cards the tools surfaced and the tool names used."""
    products: list[ProductCard] = []
    seen: set[str] = set()
    tools_used: list[str] = []

    def add(card: ProductCard) -> None:
        if card.product_id not in seen:
            seen.add(card.product_id)
            products.append(card)

    for msg in messages:
        if isinstance(msg, ModelResponse):
            for part in msg.parts:
                if isinstance(part, ToolCallPart) and part.tool_name not in tools_used:
                    tools_used.append(part.tool_name)
        else:
            for part in getattr(msg, "parts", []):
                if isinstance(part, ToolReturnPart):
                    content = part.content
                    if isinstance(content, ProductSearchResult):
                        for card in content.products:
                            add(card)
                    elif isinstance(content, ProductCard):
                        add(content)
    return products[:MAX_CARDS], tools_used


# ---------------------------------------------------------------- audit trail

def _short(content: object, limit: int = 240) -> str:
    """A compact, readable summary of a tool's return for the audit log."""
    if isinstance(content, ProductSearchResult):
        names = ", ".join(c.name for c in content.products[:4])
        return f"{content.total_matches} match(es), returned {content.returned}: {names}"[:limit]
    if isinstance(content, StockResult):
        return content.message[:limit]
    if isinstance(content, ProductCard):
        return f"{content.name} (${content.price:g}), total_stock={content.total_stock}"[:limit]
    text = content if isinstance(content, str) else json.dumps(content, default=str)
    return text[:limit]


def _trace(messages: list, entry: AuditEntry) -> None:
    """Fill tool steps, tools_used, and stop_reason from the run's messages."""
    steps: dict[str, ToolStep] = {}
    for msg in messages:
        if isinstance(msg, ModelResponse):
            for part in msg.parts:
                if isinstance(part, ToolCallPart):
                    steps[part.tool_call_id] = ToolStep(
                        tool=part.tool_name, args=part.args_as_dict()
                    )
                    if part.tool_name not in entry.tools_used:
                        entry.tools_used.append(part.tool_name)
            if getattr(msg, "finish_reason", None):
                entry.stop_reason = str(msg.finish_reason)
        else:
            for part in getattr(msg, "parts", []):
                if isinstance(part, ToolReturnPart) and part.tool_call_id in steps:
                    steps[part.tool_call_id].result = _short(part.content)
    entry.steps = list(steps.values())


def _append_audit(entry: AuditEntry) -> None:
    """Append one entry to output/audit_trail.json. Append-only: never wipes
    earlier rows. If the file is somehow unreadable, the new entry is parked in a
    sidecar recovery log instead of overwriting existing history."""
    with _audit_lock:
        AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
        rows: list = []
        if AUDIT_PATH.exists() and AUDIT_PATH.read_text(encoding="utf-8").strip():
            try:
                rows = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
                if not isinstance(rows, list):
                    rows = [rows]
            except json.JSONDecodeError:
                with (AUDIT_PATH.parent / "audit_trail.recovery.jsonl").open(
                    "a", encoding="utf-8"
                ) as f:
                    f.write(entry.model_dump_json() + "\n")
                return
        rows.append(entry.model_dump())
        AUDIT_PATH.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")


# ------------------------------------------------------------------ entrypoint

def run_agent(
    message: str,
    user: UserInfo | None = None,
    page: PageContext | None = None,
    history: list[ChatTurn] | None = None,
) -> dict:
    deps = ChatDeps(user=user, page=page)
    entry = AuditEntry(
        time=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        user_message=message,
        model=MODEL_NAME,
        user_id=user.id if user else None,
    )
    try:
        result = build_agent().run_sync(
            message, deps=deps, message_history=_to_message_history(history or [])
        )
        new_messages = result.new_messages()
        products, tools_used = _collect(new_messages)
        _trace(new_messages, entry)
        entry.reply = str(result.output)
        if entry.stop_reason in ("", "stop"):
            entry.stop_reason = "final answer (model stopped calling tools)"
        out = AgentResult(
            reply=entry.reply, products=products, tools_used=tools_used
        ).model_dump()
    except Exception as exc:  # surface a readable message instead of a 500
        entry.error = f"{type(exc).__name__}: {exc}"
        entry.stop_reason = "error"
        entry.reply = (
            "Sorry — our shop assistant tripped over its own leash just now "
            f"({type(exc).__name__}). Please try again in a moment."
        )
        out = AgentResult(reply=entry.reply).model_dump()
    _append_audit(entry)
    return out
