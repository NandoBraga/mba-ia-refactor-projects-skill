const express = require('express');
const config = require('./config');
const { Database } = require('./repositories/database');
const createCheckoutService = require('./services/checkoutService');
const createReportService = require('./services/reportService');
const registerRoutes = require('./routes');

async function createApp() {
    const db = new Database();
    await db.init();
    const app = express();
    app.use(express.json({ limit: '100kb' }));
    registerRoutes(app, {
        db,
        checkout: createCheckoutService(db),
        report: createReportService(db)
    });
    return app;
}

if (require.main === module) {
    createApp().then((app) => {
        app.listen(config.port, () => console.log(`LMS API rodando na porta ${config.port}`));
    }).catch((error) => {
        console.error('Application failed to start:', error.message);
        process.exitCode = 1;
    });
}

module.exports = { createApp };
