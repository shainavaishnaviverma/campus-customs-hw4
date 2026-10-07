import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../AuthContext'

const links = [
  { to: '/', label: 'Home', end: true },
  { to: '/products', label: 'Products' },
  { to: '/about', label: 'About Us' },
]

export default function NavBar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  async function handleLogout() {
    await logout()
    navigate('/')
  }

  return (
    <header className="navbar">
      <Link to="/" className="brand">
        <span className="brand-mark">CC</span>
        Campus Customs
      </Link>
      <nav className="nav-links">
        {links.map((l) => (
          <NavLink key={l.to} to={l.to} end={l.end}>
            {l.label}
          </NavLink>
        ))}
      </nav>
      <div className="nav-auth">
        {user ? (
          <>
            <span className="nav-greeting">Hi, {user.first_name ?? 'Bulldog'}</span>
            <button type="button" className="btn btn-small" onClick={handleLogout}>
              Log out
            </button>
          </>
        ) : (
          <>
            <NavLink to="/login">Log in</NavLink>
            <NavLink to="/signup" className="btn btn-small">
              Create account
            </NavLink>
          </>
        )}
      </div>
    </header>
  )
}
