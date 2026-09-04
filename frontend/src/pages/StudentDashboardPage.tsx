import { useState } from "react";
import { Card } from "../components/Card";
import { ProgressBar } from "../components/ProgressBar";
import { StatCard } from "../components/StatCard";
import { StatusMessage } from "../components/StatusMessage";
import { useFetch } from "../hooks/useFetch";
import { api } from "../services/api";

export function StudentDashboardPage() {
  const [studentId, setStudentId] = useState<number>(1);
  const student = useFetch(() => api.getStudent(studentId), [studentId]);
  const dashboard = useFetch(() => api.getDashboard(studentId), [studentId]);

  return (
    <div className="page">
      <header className="page__header">
        <div>
          <h1>Student Dashboard</h1>
          <p className="muted">Your learning progress at a glance.</p>
        </div>
        <label className="input-wrap">
          <span className="input-wrap__label">Student ID</span>
          <input
            className="input"
            type="number"
            min={1}
            value={studentId}
            onChange={(e) => setStudentId(Math.max(1, Number(e.target.value) || 1))}
          />
        </label>
      </header>

      {student.loading ? (
        <StatusMessage kind="loading" />
      ) : student.error ? (
        <StatusMessage kind="error" message={student.error} onRetry={student.reload} />
      ) : student.data ? (
        <section className="section grid grid--stats">
          <StatCard icon="👤" label="Student" value={student.data.name || "—"} />
          <StatCard icon="📥" label="Enrolled" value={student.data.enrolled_count} />
          <StatCard icon="🏁" label="Completed" value={student.data.completed_count} />
        </section>
      ) : null}

      {dashboard.loading ? (
        <StatusMessage kind="loading" />
      ) : dashboard.error ? (
        <StatusMessage kind="error" message={dashboard.error} onRetry={dashboard.reload} />
      ) : dashboard.data ? (
        <>
          <Section title="In progress" items={dashboard.data.enrolled} showProgress />
          <Section title="Completed" items={dashboard.data.completed} />
          <Section title="Upcoming" items={dashboard.data.upcoming} />
        </>
      ) : null}
    </div>
  );
}

interface SectionProps {
  title: string;
  items: { course_id: number; title: string; instructor_name: string; progress_percent: number; status: string }[];
  showProgress?: boolean;
}

function Section({ title, items, showProgress }: SectionProps) {
  return (
    <section className="section">
      <h2 className="section__title">{title}</h2>
      {items.length === 0 ? (
        <StatusMessage kind="empty" message={`No ${title.toLowerCase()} courses.`} />
      ) : (
        <div className="grid grid--cards">
          {items.map((c) => (
            <Card
              key={c.course_id}
              title={c.title}
              eyebrow={c.instructor_name}
              footer={<span className={`pill pill--${c.status}`}>{c.status.replace("_", " ")}</span>}
            >
              {showProgress ? <ProgressBar value={c.progress_percent} /> : <p className="muted">Ready when you are.</p>}
            </Card>
          ))}
        </div>
      )}
    </section>
  );
}
