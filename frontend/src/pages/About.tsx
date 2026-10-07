import { Link } from 'react-router-dom'

export default function About() {
  return (
    <article className="prose">
      <p className="eyebrow">About us</p>
      <h1>We sell sweatshirts. We're good at it.</h1>

      <div className="about-hero">
        <img src="/art/cage-2.jpg" alt="Picolas Page, Campus Customs spokesman" />
        <img className="bulldog-float" src="/art/bulldog-2.svg" alt="Yale bulldog in a sweater" />
      </div>

      <p>
        Campus Customs runs Yale Bulldog Blue out of 57 Broadway in New Haven. Folks ask what we do,
        and I tell them the truth: we put the Yale name on clothes people actually want to wear,
        then we sell them at a fair price. It isn't rocket science. If it were, we'd have a lot more
        engineers in here asking for discounts.
      </p>

      <p>
        Here's our whole business plan, and you can have it for free: sell good gear, treat people
        right, and don't insult their intelligence. That's it. Some folks dress that up with fancy
        words and a slide deck. We just hang it on a rack. A fair deal isn't complicated — it's just
        rare, like an honest man at an auction.
      </p>

      <h2>What we stand for</h2>
      <ul>
        <li>
          <strong>Officially licensed, every time.</strong> If it's on our shelf, Yale signed off
          on it. I trust that paperwork more than most paperwork I've read.
        </li>
        <li>
          <strong>Good brands, honest house lines.</strong> We carry names like Champion and Brooks
          Brothers next to our own designs. Both will outlast your first-year meal plan.
        </li>
        <li>
          <strong>Something for every Bulldog.</strong> Residential colleges, professional schools,
          varsity sports, class years, and the whole family tree. If your aunt wants a "Yale Aunt"
          crewneck, I'm not going to stand in her way. Nobody should.
        </li>
        <li>
          <strong>Custom when you need it.</strong> Reunions, teams, clubs. Tell us what you're
          after and we'll do our dead-level best to make it happen.
        </li>
      </ul>

      <h2>Why it matters</h2>
      <p>
        Wearing your school's colors is a small thing that says a big thing: you belong somewhere,
        and you're proud of it. That's worth more than a fancy speech, and it costs a lot less. You
        can't buy school spirit, but you can buy the sweatshirt — and around here that's close enough.
      </p>
      <p>
        We'd rather sell you one hoodie you love than three you'll leave in the closet. Quality over
        quantity: a man with one good sweatshirt knows he's warm; a man with ten is just doing
        laundry.
      </p>

      <p>
        Come see us on Broadway, or <Link to="/products">browse the shop online</Link>. Either way,
        we're glad you're here. And if you can't decide, ask the chat assistant in the corner. It's
        polite, it's patient, and it doesn't run for reelection.
      </p>
    </article>
  )
}
