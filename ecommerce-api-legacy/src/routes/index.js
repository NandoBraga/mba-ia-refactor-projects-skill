const express = require('express');
const config = require('../config');
const createCheckoutController = require('../controllers/checkoutController');
const createReportController = require('../controllers/reportController');

function registerRoutes(app, services) {
    const router = express.Router();
    router.post('/checkout', createCheckoutController(services.checkout));
    router.get('/admin/financial-report', (req, res, next) => {
        if (!config.adminApiKey || req.get('x-admin-key') !== config.adminApiKey) {
            return res.status(401).send('Não autorizado');
        }
        return createReportController(services.report)(req, res, next);
    });
    router.delete('/users/:id', async (req, res) => {
        if (!config.adminApiKey || req.get('x-admin-key') !== config.adminApiKey) {
            return res.status(401).send('Não autorizado');
        }
        try {
            await services.db.run('DELETE FROM users WHERE id = ?', [req.params.id]);
            return res.send('Usuário deletado');
        } catch (error) {
            return res.status(500).send('Erro interno');
        }
    });
    app.use('/api', router);
}

module.exports = registerRoutes;
