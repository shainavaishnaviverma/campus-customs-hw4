"""Pydantic / PydanticAI structured types shared by the agent, tools, and API.

Problem 5 scope: product cards + chat reply. These grow as tools and safety
features are added in later problems.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class SizeStock(BaseModel):
    size: str
    quantity: int


class ProductCard(BaseModel):
    """One catalogue item with live stock, as shown on the site and in chat."""

    product_id: str
    name: str
    garment_type: str
    description: str
    colors: list[str] = Field(default_factory=list)
    image_url: str
    price: float
    inventory: list[SizeStock] = Field(default_factory=list)
    total_stock: int = 0

    @property
    def in_stock_sizes(self) -> list[str]:
        return [s.size for s in self.inventory if s.quantity > 0]


class ProductSearchResult(BaseModel):
    """Return type for the search_products tool."""

    query: str
    total_matches: int
    returned: int
    products: list[ProductCard] = Field(default_factory=list)


class StockResult(BaseModel):
    """Return type for the check_stock tool — live price and per-size stock for
    one product, straight from the database. The agent must quote these numbers
    exactly and never invent them."""

    found: bool
    product_id: str = ""
    name: str = ""
    price: float = 0.0
    sizes: list[SizeStock] = Field(default_factory=list)
    total_stock: int = 0
    in_stock_sizes: list[str] = Field(default_factory=list)
    out_of_stock_sizes: list[str] = Field(default_factory=list)
    # Set only when the shopper asked about a specific size:
    requested_size: str | None = None
    requested_quantity: int | None = None
    requested_in_stock: bool | None = None
    # Plain-language summary the agent can lean on (it still answers in voice):
    message: str = ""


class UserInfo(BaseModel):
    """The signed-in shopper the agent is chatting with (None for guests)."""

    id: int
    name: str
    first_name: str | None = None
    email: str


class PageContext(BaseModel):
    """What the shopper is looking at, so 'this one' / 'do you have this in pink?'
    resolves to the right item. Sent by the front end with each chat message."""

    product_id: str | None = None
    product_name: str | None = None


class ChatTurn(BaseModel):
    """One stored message, for reloading a returning shopper's conversation."""

    role: str  # "user" or "assistant"
    content: str
    products: list[ProductCard] = Field(default_factory=list)


class AgentResult(BaseModel):
    """What run_agent hands back to the API layer."""

    reply: str
    products: list[ProductCard] = Field(default_factory=list)
    tools_used: list[str] = Field(default_factory=list)


class ToolStep(BaseModel):
    """One tool call made during an agent run, for the audit trail."""

    tool: str
    args: dict = Field(default_factory=dict)
    result: str = ""  # short summary of what the tool returned


class AuditEntry(BaseModel):
    """One row of output/audit_trail.json — a record of a single agent run."""

    time: str
    user_message: str
    model: str
    user_id: int | None = None  # which shopper (None = guest); no PII beyond id
    steps: list[ToolStep] = Field(default_factory=list)
    tools_used: list[str] = Field(default_factory=list)
    reply: str = ""
    stop_reason: str = ""
    error: str | None = None
