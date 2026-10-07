# Campus Customs — Usability Improvements (Problem 9)

Four improvements on top of the working shop: two front-end, two agent/backend.
Each is live in the running app.

## Front-end

### FE1 — Filter & sort bar on the Products page

**What was added:** a control bar above the product grid with (a) garment-category
filter chips (All, Hoodies, Crewnecks, T-Shirts, Quarter-Zips, Jackets, Fleece),
(b) a sort dropdown (Featured, Price: Low→High, Price: High→Low, Name A–Z), and
(c) an "In stock only" toggle. These compose with the existing text search and
apply to the full catalogue view.

**Why it helps:** the catalogue has 102 items with inconsistent garment-type
labels. Letting shoppers narrow to a category, hide sold-out items, and sort by
price turns a long scroll into a quick find — the single biggest driver of
"did I find what I wanted?" on a store. Price sorting in particular helps
budget-minded students, which should lift conversion for the business.

### FE2 — Starter question chips in the chat

**What was added:** when the chat is fresh (no messages sent yet), the panel shows
a few one-tap suggestion chips ("What hoodies do you have?", "Crewnecks under
$60", "What's in stock in size M?"). Tapping one sends it immediately.

**Why it helps:** a blank chat box is intimidating and many shoppers don't know
the assistant can search the catalogue. The chips advertise what it can do and
remove the friction of typing, so more shoppers actually engage the assistant —
and engaged shoppers see more relevant products.

## Agent / backend

### BE1 — In-stock alternatives when something is sold out

**What was added:** a `suggest_alternatives(product_id, size?)` tool that returns a
few **in-stock** items similar to the one asked about (same garment type, same
requested size when given, excluding the original). The prompt now tells the
agent: whenever an item or a requested size is out of stock, call this and offer
real alternatives.

**Why it helps:** "out of stock" is a dead end that loses a sale. Turning it into
"that size is gone, but here are three similar hoodies in M you can buy right now"
keeps the shopper moving toward a purchase — better for the shopper and directly
protective of revenue for the business. Every suggestion is a real, in-stock DB
row, so it never sends someone toward something they can't buy.

### BE2 — Price-aware search (sorting + "cheapest" support)

**What was added:** `search_products` gained a `sort` option
(`price_asc`, `price_desc`, `name`) plus an optional `min_price`. The prompt tells
the agent to use `sort="price_asc"` for "cheapest / most affordable" questions and
the price filters for budget ranges.

**Why it helps:** budget questions ("what's your cheapest crewneck?", "hoodies
between $40 and $70") are common and were previously answered by eyeballing an
unsorted list. Now the agent returns correctly ordered, correctly filtered results
straight from the database, so price answers are exact and the shopper sees the
most relevant-to-budget items first.
