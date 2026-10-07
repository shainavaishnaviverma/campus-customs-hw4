import type { ChatReply, ChatTurn, PageContext, Product } from './types'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, init)
  if (!res.ok) {
    throw new Error(res.status === 404 ? 'Not found' : `Request failed (${res.status})`)
  }
  return res.json() as Promise<T>
}

export function fetchProducts(q?: string): Promise<Product[]> {
  const params = q ? `?q=${encodeURIComponent(q)}` : ''
  return request<Product[]>(`/api/products${params}`)
}

export function fetchProduct(productId: string): Promise<Product> {
  return request<Product>(`/api/products/${encodeURIComponent(productId)}`)
}

// credentials: 'include' sends the session cookie so the agent knows who's
// chatting and can persist history for signed-in shoppers. `page` tells it what
// the shopper is viewing, so "do you have this in pink?" resolves.
export function sendChat(message: string, page?: PageContext): Promise<ChatReply> {
  return request<ChatReply>('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ message, page: page ?? null }),
  })
}

// Saved conversation for the signed-in shopper (empty for guests).
export function fetchChatHistory(): Promise<ChatTurn[]> {
  return request<ChatTurn[]>('/api/chat/history', { credentials: 'include' })
}

export const formatPrice = (price: number) =>
  price.toLocaleString('en-US', { style: 'currency', currency: 'USD' })

// ---- Auth ----
import type { User } from './types'

interface SignupInput {
  first_name: string
  last_name: string
  email: string
  password: string
}

async function authRequest<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify(body),
  })
  if (!res.ok) {
    let detail = `Request failed (${res.status})`
    try {
      const data = await res.json()
      if (typeof data.detail === 'string') detail = data.detail
      else if (Array.isArray(data.detail) && data.detail[0]?.msg) detail = data.detail[0].msg
    } catch {
      /* keep default */
    }
    throw new Error(detail)
  }
  return res.json() as Promise<T>
}

export const signup = (input: SignupInput) => authRequest<User>('/api/auth/signup', input)

export const login = (email: string, password: string) =>
  authRequest<User>('/api/auth/login', { email, password })

export async function logout(): Promise<void> {
  await fetch('/api/auth/logout', { method: 'POST', credentials: 'include' })
}

export async function fetchMe(): Promise<User | null> {
  const res = await fetch('/api/auth/me', { credentials: 'include' })
  return res.ok ? ((await res.json()) as User) : null
}
