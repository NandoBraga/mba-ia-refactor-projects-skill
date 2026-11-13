function createReportService(db) {
    return {
        async financialReport() {
            const rows = await db.all(
                'SELECT c.id AS course_id, c.title AS course, COALESCE(SUM(CASE WHEN p.status = ? THEN p.amount ELSE 0 END), 0) AS revenue, COUNT(DISTINCT e.user_id) AS students_count FROM courses c LEFT JOIN enrollments e ON e.course_id = c.id LEFT JOIN payments p ON p.enrollment_id = e.id GROUP BY c.id, c.title',
                ['PAID']
            );
            const students = await db.all(
                'SELECT e.course_id, u.name AS student, COALESCE(p.amount, 0) AS paid FROM enrollments e JOIN users u ON u.id = e.user_id LEFT JOIN payments p ON p.enrollment_id = e.id'
            );
            return rows.map((row) => ({
                course: row.course,
                revenue: row.revenue,
                students: students.filter((student) => student.course_id === row.course_id).map(({ student, paid }) => ({ student, paid }))
            }));
        }
    };
}

module.exports = createReportService;
