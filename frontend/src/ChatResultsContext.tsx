import { createContext, useContext, useState, type ReactNode } from 'react'
import type { Product } from './types'

/**
 * Holds the product cards the chat agent most recently surfaced, so the chat
 * widget can push search results onto the page and the Products page can render
 * them. The cards are plain Product objects, so the normal ProductCard (and its
 * click-through to the single-item detail page) works unchanged.
 */
interface ChatResultsValue {
  query: string
  results: Product[]
  show: (query: string, results: Product[]) => void
  clear: () => void
}

const ChatResultsContext = createContext<ChatResultsValue | null>(null)

export function ChatResultsProvider({ children }: { children: ReactNode }) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<Product[]>([])

  const value: ChatResultsValue = {
    query,
    results,
    show: (q, r) => {
      setQuery(q)
      setResults(r)
    },
    clear: () => {
      setQuery('')
      setResults([])
    },
  }

  return <ChatResultsContext.Provider value={value}>{children}</ChatResultsContext.Provider>
}

// eslint-disable-next-line react-refresh/only-export-components
export function useChatResults(): ChatResultsValue {
  const ctx = useContext(ChatResultsContext)
  if (!ctx) throw new Error('useChatResults must be used within ChatResultsProvider')
  return ctx
}
