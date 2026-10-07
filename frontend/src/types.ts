export interface SizeStock {
  size: string
  quantity: number
}

export interface Product {
  product_id: string
  name: string
  garment_type: string
  description: string
  colors: string[]
  search_tags: string[]
  image_url: string
  price: number
  inventory: SizeStock[]
  total_stock: number
}

export interface ChatReply {
  reply: string
  products: Product[]
}

export interface User {
  id: number
  first_name: string | null
  last_name: string | null
  email: string
}

export interface PageContext {
  product_id?: string
  product_name?: string
}

export interface ChatTurn {
  role: 'user' | 'assistant'
  content: string
  products: Product[]
}
