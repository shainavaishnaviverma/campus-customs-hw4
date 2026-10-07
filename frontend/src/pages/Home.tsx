import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { fetchProducts } from '../api'
import ProductCard from '../components/ProductCard'
import type { Product } from '../types'

const FEATURED_IDS = [
  'basic-hoodie-big-yale',
  'baseball-left-chest-crewneck',
  '2025-yale-vs-harvard-t-shirt',
  'district-vit-hoodie-vintage-bulldog',
]

const pitches = [
  {
    title: 'Officially licensed',
    text: "Every stitch is the real deal. I don't sell knockoffs. I've got enough fake things to deal with at my day job.",
    dog: '/art/bulldog-1.svg',
  },
  {
    title: 'Every Bulldog in the family',
    text: "Students, alumni, moms, dads, grandpas, and that one cousin who claims he almost got in. We've got a shirt for him too.",
    dog: '/art/bulldog-2.svg',
  },
  {
    title: 'Colleges, schools, and sports',
    text: 'Residential colleges, grad schools, and varsity teams from fencing to field hockey. Pick a side. Wear it proud.',
    dog: '/art/bulldog-3.svg',
  },
]

// Original caricature art of our (very dramatic) celebrity spokesman, each in a
// different men's item. Placeholders for licensed photography.
const spokesmen = [
  { img: '/art/spokesman-1.svg', caption: 'The Big YALE Hoodie — hood up, standards higher' },
  { img: '/art/spokesman-2.svg', caption: 'Harvard-Yale tee — worn with menace and joy' },
  { img: '/art/spokesman-3.svg', caption: 'The quarter-zip — for the dramatic alumnus' },
]

export default function Home() {
  const [featured, setFeatured] = useState<Product[]>([])

  useEffect(() => {
    fetchProducts()
      .then((all) => setFeatured(all.filter((p) => FEATURED_IDS.includes(p.product_id))))
      .catch(() => setFeatured([]))
  }, [])

  return (
    <>
      <section className="hero">
        <div className="hero-copy">
          <p className="eyebrow">Yale Bulldog Blue · by Campus Customs</p>
          <h1>Bulldog blue, made simple.</h1>
          <p className="lede">
            Look, I'm not saying a Yale hoodie will make you smarter. I'm saying nobody's ever looked
            dumber wearing one. We're right on Broadway in New Haven, and we sell officially licensed
            Yale gear that's comfortable, durable, and bluer than a cold day in Connecticut.
          </p>
          <div className="hero-actions">
            <Link to="/products" className="btn">
              Shop the goods
            </Link>
            <Link to="/about" className="btn btn-ghost">
              Who are these people?
            </Link>
          </div>
        </div>
        <div className="hero-art">
          <img src="/art/spokesman-1.svg" alt="Campus Customs spokesman in a navy Yale hoodie" />
        </div>
      </section>

      <section className="pitches">
        {pitches.map((p) => (
          <article key={p.title} className="pitch">
            <h3>{p.title}</h3>
            <p>{p.text}</p>
            <img className="pitch-dog" src={p.dog} alt="" aria-hidden="true" />
          </article>
        ))}
      </section>

      <section>
        <div className="section-head">
          <h2>As seen on our spokesman</h2>
        </div>
        <p className="muted">
          Our wildly committed (and entirely fictional) spokesman, modeling the men's line.
        </p>
        <div className="spokes-gallery">
          {spokesmen.map((s) => (
            <figure key={s.img} className="spokes-card">
              <img src={s.img} alt={s.caption} />
              <figcaption>{s.caption}</figcaption>
            </figure>
          ))}
        </div>
      </section>

      {featured.length > 0 && (
        <section>
          <div className="section-head">
            <h2>Crowd favorites</h2>
            <Link to="/products">See everything →</Link>
          </div>
          <div className="product-grid">
            {featured.map((p) => (
              <ProductCard key={p.product_id} product={p} />
            ))}
          </div>
        </section>
      )}

      <section className="quote-band">
        <p>
          "A good sweatshirt is like a good friend. It's there when it's cold, it doesn't ask
          questions, and it's never once filibustered."
        </p>
      </section>
    </>
  )
}
