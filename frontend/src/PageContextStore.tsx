import { createContext, useContext, useState, type ReactNode } from 'react'
import type { PageContext } from './types'

/**
 * Tracks what the shopper is currently looking at (set by the product detail
 * page). The chat widget sends this to the backend with each message so the
 * agent can resolve "this one" / "do you have this in pink?" to the right item.
 */
interface PageContextValue {
  page: PageContext | null
  setPage: (page: PageContext | null) => void
}

const PageCtx = createContext<PageContextValue | null>(null)

export function PageContextProvider({ children }: { children: ReactNode }) {
  const [page, setPage] = useState<PageContext | null>(null)
  return <PageCtx.Provider value={{ page, setPage }}>{children}</PageCtx.Provider>
}

// eslint-disable-next-line react-refresh/only-export-components
export function usePageContext(): PageContextValue {
  const ctx = useContext(PageCtx)
  if (!ctx) throw new Error('usePageContext must be used within PageContextProvider')
  return ctx
}
