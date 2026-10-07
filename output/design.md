# Campus Customs — Design Pass (Problem 10)

Goal: make the site feel like a real Yale-blue storefront so shoppers stay,
browse, and buy. What changed and why:

## Color & brand
- **Yale blue + white base** with a **rainbow pastel accent** system (pink, peach,
  yellow, mint, blue, lavender) used on the nav underline, card captions, section
  dividers, and soft background glows.
- *Why:* the blue says "official Yale"; the pastels feel modern and fun, so the
  shop reads as trustworthy **and** approachable — not a stuffy institutional page.

## Fonts & hierarchy
- Display headings in **Anton** (bold collegiate), friendly labels/brand in
  **Fredoka**, body in **Inter**.
- *Why:* a clear type hierarchy pulls the eye to the pitch and product names first,
  so shoppers grasp "what is this and what can I buy" in a glance.

## Motion
- Hero art **floats**, bulldogs gently **bob**, sections **fade up** on load,
  buttons press with a **3D push**, cards **lift and tilt** on hover.
- *Why:* subtle life makes the store feel polished and responsive to touch, which
  builds confidence and keeps people scrolling. (All motion is light and
  CSS-only, so it never gets in the way.)

## 3D look
- Layered drop shadows and soft gradients on cards, buttons, hero, and chat; the
  product grid uses perspective so cards **tilt toward you** on hover.
- *Why:* depth makes products feel tangible — closer to holding a real sweatshirt,
  which helps shoppers commit.

## Product presentation
- Cards get a soft blue-tinted image backdrop, rounded corners, a "Sold out"
  badge, and a 3D hover lift. The Products page keeps the Problem 9 filter/sort bar.
- *Why:* consistent, premium-feeling cards make browsing 102 items pleasant and
  scannable, which drives more clicks into product pages.

## Mascot & spokesman imagery
- **Three unique bulldog illustrations** appear across the site (home pitch cards,
  the About page, and as the chat avatar + chat button), plus **three unique
  "celebrity spokesman" portraits** — each modeling a different men's item (hoodie,
  Harvard-Yale tee, quarter-zip) in a hero spot and an "As seen on our spokesman"
  gallery.
- *Why:* personality and a recurring mascot make the brand memorable and shareable;
  showing items "worn" helps shoppers picture themselves in the gear.
- *Note:* these are **original caricature illustrations** standing in for licensed
  photography. We can't use real photos of a specific celebrity (likeness/rights),
  so the art evokes the over-the-top-spokesman vibe and is drop-in replaceable with
  licensed photos later (just swap the files in `public/art/`).

## Chat feel
- The assistant gets a bulldog avatar, a titled "Yale gear concierge" header, a
  pastel-gradient message style, and a bobbing bulldog launcher button.
- *Why:* a friendly, branded assistant invites shoppers to ask for help, and more
  assisted shoppers find the right item faster.
