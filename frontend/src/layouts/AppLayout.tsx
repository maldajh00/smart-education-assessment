import { useState } from "react";
import { NavLink, Outlet } from "react-router-dom";

const NAV = [
  { to: "/", label: "Home", end: true },
  { to: "/courses", label: "Courses" },
  { to: "/instructors", label: "Instructors" },
  { to: "/dashboard", label: "Student Dashboard" },
  { to: "/status", label: "System Status" },
];

export function AppLayout() {
  const [open, setOpen] = useState(false);

  return (
    <div className={`shell ${open ? "shell--open" : ""}`}>
      <aside className="sidebar" aria-label="Primary">
        <div className="sidebar__brand">
          <span className="sidebar__logo" aria-hidden="true">SE</span>
          <span className="sidebar__brandText">
            <strong>Smart Education</strong>
            <span>Portal</span>
          </span>
        </div>
        <nav className="sidebar__nav">
          {NAV.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                `sidebar__link ${isActive ? "sidebar__link--active" : ""}`
              }
              onClick={() => setOpen(false)}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar__footer">v1.0.0</div>
      </aside>

      <div className="main">
        <header className="topbar">
          <button
            className="topbar__menu"
            aria-label="Toggle navigation"
            onClick={() => setOpen((v) => !v)}
          >
            <span />
            <span />
            <span />
          </button>
          <div className="topbar__title">Smart Education Portal</div>
        </header>
        <main className="content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
