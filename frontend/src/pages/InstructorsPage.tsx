import { Card } from "../components/Card";
import { StatusMessage } from "../components/StatusMessage";
import { useFetch } from "../hooks/useFetch";
import { api } from "../services/api";

function initials(name: string): string {
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((s) => s[0]?.toUpperCase())
    .join("");
}

export function InstructorsPage() {
  const { data, loading, error, reload } = useFetch(() => api.listInstructors(), []);

  return (
    <div className="page">
      <header className="page__header">
        <div>
          <h1>Instructors</h1>
          <p className="muted">Meet the people teaching on the platform.</p>
        </div>
      </header>

      {loading ? (
        <StatusMessage kind="loading" />
      ) : error ? (
        <StatusMessage kind="error" message={error} onRetry={reload} />
      ) : !data || data.length === 0 ? (
        <StatusMessage kind="empty" message="No instructors available yet." />
      ) : (
        <div className="grid grid--cards">
          {data.map((i) => (
            <Card
              key={i.id}
              title={
                <div className="instructor__head">
                  <span className="avatar" aria-hidden="true">{initials(i.name)}</span>
                  <span>{i.name}</span>
                </div>
              }
              eyebrow={i.specialization}
              footer={<span className="pill">{i.course_count} courses</span>}
            >
              {i.bio ? <p>{i.bio}</p> : <p className="muted">No bio provided.</p>}
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
