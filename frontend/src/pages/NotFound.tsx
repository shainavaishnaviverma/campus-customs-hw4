import { Link } from 'react-router-dom'

export default function NotFound() {
  return (
    <div className="prose">
      <h1>Page not found</h1>
      <p>
        This page is about as lost as a Harvard fan at The Game. <Link to="/">Head home</Link>.
      </p>
    </div>
  )
}
