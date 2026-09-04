import { Card } from "../components/Card";
import { StatusMessage } from "../components/StatusMessage";
import { useFetch } from "../hooks/useFetch";
import { api } from "../services/api";

export function SystemStatusPage() {
  const health = useFetch(() => api.getHealth(), []);
  const ready = useFetch(() => api.getReady(), []);
  const stats = useFetch(() => api.getStatistics(), []);

  return (
    <div className="page">
      <header className="page__header">
        <div>
          <h1>System Status</h1>
          <p className="muted">Operational overview of the backend and database.</p>
        </div>
      </header>

      <div className="grid grid--cards">
        <Card title="Backend" eyebrow="/health">
          {health.loading ? (
            <StatusMessage kind="loading" />
          ) : health.error ? (
            <StatusMessage kind="error" message={health.error} onRetry={health.reload} />
          ) : health.data ? (
            <ul className="kv">
              <li><span>Status</span><strong className="ok">{health.data.status}</strong></li>
              <li><span>Service</span><strong>{health.data.service}</strong></li>
              <li><span>Version</span><strong>{health.data.version}</strong></li>
            </ul>
          ) : null}
        </Card>

        <Card title="Database" eyebrow="/ready">
          {ready.loading ? (
            <StatusMessage kind="loading" />
          ) : ready.error ? (
            <StatusMessage kind="error" message={ready.error} onRetry={ready.reload} />
          ) : ready.data ? (
            <ul className="kv">
              <li>
                <span>Status</span>
                <strong className={ready.data.status === "ready" ? "ok" : "bad"}>
                  {ready.data.status}
                </strong>
              </li>
              <li>
                <span>Database</span>
                <strong className={ready.data.database === "connected" ? "ok" : "bad"}>
                  {ready.data.database}
                </strong>
              </li>
            </ul>
          ) : null}
        </Card>

        <Card title="Application" eyebrow="/api/statistics">
          {stats.loading ? (
            <StatusMessage kind="loading" />
          ) : stats.error ? (
            <StatusMessage kind="error" message={stats.error} onRetry={stats.reload} />
          ) : stats.data ? (
            <ul className="kv">
              <li><span>Version</span><strong>{stats.data.version}</strong></li>
              <li><span>Courses</span><strong>{stats.data.total_courses}</strong></li>
              <li><span>Instructors</span><strong>{stats.data.total_instructors}</strong></li>
              <li><span>Students</span><strong>{stats.data.total_students}</strong></li>
              <li><span>Enrollments</span><strong>{stats.data.total_enrollments}</strong></li>
            </ul>
          ) : null}
        </Card>
      </div>
    </div>
  );
}
