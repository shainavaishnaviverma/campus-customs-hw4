import { useEffect, useRef, useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import { fetchChatHistory, formatPrice, sendChat } from '../api'
import { useAuth } from '../AuthContext'
import { useChatResults } from '../ChatResultsContext'
import { usePageContext } from '../PageContextStore'
import type { Product } from '../types'

interface Message {
  role: 'user' | 'assistant'
  content: string
  products?: Product[]
}

const GREETING: Message = {
  role: 'assistant',
  content: "Howdy. Looking for a hoodie, a crewneck, or just some company? Ask away.",
}

function ProductChips({ products, onPick }: { products: Product[]; onPick: () => void }) {
  return (
    <div className="chat-products">
      {products.map((p) => (
        <Link
          key={p.product_id}
          to={`/products/${p.product_id}`}
          className="chat-product"
          onClick={onPick}
        >
          <img src={p.image_url} alt={p.name} loading="lazy" />
          <span className="chat-product-name">{p.name}</span>
          <span className="chat-product-price">{formatPrice(p.price)}</span>
        </Link>
      ))}
    </div>
  )
}

export default function ChatWidget() {
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>([GREETING])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const endRef = useRef<HTMLDivElement>(null)
  const chatResults = useChatResults()
  const { page } = usePageContext()
  const { user, loading: authLoading } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, open])

  // Reload a signed-in shopper's saved conversation when they arrive or log in;
  // reset to a fresh greeting for guests / after logout.
  useEffect(() => {
    if (authLoading) return
    let cancelled = false
    const load = async (): Promise<Message[]> => {
      if (!user) return [GREETING]
      try {
        const turns = await fetchChatHistory()
        const restored = turns.map((t) => ({
          role: t.role,
          content: t.content,
          products: t.products,
        }))
        return restored.length > 0 ? [GREETING, ...restored] : [GREETING]
      } catch {
        return [GREETING]
      }
    }
    load().then((msgs) => {
      if (!cancelled) setMessages(msgs)
    })
    return () => {
      cancelled = true
    }
  }, [user, authLoading])

  async function send(raw: string) {
    const text = raw.trim()
    if (!text || sending) return
    setMessages((m) => [...m, { role: 'user', content: text }])
    setInput('')
    setSending(true)
    try {
      const { reply, products } = await sendChat(text, page ?? undefined)
      setMessages((m) => [...m, { role: 'assistant', content: reply, products }])
      // Push the agent's matches onto the page as full product cards and take the
      // shopper to the Products page to see them.
      if (products.length > 0) {
        chatResults.show(text, products)
        navigate('/products')
      }
    } catch {
      setMessages((m) => [
        ...m,
        { role: 'assistant', content: "I couldn't reach the shop's server. Try again in a moment." },
      ])
    } finally {
      setSending(false)
    }
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    send(input)
  }

  // Shown until the shopper sends their first message, to advertise what the
  // assistant can do and remove the friction of a blank box.
  const starters = ['What hoodies do you have?', 'Crewnecks under $60', "What's your cheapest item?"]
  const showStarters = !messages.some((m) => m.role === 'user')

  return (
    <div className="chat-widget">
      {open && (
        <section className="chat-panel" aria-label="Shopping assistant">
          <header className="chat-header">
            <img className="chat-avatar" src="/art/bulldog-1.svg" alt="" />
            <span className="title-wrap">
              Bulldog Assistant
              <small>Yale gear concierge</small>
            </span>
            <button type="button" onClick={() => setOpen(false)} aria-label="Close chat">
              ×
            </button>
          </header>
          <div className="chat-messages">
            {messages.map((m, i) => (
              <div key={i} className="chat-row">
                <div className={`chat-bubble ${m.role}`}>
                  {m.role === 'assistant' ? (
                    <ReactMarkdown>{m.content}</ReactMarkdown>
                  ) : (
                    m.content
                  )}
                </div>
                {m.products && m.products.length > 0 && (
                  <ProductChips products={m.products} onPick={() => setOpen(false)} />
                )}
              </div>
            ))}
            {showStarters && (
              <div className="chat-starters">
                {starters.map((s) => (
                  <button key={s} type="button" className="chip-btn" onClick={() => send(s)}>
                    {s}
                  </button>
                ))}
              </div>
            )}
            {sending && <div className="chat-bubble assistant typing">…</div>}
            <div ref={endRef} />
          </div>
          <form className="chat-input" onSubmit={handleSubmit}>
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about sizes, colors, prices…"
              aria-label="Chat message"
            />
            <button type="submit" disabled={sending || !input.trim()}>
              Send
            </button>
          </form>
        </section>
      )}
      <button
        type="button"
        className="chat-toggle"
        onClick={() => setOpen((o) => !o)}
        aria-label={open ? 'Close chat' : 'Open chat'}
      >
        {open ? '×' : <img src="/art/bulldog-3.svg" alt="" />}
      </button>
    </div>
  )
}
