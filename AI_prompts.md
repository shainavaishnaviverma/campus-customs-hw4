# AI Prompts — October 7, 2026

> Log of the prompts I type while working on HW 4 today.

## Log instructions

### Prompt

In AI_prompts.md, ensure there is one section for each problem, and that they are listed numerically. Each section has to include:

* The problem number and title
* At least one prompt you typed
* Any significant followup prompts

## Problem 1: Vibe coder prompts

### Prompt 1

We are working on HW 4 today. Create AI_prompts.md and keep it updated with a log of my prompts throughout the session.

## Problem 2: Analyze the database

### Prompt 1

Problem 2: Analyze the database

Review campus_customs.db inside the data folder in HW4 folder. Start the file output/harness.md then write down each table and its fields, and one short line on why each field matters for the shop or the chatbot. We will keep adding to this harness file in later problems (models, tools, safety, specs).

## Problem 3: Build the Campus Customs website

### Prompt 1

Problem 3: Build the Campus Customs website

Scaffold a React + Vite + TypeScript front end for Campus Customs. Put a nav bar at the top that links to the main pages:

* Home
* Products
* About Us
* Log in
* Create account

Pull Campus Customs-style wording from yalebulldogblue.com for Home and About Us, but write these pages in senator john kennedy's voice i.e. witty and quippy (do not copy the original site text).

On the Products page, show product images from the catalogue (use the image paths in the database) with basic product info (name, price, short description).

Make each product open a single-item page (large image on one side, full product text on the other - description, price, sizes/stock when you have them). Clicking a card on Products should take the shopper there.

Add a chat interface in the bottom right of the site (a floating chat panel is fine). It does not need to talk to an agent yet - a stub that will call our backend later is enough for this problem.

We will need a small API soon to read the database. It's ok to start a simple FastAPl app in backend/main.py just to serve products and images, then grow it into the agent backend in Problem 5.

### Prompt 2

How do I let macOS allow it to read?

### Prompt 3

Move the AI Foundations folder back to its old location of FA26 1

### Prompt 4

Oh that's also in Documents - will I run into the same issue? If so, move to a suitable location and share the path here.

## Problem 4: Create account and login

### Prompt 1

Problem 4: Create account and login

Ok now build a normal create-account / login flow.

