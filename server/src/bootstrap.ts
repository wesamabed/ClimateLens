import { buildExpressApp } from './interfaces/http/express.server';
import { config }          from './core/config.factory';
import { logger }          from './core/logger.adapter';
import { mongoSingleton }  from './infrastructure/database/mongo.singleton';

async function start() {
  const app = await buildExpressApp();
  const srv = app.listen(config.PORT, () =>
    logger.info(`API  http://localhost:${config.PORT}`)
  );

  const shutdown = async () => {
    logger.info('SIGTERM received – shutting down');
    srv.close(async () => {
      await mongoSingleton.close();
      logger.info('Shutdown complete');
      process.exit(0);
    });
  };
  process.on('SIGTERM', shutdown);
  process.on('SIGINT',  shutdown);
}

if (require.main === module) {
  start().catch((e: unknown) => {
    logger.error('Startup failure', e);
    process.exit(1);
  });
}

export { start };    // CommonJS will compile this to module.exports.start
