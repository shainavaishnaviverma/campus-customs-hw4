"""Campus Customs API — products, auth, and the shop chatbot.

Run from the backend/ folder:
    uvicorn main:app --reload --port 8000

Serves the React front end: product catalogue + images (Problem 3), account
create/login (Problem 4), and the PydanticAI shop agent at /api/chat (Problem 5).
API docs: http://127.0.0.1:8000/docs
"""

from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Cookie, FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, Field

import auth
from agent import run_agent
from models import ChatTurn, PageContext, UserInfo

HW4_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = HW4_DIR / "data"
DB_PATH = DATA_DIR / "campus_customs.db"
PRODUCTS_DIR = DATA_DIR / "products"

# PORTKEY_API_KEY lives in the project-root .env (never committed). Load it (and
# hw4/.env if present) so the agent can reach the model.
load_dotenv(HW4_DIR / ".env")
load_dotenv(HW4_DIR.parent / ".env")

SIZE_ORDER = ["XS", "S", "M", "L", "XL", "XXL"]
SESSION_COOKIE = "cc_session"
# Development default so the seeded test account logs in through our own scheme.
TEST_USER_EMAIL = "test@campuscustoms.yale.edu"
TEST_USER_PASSWORD = "password"

app = FastAPI(title="Campus Customs API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def ensure_test_user() -> None:
    """Make the documented test login work under our current hash scheme.

    The seed DB stored the test user's hash in an older format we can't verify
    against, so we re-hash its known dev password once. Idempotent: it only
    rewrites the hash if it isn't already in our pbkdf2_sha256$<iters>$... form.
    """
    with closing(auth.connect_rw(DB_PATH)) as conn:
        row = conn.execute(
            "SELECT password_hash FROM users WHERE email = ?", (TEST_USER_EMAIL,)
        ).fetchone()
        if row is None:
            return
        parts = row["password_hash"].split("$")
        already_ours = len(parts) == 4 and parts[0] == auth.ALGORITHM
        if not already_ours:
            conn.execute(
                "UPDATE users SET password_hash = ? WHERE email = ?",
                (auth.hash_password(TEST_USER_PASSWORD), TEST_USER_EMAIL),
            )
            conn.commit()

# Images live at data/products/<file>.jpg; the DB stores "products/<file>.jpg",
# so the public URL is /media/<image_file_path>.
app.mount("/media/products", StaticFiles(directory=PRODUCTS_DIR), name="product-images")


def connect() -> sqlite3.Connection:
    if not DB_PATH.exists():
        raise RuntimeError(f"Database not found at {DB_PATH}")
    # Read-only: the storefront never writes to the catalogue.
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def product_from_row(row: sqlite3.Row) -> dict:
    return {
        "product_id": row["product_id"],
        "name": row["name"],
        "garment_type": row["garment_type"],
        "description": row["description"],
        "colors": json.loads(row["colors"]),
        "search_tags": json.loads(row["search_tags"]),
        "image_url": f"/media/{row['image_file_path']}",
        "price": row["price"],
    }


def inventory_for(conn: sqlite3.Connection, product_ids: list[str]) -> dict[str, list[dict]]:
    if not product_ids:
        return {}
    placeholders = ",".join("?" * len(product_ids))
    rows = conn.execute(
        f"SELECT product_id, size, quantity FROM inventory WHERE product_id IN ({placeholders})",
        product_ids,
    ).fetchall()
    by_product: dict[str, list[dict]] = {pid: [] for pid in product_ids}
    for r in rows:
        by_product[r["product_id"]].append({"size": r["size"], "quantity": r["quantity"]})
    for sizes in by_product.values():
        sizes.sort(key=lambda s: SIZE_ORDER.index(s["size"]) if s["size"] in SIZE_ORDER else 99)
    return by_product


def with_inventory(product: dict, sizes: list[dict]) -> dict:
    return {**product, "inventory": sizes, "total_stock": sum(s["quantity"] for s in sizes)}


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/products")
def list_products(q: str | None = None) -> list[dict]:
    sql = "SELECT * FROM catalogue"
    params: list[str] = []
    if q:
        like = f"%{q.strip()}%"
        sql += " WHERE name LIKE ? OR garment_type LIKE ? OR description LIKE ? OR search_tags LIKE ? OR colors LIKE ?"
        params = [like] * 5
    sql += " ORDER BY name"
    with closing(connect()) as conn:
        products = [product_from_row(r) for r in conn.execute(sql, params)]
        inv = inventory_for(conn, [p["product_id"] for p in products])
    return [with_inventory(p, inv[p["product_id"]]) for p in products]


@app.get("/api/products/{product_id}")
def get_product(product_id: str) -> dict:
    with closing(connect()) as conn:
        row = conn.execute("SELECT * FROM catalogue WHERE product_id = ?", (product_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Product not found")
        product = product_from_row(row)
        inv = inventory_for(conn, [product_id])
    return with_inventory(product, inv[product_id])


# ---- Authentication ----


class SignupRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=200)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class PublicUser(BaseModel):
    """What we expose about a user. Never includes the password hash."""

    id: int
    first_name: str | None
    last_name: str | None
    email: str


def public_user(row: sqlite3.Row) -> PublicUser:
    return PublicUser(
        id=row["id"],
        first_name=row["first_name"],
        last_name=row["last_name"],
        email=row["email"],
    )


def set_session_cookie(response: Response, user_id: int) -> None:
    response.set_cookie(
        SESSION_COOKIE,
        auth.issue_session(user_id),
        max_age=auth.SESSION_TTL_SECONDS,
        httponly=True,  # not readable from JS, so XSS can't steal it
        samesite="lax",
    )


@app.post("/api/auth/signup", response_model=PublicUser, status_code=201)
def signup(req: SignupRequest, response: Response) -> PublicUser:
    email = req.email.strip().lower()
    full_name = f"{req.first_name.strip()} {req.last_name.strip()}"
    password_hash = auth.hash_password(req.password)
    with closing(auth.connect_rw(DB_PATH)) as conn:
        exists = conn.execute("SELECT 1 FROM users WHERE email = ?", (email,)).fetchone()
        if exists:
            raise HTTPException(status_code=409, detail="An account with that email already exists.")
        cur = conn.execute(
            "INSERT INTO users (name, email, password_hash, first_name, last_name) "
            "VALUES (?, ?, ?, ?, ?)",
            (full_name, email, password_hash, req.first_name.strip(), req.last_name.strip()),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM users WHERE id = ?", (cur.lastrowid,)).fetchone()
    set_session_cookie(response, row["id"])
    return public_user(row)


@app.post("/api/auth/login", response_model=PublicUser)
def login(req: LoginRequest, response: Response) -> PublicUser:
    email = req.email.strip().lower()
    with closing(auth.connect_rw(DB_PATH)) as conn:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    # Same error whether the email is unknown or the password is wrong, so we
    # don't reveal which emails have accounts.
    if row is None or not auth.verify_password(req.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    set_session_cookie(response, row["id"])
    return public_user(row)


@app.post("/api/auth/logout", status_code=204)
def logout(response: Response) -> None:
    response.delete_cookie(SESSION_COOKIE)


@app.get("/api/auth/me", response_model=PublicUser)
def me(cc_session: str | None = Cookie(default=None)) -> PublicUser:
    user_id = auth.read_session(cc_session)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Not logged in.")
    with closing(auth.connect_rw(DB_PATH)) as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=401, detail="Not logged in.")
    return public_user(row)


class PageContextIn(BaseModel):
    """What the shopper is looking at, sent by the front end with each message."""

    product_id: str | None = None
    product_name: str | None = None


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    page: PageContextIn | None = None


class ChatResponse(BaseModel):
    reply: str
    products: list[dict] = []
    tools_used: list[str] = []


class ChatTurnOut(BaseModel):
    role: str
    content: str
    products: list[dict] = []


def _load_user_info(user_id: int) -> UserInfo | None:
    with closing(auth.connect_rw(DB_PATH)) as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if row is None:
        return None
    return UserInfo(
        id=row["id"], name=row["name"], first_name=row["first_name"], email=row["email"]
    )


def _load_history(user_id: int) -> list[ChatTurn]:
    with closing(auth.connect_rw(DB_PATH)) as conn:
        rows = conn.execute(
            "SELECT role, content, products_json FROM chat_messages "
            "WHERE user_id = ? ORDER BY id",
            (user_id,),
        ).fetchall()
    turns: list[ChatTurn] = []
    for r in rows:
        products = json.loads(r["products_json"]) if r["products_json"] else []
        turns.append(ChatTurn(role=r["role"], content=r["content"], products=products))
    return turns


def _save_turn(
    user_id: int, role: str, content: str, products: list[dict] | None = None
) -> None:
    products_json = json.dumps(products) if products else None
    with closing(auth.connect_rw(DB_PATH)) as conn:
        conn.execute(
            "INSERT INTO chat_messages (user_id, role, content, products_json) "
            "VALUES (?, ?, ?, ?)",
            (user_id, role, content, products_json),
        )
        conn.commit()


@app.get("/api/chat/history", response_model=list[ChatTurnOut])
def chat_history(cc_session: str | None = Cookie(default=None)) -> list[ChatTurnOut]:
    """Return the signed-in shopper's saved conversation (empty for guests)."""
    user_id = auth.read_session(cc_session)
    if user_id is None:
        return []
    return [
        ChatTurnOut(role=t.role, content=t.content, products=[p.model_dump() for p in t.products])
        for t in _load_history(user_id)
    ]


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest, cc_session: str | None = Cookie(default=None)) -> ChatResponse:
    """Send the shopper's message to the PydanticAI agent and return its reply
    plus any product cards the agent surfaced.

    For signed-in shoppers we pass who they are + their prior history to the agent
    (memory) and persist this turn. Guests chat too, but nothing is saved.
    """
    message = req.message.strip()
    user_id = auth.read_session(cc_session)

    user = _load_user_info(user_id) if user_id else None
    history = _load_history(user_id) if user_id else []
    page = PageContext(**req.page.model_dump()) if req.page else None

    result = run_agent(message, user=user, page=page, history=history)
    reply = result.get("reply", "")
    products = list(result.get("products") or [])

    if user_id:
        _save_turn(user_id, "user", message)
        _save_turn(user_id, "assistant", reply, products)

    return ChatResponse(
        reply=reply,
        products=products,
        tools_used=list(result.get("tools_used") or []),
    )
