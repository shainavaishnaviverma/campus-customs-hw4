import { Link } from 'react-router-dom'
import { formatPrice } from '../api'
import type { Product } from '../types'

const MAX_BLURB = 110

function blurb(text: string) {
  return text.length > MAX_BLURB ? `${text.slice(0, MAX_BLURB).trimEnd()}…` : text
}

export default function ProductCard({ product }: { product: Product }) {
  return (
    <Link to={`/products/${product.product_id}`} className="product-card">
      <div className="product-card-image">
        <img src={product.image_url} alt={product.name} loading="lazy" />
        {product.total_stock === 0 && <span className="badge">Sold out</span>}
      </div>
      <div className="product-card-body">
        <h3>{product.name}</h3>
        <p className="price">{formatPrice(product.price)}</p>
        <p className="blurb">{blurb(product.description)}</p>
      </div>
    </Link>
  )
}
