require('dotenv').config();
const app = require('./src/app');

const PORT = process.env.PORT || 5000;

const server = app.listen(PORT, () => {
  console.log(`\n🚀  Blog API running in ${process.env.NODE_ENV} mode`);
  console.log(`📡  Server:  http://localhost:${PORT}`);
  console.log(`📖  Swagger: http://localhost:${PORT}/api-docs\n`);
});

// Graceful shutdown
const gracefulShutdown = (signal) => {
  console.log(`\n${signal} received – shutting down gracefully…`);
  server.close(() => {
    console.log('✅  HTTP server closed.');
    process.exit(0);
  });
};

process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
process.on('SIGINT',  () => gracefulShutdown('SIGINT'));

// Unhandled promise rejections
process.on('unhandledRejection', (err) => {
  console.error('💥  Unhandled rejection:', err.message);
  server.close(() => process.exit(1));
});
