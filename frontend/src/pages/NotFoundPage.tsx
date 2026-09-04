import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <div className="page notfound">
      <div className="notfound__code">404</div>
      <h1>Page not found</h1>
      <p className="muted">The page you are looking for does not exist or has moved.</p>
      <Link to="/" className="btn btn--primary">Go home</Link>
    </div>
  );
}
