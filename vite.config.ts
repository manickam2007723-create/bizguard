import tailwindcss from '@tailwindcss/vite';
import react from '@vitejs/plugin-react';
import path from 'path';
import {defineConfig, Plugin} from 'vite';
import { getDemoTransactions } from './src/data/demoData';
import { generateTransactionsCSVString } from './src/utils/csv';

function exportApiPlugin(): Plugin {
  return {
    name: 'bizguard-export-api',
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        const url = req.url ? req.url.split('?')[0] : '';
        if (
          url === '/api/export/csv' ||
          url === '/api/export' ||
          url === '/export/csv' ||
          url === '/export' ||
          url === '/api/transactions/export'
        ) {
          const txs = getDemoTransactions();
          const csvData = generateTransactionsCSVString(txs);
          res.setHeader('Content-Type', 'text/csv; charset=utf-8');
          res.setHeader('Content-Disposition', 'attachment; filename="bizguard_transactions.csv"');
          res.end(csvData);
          return;
        }
        next();
      });
    },
  };
}

export default defineConfig(() => {
  return {
    plugins: [react(), tailwindcss(), exportApiPlugin()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, '.'),
      },
    },
    server: {
      // HMR is disabled in AI Studio via DISABLE_HMR env var.
      // Do not modifyâfile watching is disabled to prevent flickering during agent edits.
      hmr: process.env.DISABLE_HMR !== 'true',
      // Disable file watching when DISABLE_HMR is true to save CPU during agent edits.
      watch: process.env.DISABLE_HMR === 'true' ? null : {},
    },
  };
});
