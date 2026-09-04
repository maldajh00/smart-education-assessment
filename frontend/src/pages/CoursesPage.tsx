import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Card } from "../components/Card";
import { StatusMessage } from "../components/StatusMessage";
import { useFetch } from "../hooks/useFetch";
import { api } from "../services/api";

export function CoursesPage() {
  const { data, loading, error, reload } = useFetch(() => api.listCourses(), []);
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState<string>("");

  const categories = useMemo(() => {
    const set = new Set((data ?? []).map((c) => c.category));
    return Array.from(set).sort();
  }, [data]);

  const filtered = useMemo(() => {
    return (data ?? []).filter((c) => {
      const matchesQ =
        query.length === 0 ||
        c.title.toLowerCase().includes(query.toLowerCase()) ||
        c.instructor_name.toLowerCase().includes(query.toLowerCase());
      const matchesC = category === "" || c.category === category;
      return matchesQ && matchesC;
    });
  }, [data, query, category]);

  return (
    <div className="page">
      <header className="page__header">
        <div>
          <h1>Courses</h1>
          <p className="muted">Browse the full catalog.</p>
        </div>
        <div className="filters">
          <input
            className="input"
            type="search"
            placeholder="Search title or instructor"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            aria-label="Search courses"
          />
          <select
            className="input"
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            aria-label="Filter by category"
          >
            <option value="">All categories</option>
            {categories.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>
      </header>

      {loading ? (
        <StatusMessage kind="loading" />
      ) : error ? (
        <StatusMessage kind="error" message={error} onRetry={reload} />
      ) : filtered.length === 0 ? (
        <StatusMessage kind="empty" message="No courses match your filters." />
      ) : (
        <div className="grid grid--cards">
          {filtered.map((c) => (
            <Card
              key={c.id}
              eyebrow={c.category}
              title={<Link to={`/courses/${c.id}`}>{c.title}</Link>}
              footer={
                <div className="row row--between">
                  <span className="muted">by {c.instructor_name}</span>
                  <span className="pill">{c.student_count} students</span>
                </div>
              }
            >
              <p>{c.description}</p>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
