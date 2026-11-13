function createReportController(reportService) {
    return async (req, res) => {
        try {
            return res.json(await reportService.financialReport());
        } catch (error) {
            console.error('Financial report failed:', error.message);
            return res.status(500).send('Erro interno');
        }
    };
}

module.exports = createReportController;
