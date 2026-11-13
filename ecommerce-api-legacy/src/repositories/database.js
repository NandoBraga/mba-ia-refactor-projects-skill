const sqlite3 = require('sqlite3').verbose();
const config = require('../config');

class Database {
    constructor() {
        this.db = new sqlite3.Database(config.dbPath);
    }

    run(sql, params = []) {
        return new Promise((resolve, reject) => {
            this.db.run(sql, params, function onRun(error) {
                if (error) return reject(error);
                resolve({ id: this.lastID, changes: this.changes });
            });
        });
    }

    get(sql, params = []) {
        return new Promise((resolve, reject) => {
            this.db.get(sql, params, (error, row) => error ? reject(error) : resolve(row));
        });
    }

    all(sql, params = []) {
        return new Promise((resolve, reject) => {
            this.db.all(sql, params, (error, rows) => error ? reject(error) : resolve(rows));
        });
    }

    async init() {
        await this.run('PRAGMA foreign_keys = ON');
        await this.run('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE, pass TEXT)');
        await this.run('CREATE TABLE IF NOT EXISTS courses (id INTEGER PRIMARY KEY, title TEXT, price REAL, active INTEGER)');
        await this.run('CREATE TABLE IF NOT EXISTS enrollments (id INTEGER PRIMARY KEY, user_id INTEGER, course_id INTEGER, FOREIGN KEY(user_id) REFERENCES users(id), FOREIGN KEY(course_id) REFERENCES courses(id))');
        await this.run('CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY, enrollment_id INTEGER, amount REAL, status TEXT, FOREIGN KEY(enrollment_id) REFERENCES enrollments(id))');
        await this.run('CREATE TABLE IF NOT EXISTS audit_logs (id INTEGER PRIMARY KEY, action TEXT, created_at DATETIME)');

        const user = await this.get('SELECT id FROM users LIMIT 1');
        if (!user) {
            await this.run('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)', ['Leonan', 'leonan@fullcycle.com.br', hashPassword('123')]);
            await this.run('INSERT INTO courses (title, price, active) VALUES (?, ?, ?), (?, ?, ?)', ['Clean Architecture', 997, 1, 'Docker', 497, 1]);
            const enrollment = await this.run('INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)', [1, 1]);
            await this.run('INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)', [enrollment.id, 997, 'PAID']);
        }
    }
}

function hashPassword(password) {
    const crypto = require('crypto');
    const salt = crypto.randomBytes(16).toString('hex');
    const hash = crypto.scryptSync(password, salt, 64).toString('hex');
    return `${salt}:${hash}`;
}

function verifyPassword(password, stored) {
    const crypto = require('crypto');
    const [salt, expected] = String(stored).split(':');
    if (!salt || !expected) return false;
    const actual = crypto.scryptSync(password, salt, 64).toString('hex');
    return crypto.timingSafeEqual(Buffer.from(actual, 'hex'), Buffer.from(expected, 'hex'));
}

module.exports = { Database, hashPassword, verifyPassword };
