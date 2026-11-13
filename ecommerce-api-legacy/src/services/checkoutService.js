const { hashPassword, verifyPassword } = require('../repositories/database');

function createCheckoutService(db) {
    return {
        async checkout({ name, email, password, courseId, card }) {
            if (!name || !email || !password || !courseId || !card) {
                return { status: 400, body: 'Bad Request' };
            }

            const course = await db.get('SELECT * FROM courses WHERE id = ? AND active = 1', [courseId]);
            if (!course) return { status: 404, body: 'Curso não encontrado' };

            let user = await db.get('SELECT * FROM users WHERE email = ?', [email]);
            if (user && !verifyPassword(password, user.pass)) {
                return { status: 401, body: 'Credenciais inválidas' };
            }
            if (!user) {
                const result = await db.run('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)', [name, email, hashPassword(password)]);
                user = { id: result.id, name, email };
            }

            const status = String(card).startsWith('4') ? 'PAID' : 'DENIED';
            if (status === 'DENIED') return { status: 400, body: 'Pagamento recusado' };

            const enrollment = await db.run('INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)', [user.id, courseId]);
            await db.run('INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)', [enrollment.id, course.price, status]);
            await db.run('INSERT INTO audit_logs (action, created_at) VALUES (?, datetime(\'now\'))', [`Checkout curso ${courseId} por ${user.id}`]);
            return { status: 200, body: { msg: 'Sucesso', enrollment_id: enrollment.id } };
        }
    };
}

module.exports = createCheckoutService;