* Create account: first name, last name, email, password (confirm password is a nice touch
* Log in: email and password

New accounts should go into the users table. Ensure we store passwords securely so AI or human hackers can't access them.

## Problem 5: PydanticAI agent backend

### Prompt 1

Problem 5: PydanticAI agent backend

Ok now build the shop chatbot as a PydanticAI agent behind FastAPI, plugged into our front-end chat widget. Put the API app in backend/main.py - that is the file we run with Uvicorn.

Keep the agent as these four files next to it:

* backend/prompts/prompt.md — system prompt (grow this same file later)
* backend/agent.py — agent entry / wiring
* backend/tools.py — tools the agent can call
* backend/models.py — Pydantic / PydanticAI structured types

In main.py, expose a chat route so a message from the website returns a reply from the agent (and whatever else we need for products/auth). Let me know if you need my API key, and how to share that securely.

Put Campus Customs voice and safety basics into prompts/prompt.md (we will expand tools and safety later). Start or update types in models.py for chat replies / product cards as needed.

Make sure you note how the front end talks to FastAPI and how the agent is loaded (prompt file + model) in output/harness.md.

Ensure the backend runs from the backend/ folder like this: uvicorn main:app --reload --port 8000

## Problem 6: Tools: product info and stock

### Prompt 1

Problem 6: Tools: product info and stock

I want you to create/use tools that look up real information from campus_customs.db:

* Product description
* Price
* How many are in stock (by size when the customer asks)

You MUST use the database — DO NOT invent prices or quantities. If a size is out of stock, say so clearly.

Expand prompts/prompt.md and note that you should call these tools for price and stock questions. Add or update return types in models.py
In output/harness.md, list each tool and explain which model fields you chose for lookup results and why.

## Problem 7: Chat search that updates the page

### Prompt 1

Problem 7: Chat search that updates the page

I want to add another feature. When a customer asks about a type of item - for example "what hoodies do you have?" — you should search the catalogue and the website should dynamically show those matching items as product cards (image, name, price, short info). After the dynamic product cards are loaded by this new feature, ensure the same single-item page behavior we built in Problem 3 still works: each product card - including the ones the chat just put on the page — should still open that detail view (large image + full info) when clicked.

Update prompts/prompt.md and output/harness.md so it is clear how search results reach the page.

## Problem 8: Customer memory

### Prompt 1

Problem 8: Customer memory

When a shopper is logged in, save their chat history in the database in an appropriate table and reload it when they return. You should know who is chatting (name, email) - put that in agent deps (or an equivalent clear pattern) and/or tools the agent can call.

Also pass enough page context that if someone is on a product page and asks "do you have this in pink?", you should know which item they mean. Put code into the agent context. Guests can still chat, but history only needs to persist for logged-in users.

Document in output/harness.md: how user chat history is stored, what customer fields you see, and how page context is passed.

## Problem 9: Usability improvements

### Prompt 1

Problem 9: Usability improvements

Now that the core shop works, I want to improve it. Choose and implement:

* 2 front-end usability improvements
* 2 agent / backend usability improvements

Write output/usability.md before or as we build. For each of the improvements, say:

* What was added
* Why it helps a Campus Customs shopper or the business

Then make sure all improvements actually show up in the running app.

## Problem 10: Style the website

### Prompt 1

Problem 10: Style the website

I want to add creative design so the site feels like a real Campus Customs storefront - fonts, color, hierarchy, motion, product presentation, chat feel.

Make it yale blue and white with some rainbow pastel accents. Include photos of nicolas cage wearing some men's items (multiple unique photos, not just one copy pasted everywhere). Give it a 3d look. Add some bulldog photos as well everywhere.

Write what we changed and why it should help customers stick around and buy in output/design.md. Keep it concrete and short.

### Note

During Problem 10, OneDrive removed files from the working tree (frontend src/pages, src/components, node_modules, backend .venv). Recovered by recreating the source files and reinstalling dependencies; no prompts were lost.

## Problem 11: Site testing (app check)

### Prompt 1

Problem 11: Site testing (app check)

Now test the live site and document it in output/app_check.html (a page we can double-click open). Include clear screenshots and short captions for:

1. Chat checking the inventory level of an item (honest stock/price from the DB)
2. The dynamic search-result cards appearing after a category question (e.g. hoodies)
3. One of the usability features we added in Problem 9

Ensure the HTML is easy to grade: heading for each check, screenshot, one or two sentences on what the screenshot proves. Put the screenshot image files in output/app_check_images/ and link them from app_check.html with relative paths (for example app_check_images/inventory.png).

## Problem 12: Audit trail, safety, finish harness

### Prompt 1

Problem 12: Audit trail, safety, finish harness

Keep an append-only output/audit_trail.json of agent-loop activity (time, tool name, short args/result, stop reason). Do not wipe it between runs.
Put the following safety prompts in prompts/prompt.md - also add on any others you think may be useful.

* Customers should only see their own account and order data, NOT anyone else's.
* The bot MUST ask customers to confirm before taking action e.g. placing an order.
* Do NOT edit orders without customer authorization.
* Do NOT access any customer data they have not authorized.

Finish output/harness.md so it is clear how the system works.

* Model fields in models py and why you chose them
* Tools and abilities
* Safety rules
* Specs (loop limits, result caps, models, how to run front + back)

## Problem 13: Push to GitHub and submit the URL

### Prompt 1

Yes - put today's code in hw4 and push it to a public GitHub repository. Display the repo URL. Do not put my real .env, campus_customs.db, or product images in the GitHub repo. Use .gitignore. Include .env.example with placeholders only.
