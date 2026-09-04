export interface Course {
  id: number;
  title: string;
  category: string;
  instructor_name: string;
  description: string;
  student_count: number;
}

export interface CourseDetail extends Course {
  duration_hours: number;
  status: string;
}

export interface Instructor {
  id: number;
  name: string;
  specialization: string;
  bio?: string | null;
  course_count: number;
}

export interface Student {
  id: number;
  name: string;
  email: string;
  enrolled_count: number;
  completed_count: number;
}

export interface EnrolledCourse {
  course_id: number;
  title: string;
  instructor_name: string;
  progress_percent: number;
  status: string;
}

export interface Dashboard {
  student_id: number;
  student_name: string;
  enrolled: EnrolledCourse[];
  completed: EnrolledCourse[];
  upcoming: EnrolledCourse[];
}

export interface Statistics {
  version: string;
  total_courses: number;
  total_instructors: number;
  total_students: number;
  total_enrollments: number;
}

export interface HealthStatus {
  status: string;
  service: string;
  version: string;
}

export interface ReadyStatus {
  status: string;
  database: string;
}
