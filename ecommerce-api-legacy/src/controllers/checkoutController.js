function createCheckoutController(checkoutService) {
    return async (req, res) => {
        try {
            const result = await checkoutService.checkout({
                name: req.body.usr,
                email: req.body.eml,
                password: req.body.pwd,
                courseId: req.body.c_id,
                card: req.body.card
            });
            return res.status(result.status).json(result.body);
        } catch (error) {
            console.error('Checkout failed:', error.message);
            return res.status(500).send('Erro interno');
        }
    };
}

module.exports = createCheckoutController;
