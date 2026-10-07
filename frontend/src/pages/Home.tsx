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
    text: "Every stitch is the real McCoy. We don't do knockoffs — a counterfeit Yale hoodie is like a screen door on a submarine: looks fine till it matters. If it's on our rack, Yale put its name on it.",
    dog: '/art/bulldog-1.svg',
  },
  {
    title: 'Every Bulldog in the family',
    text: "Students, alumni, mamas, grandpas, and that cousin who swears he almost got in. We'll dress him too — his money spends the same, bless his heart.",
    dog: '/art/bulldog-2.svg',
  },
  {
    title: 'Colleges, schools, and sports',
    text: "Residential colleges, grad schools, and teams from fencing to field hockey. Pick your side and wear it proud. Fence-sitting's uncomfortable, and it's bad for the fence.",
    dog: '/art/bulldog-3.svg',
  },
]

// A few more Senator-Kennedy-style straight-talk quips for the home page.
const quips = [
  "A good sweatshirt is like a good friend: there when it's cold, doesn't ask questions, and never once filibustered.",
  "Our prices are honest. If you find cheaper Yale gear, it's either a knockoff or it fell off a truck — and that truck wasn't ours.",
  "This fleece is softer than a two-dollar steak and twice as satisfying.",
  "Buy the hoodie. Life's too short to be cold and underdressed at The Game.",
]

// Our celebrity spokesman, Picolas Page, each portrait paired with the men's
// item he's endorsing (product thumbnail + link to its page).
const spokesmen = [
  {
    img: '/art/cage-1.jpg',
    productId: 'basic-hoodie-big-yale',
    product: 'Basic Hoodie Big Yale',
    price: '$68',
    productImg: '/media/products/basic-hoodie-big-yale.jpg',
  },
  {
    img: '/art/cage-2.jpg',
    productId: '2025-yale-vs-harvard-t-shirt',
    product: '2025 Yale vs. Harvard Tee',
    price: '$32',
    productImg: '/media/products/2025-yale-vs-harvard-t-shirt.jpg',
  },
  {
    img: '/art/cage-3.jpg',
    productId: 'baseball-left-chest-crewneck',
    product: 'Baseball Left Chest Crewneck',
    price: '$58',
    productImg: '/media/products/baseball-left-chest-crewneck.jpg',
  },
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
            Look, I'm not saying a Yale hoodie will make you smarter. I'm saying nobody ever looked
            dumber in one. We're right on Broadway in New Haven, selling officially licensed Yale
            gear that's comfortable, built to last, and bluer than a hound dog in a snowstorm. Come
            on in — the coffee's free and the sweatshirts are worth every nickel.
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
          <img src="/art/cage-1.jpg" alt="Picolas Page, Campus Customs spokesman" />
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
          <h2>As seen on Picolas Page</h2>
        </div>
        <p className="muted">
          Our wildly committed celebrity spokesman, Picolas Page, endorsing the men's line —
          tap his pick to shop it.
        </p>
        <div className="spokes-gallery">
          {spokesmen.map((s) => (
            <Link key={s.img} to={`/products/${s.productId}`} className="spokes-card">
              <div className="spokes-photo">
                <img src={s.img} alt={`Picolas Page endorsing the ${s.product}`} />
                <img className="spokes-badge" src={s.productImg} alt="" aria-hidden="true" />
              </div>
              <figcaption>
                Picolas Page’s pick: <strong>{s.product}</strong> · {s.price}
              </figcaption>
            </Link>
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

      <section>
        <div className="section-head">
          <h2>Straight talk from the shop</h2>
        </div>
        <div className="quip-grid">
          {quips.map((q) => (
            <blockquote key={q} className="quip">
              {q}
            </blockquote>
          ))}
        </div>
      </section>
    </>
  )
}
