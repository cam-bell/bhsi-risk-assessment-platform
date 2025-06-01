import { http, HttpResponse } from 'msw'
import { setupWorker } from 'msw/browser'

// Define handlers
const handlers = [
  http.get('/api/v1/score', ({ request }) => {
    const url = new URL(request.url)
    const query = url.searchParams.get('query')
    
    return HttpResponse.json({
      company: query?.toUpperCase().includes('ACME') ? 'ACME S.A.' : `${query} S.A.`,
      vat: query?.toUpperCase().includes('ESX') ? query : 'ESX1234567',
      overall: 'orange',
      blocks: {
        turnover: 'green',
        shareholding: 'orange',
        bankruptcy: 'green',
        legal: 'red'
      }
    }, { status: 200 })
  })
]

// Create and export the service worker
export const worker = setupWorker(...handlers)