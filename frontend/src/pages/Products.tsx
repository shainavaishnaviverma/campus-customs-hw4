import { useEffect, useMemo, useState } from 'react'
import { fetchProducts } from '../api'
import { useChatResults } from '../ChatResultsContext'
import ProductCard from '../components/ProductCard'
import type { Product } from '../types'

// Category chips → substrings matched against the (messy) garment_type labels.
const CATEGORIES: { label: string; match: string | null }[] = [
  { label: 'All', match: null },
  { label: 'Hoodies', match: 'hood' },
  { label: 'Crewnecks', match: 'crew' },
  { label: 'T-Shirts', match: 't-shirt' },
  { label: 'Quarter-Zips', match: 'zip' },
  { label: 'Jackets', match: 'jacket' },
  { label: 'Fleece', match: 'fleece' },
]

type Sort = 'featured' | 'price_asc' | 'price_desc' | 'name'

export default function Products() {
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [query, setQuery] = useState('')
  const [category, setCategory] = useState<string | null>(null)
  const [sort, setSort] = useState<Sort>('featured')
  const [inStockOnly, setInStockOnly] = useState(false)
  const chatResults = useChatResults()

  useEffect(() => {
    fetchProducts()
      .then(setProducts)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  const visible = useMemo(() => {
    const q = query.trim().toLowerCase()
    let list = products.filter((p) => {
      if (q) {
        const hay = [p.name, p.garment_type, p.description, ...p.colors, ...p.search_tags]
          .join(' ')
          .toLowerCase()
        if (!hay.includes(q)) return false
      }
      if (category && !p.garment_type.toLowerCase().includes(category)) return false
      if (inStockOnly && p.total_stock === 0) return false
      return true
    })
    if (sort === 'price_asc') list = [...list].sort((a, b) => a.price - b.price)
    else if (sort === 'price_desc') list = [...list].sort((a, b) => b.price - a.price)
    else if (sort === 'name') list = [...list].sort((a, b) => a.name.localeCompare(b.name))
    return list
  }, [products, query, category, sort, inStockOnly])

  // When the chat has pushed search results, show those instead of the full
  // catalogue. They're the same Product shape, so ProductCard — and its click
  // through to the single-item page — works exactly as for the full grid.
  const showingChat = chatResults.results.length > 0
  const grid = showingChat ? chatResults.results : visible

  return (
    <>
      <div className="section-head">
        <h1>Products</h1>
        <input
          className="search"
          type="search"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value)
            if (showingChat) chatResults.clear() // typing returns to the full catalogue
          }}
          placeholder="Search hoodies, colleges, sports…"
          aria-label="Search products"
        />
      </div>

      {!showingChat && (
        <div className="filter-bar">
          <div className="category-chips" role="group" aria-label="Filter by category">
            {CATEGORIES.map((c) => (
              <button
                key={c.label}
                type="button"
                className={`chip-btn ${category === c.match ? 'active' : ''}`}
                aria-pressed={category === c.match}
                onClick={() => setCategory(c.match)}
              >
                {c.label}
              </button>
            ))}
          </div>
          <div className="filter-controls">
            <label className="instock-toggle">
              <input
                type="checkbox"
                checked={inStockOnly}
                onChange={(e) => setInStockOnly(e.target.checked)}
              />
              In stock only
            </label>
            <label className="sort-select">
              Sort
              <select value={sort} onChange={(e) => setSort(e.target.value as Sort)}>
                <option value="featured">Featured</option>
                <option value="price_asc">Price: Low → High</option>
                <option value="price_desc">Price: High → Low</option>
                <option value="name">Name A–Z</option>
              </select>
            </label>
          </div>
        </div>
      )}

      {showingChat && (
        <div className="chat-result-banner">
          <span>
            Showing {chatResults.results.length} item
            {chatResults.results.length === 1 ? '' : 's'} the assistant found for{' '}
            <strong>“{chatResults.query}”</strong>
          </span>
          <button type="button" className="btn btn-small btn-ghost" onClick={chatResults.clear}>
            Show all products
          </button>
        </div>
      )}

      {loading && <p className="muted">Loading the racks…</p>}
      {error && <p className="error">Couldn't load products: {error}. Is the backend running?</p>}
      {!loading && !error && (
        <>
          {!showingChat && <p className="muted">{grid.length} items</p>}
          {grid.length === 0 ? (
            <p className="muted">No items match those filters. Try widening your search.</p>
          ) : (
            <div className="product-grid">
              {grid.map((p) => (
                <ProductCard key={p.product_id} product={p} />
              ))}
            </div>
          )}
        </>
      )}
    </>
  )
}
