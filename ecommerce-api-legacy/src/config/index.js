const config = {
    port: Number(process.env.PORT || 3000),
    adminApiKey: process.env.ADMIN_API_KEY || '',
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || '',
    dbPath: process.env.DB_PATH || ':memory:'
};

module.exports = config;
