// Real fetching is wired in Phase 6. The client is defined now so pages
// import a stable shape from the beginning.

import type {
  Course,
  CourseDetail,
  Dashboard,
  HealthStatus,
  Instructor,
  ReadyStatus,
  Statistics,
  Student,
} from "../types";

const BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? "/api";
const ROOT_URL = BASE_URL.replace(/\/api\/?$/, "");

async function jsonOrThrow<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(`HTTP ${res.status} ${res.statusText}${body ? `: ${body}` : ""}`);
  }
  return (await res.json()) as T;
}

export const api = {
  listCourses: () => fetch(`${BASE_URL}/courses`).then((r) => jsonOrThrow<Course[]>(r)),
  getCourse: (id: number) =>
    fetch(`${BASE_URL}/courses/${id}`).then((r) => jsonOrThrow<CourseDetail>(r)),
  listInstructors: () =>
    fetch(`${BASE_URL}/instructors`).then((r) => jsonOrThrow<Instructor[]>(r)),
  getInstructor: (id: number) =>
    fetch(`${BASE_URL}/instructors/${id}`).then((r) => jsonOrThrow<Instructor>(r)),
  getStudent: (id: number) =>
    fetch(`${BASE_URL}/students/${id}`).then((r) => jsonOrThrow<Student>(r)),
  getDashboard: (studentId: number) =>
    fetch(`${BASE_URL}/dashboard/${studentId}`).then((r) => jsonOrThrow<Dashboard>(r)),
  getStatistics: () =>
    fetch(`${BASE_URL}/statistics`).then((r) => jsonOrThrow<Statistics>(r)),
  getHealth: () => fetch(`${ROOT_URL}/health`).then((r) => jsonOrThrow<HealthStatus>(r)),
  getReady: async (): Promise<ReadyStatus> => {
    const r = await fetch(`${ROOT_URL}/ready`);
    // /ready may return 503 with a JSON body — parse either way.
    const body = (await r.json()) as ReadyStatus;
    return body;
  },
};
