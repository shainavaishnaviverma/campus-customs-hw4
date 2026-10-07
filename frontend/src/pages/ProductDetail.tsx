import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { fetchProduct, formatPrice } from '../api'
import { usePageContext } from '../PageContextStore'
import type { Product } from '../types'

const LOW_STOCK = 5

function stockLabel(qty: number) {
  if (qty === 0) return 'Out of stock'
  if (qty <= LOW_STOCK) return `Only ${qty} left`
  return `${qty} in stock`
}

export default function ProductDetail() {
  const { productId = '' } = useParams()
  const { setPage } = usePageContext()
  // Tag results with the id they belong to, so a stale result is ignored on navigation.
  const [result, setResult] = useState<{ id: string; product?: Product; error?: string }>()

  useEffect(() => {
    fetchProduct(productId)
      .then((product) => setResult({ id: productId, product }))
      .catch((e: Error) => setResult({ id: productId, error: e.message }))
  }, [productId])

  const current = result?.id === productId ? result : undefined
  const product = current?.product
  const error = current?.error

  // Tell the chat widget which item is on screen (so "do you have this in pink?"
  // resolves), and clear it when the shopper leaves the page.
  useEffect(() => {
    if (product) setPage({ product_id: product.product_id, product_name: product.name })
    return () => setPage(null)
  }, [product, setPage])

  if (error) {
    return (
      <div className="prose">
        <h1>{error === 'Not found' ? "We don't carry that one" : 'Something went wrong'}</h1>
        <p>
          <Link to="/products">← Back to all products</Link>
        </p>
      </div>
    )
  }
  if (!product) return <p className="muted">Loading…</p>

  return (
    <>
      <Link to="/products" className="back-link">
        ← All products
      </Link>
      <div className="detail">
        <div className="detail-image">
          <img src={product.image_url} alt={product.name} />
        </div>
        <div className="detail-info">
          <p className="eyebrow">{product.garment_type}</p>
          <h1>{product.name}</h1>
          <p className="detail-price">{formatPrice(product.price)}</p>
          <p>{product.description}</p>

          <h3>Colors</h3>
          <div className="chips">
            {product.colors.map((c) => (
              <span key={c} className="chip">
                {c}
              </span>
            ))}
          </div>

          <h3>Sizes &amp; stock</h3>
          {product.inventory.length === 0 ? (
            <p className="muted">Stock info isn't available for this item yet.</p>
          ) : (
            <table className="stock-table">
              <tbody>
                {product.inventory.map((s) => (
                  <tr key={s.size} className={s.quantity === 0 ? 'out' : ''}>
                    <th>{s.size}</th>
                    <td>{stockLabel(s.quantity)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
          <p className="muted">{product.total_stock} total in stock across all sizes.</p>
        </div>
      </div>
    </>
  )
}
