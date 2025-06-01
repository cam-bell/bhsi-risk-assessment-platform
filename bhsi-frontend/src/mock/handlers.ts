import { rest } from 'msw';

export const handlers = [
  rest.get('/api/v1/score', (req, res, ctx) => {
    const query = req.url.searchParams.get('query');
    
    // Simulate API delay
    return res(
      ctx.delay(800),
      ctx.json({
        company: query && query.toUpperCase().includes('ACME') ? 'ACME S.A.' : `${query} S.A.`,
        vat: query && query.toUpperCase().includes('ESX') ? query : 'ESX1234567',
        overall: 'orange',
        blocks: {
          turnover: 'green',
          shareholding: 'orange',
          bankruptcy: 'green',
          legal: 'red'
        }
      })
    );
  }),
];