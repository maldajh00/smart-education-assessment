import { Link, useParams } from "react-router-dom";
import { StatusMessage } from "../components/StatusMessage";
import { useFetch } from "../hooks/useFetch";
import { api } from "../services/api";

export function CourseDetailsPage() {
  const { courseId } = useParams<{ courseId: string }>();
  const id = Number(courseId);
  const { data, loading, error, reload } = useFetch(() => api.getCourse(id), [id]);

  if (Number.isNaN(id)) {
    return <StatusMessage kind="error" title="Invalid course ID" message="URL parameter is not a number." />;
  }
  if (loading) return <StatusMessage kind="loading" />;
  if (error) return <StatusMessage kind="error" message={error} onRetry={reload} />;
  if (!data) return <StatusMessage kind="empty" />;

  return (
    <div className="page">
      <nav className="crumbs">
        <Link to="/courses">← Back to courses</Link>
      </nav>

      <header className="page__header">
        <div>
          <span className="pill pill--muted">{data.category}</span>
          <h1>{data.title}</h1>
          <p className="muted">by {data.instructor_name}</p>
        </div>
        <span className={`pill pill--${data.status}`}>{data.status}</span>
      </header>

      <section className="section">
        <p className="lead">{data.description}</p>
      </section>

      <section className="section grid grid--stats">
        <div className="stat">
          <div className="stat__value">{data.duration_hours}h</div>
          <div className="stat__label">Duration</div>
        </div>
        <div className="stat">
          <div className="stat__value">{data.student_count}</div>
          <div className="stat__label">Students enrolled</div>
        </div>
        <div className="stat">
          <div className="stat__value">{data.status}</div>
          <div className="stat__label">Status</div>
        </div>
      </section>
    </div>
  );
}
