import { Link } from "react-router-dom";
import { Card } from "../components/Card";
import { StatCard } from "../components/StatCard";
import { StatusMessage } from "../components/StatusMessage";
import { useFetch } from "../hooks/useFetch";
import { api } from "../services/api";

export function HomePage() {
  const courses = useFetch(() => api.listCourses(), []);
  const stats = useFetch(() => api.getStatistics(), []);
  const featured = (courses.data ?? []).slice(0, 3);

  return (
    <div className="page">
      <section className="hero">
        <div>
          <p className="hero__eyebrow">Welcome to</p>
          <h1 className="hero__title">Smart Education Portal</h1>
          <p className="hero__lead">
            Explore modern courses in cloud, Kubernetes, security, and backend
            engineering — taught by practitioners.
          </p>
          <Link to="/courses" className="btn btn--primary">Browse all courses</Link>
        </div>
      </section>

      <section className="section">
        <h2 className="section__title">Platform at a glance</h2>
        {stats.loading ? (
          <StatusMessage kind="loading" />
        ) : stats.error ? (
          <StatusMessage kind="error" message={stats.error} onRetry={stats.reload} />
        ) : stats.data ? (
          <div className="grid grid--stats">
            <StatCard icon="📚" label="Courses" value={stats.data.total_courses} />
            <StatCard icon="👩‍🏫" label="Instructors" value={stats.data.total_instructors} />
            <StatCard icon="🎓" label="Students" value={stats.data.total_students} />
            <StatCard icon="✅" label="Enrollments" value={stats.data.total_enrollments} />
          </div>
        ) : null}
      </section>

      <section className="section">
        <div className="section__head">
          <h2 className="section__title">Featured courses</h2>
          <Link to="/courses" className="link">See all →</Link>
        </div>

        {courses.loading ? (
          <StatusMessage kind="loading" />
        ) : courses.error ? (
          <StatusMessage kind="error" message={courses.error} onRetry={courses.reload} />
        ) : featured.length === 0 ? (
          <StatusMessage kind="empty" message="No courses available yet." />
        ) : (
          <div className="grid grid--cards">
            {featured.map((c) => (
              <Card
                key={c.id}
                eyebrow={c.category}
                title={<Link to={`/courses/${c.id}`}>{c.title}</Link>}
                footer={<span className="muted">by {c.instructor_name}</span>}
              >
                <p>{c.description}</p>
              </Card>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
