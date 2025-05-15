import express, { Express } from 'express';
import helmet from 'helmet';
import cors from 'cors';
import compression from 'compression';
import rateLimit from 'express-rate-limit';
import morgan from 'morgan';
import { config } from '../../core/config.factory';
import { logger } from '../../core/logger.adapter';
import { mongoSingleton } from '../../infrastructure/database/mongo.singleton';
import { healthRouter } from './routes/health.router';
import { rootRouter } from './routes/root.router';
import { ENV } from '../../core/environments';

export async function buildExpressApp(): Promise<Express> {
  await mongoSingleton.connect(); // fail fast if DB down
  const app = express();

  /* generic middleware */
  app.use(helmet());
  app.use(cors({ origin: '*', optionsSuccessStatus: 204 }));
  app.use(compression());
  app.use(express.json({ limit: '1mb' }));
  app.use(
    rateLimit({
      windowMs: 15 * 60 * 1000,
      max: 200,
      standardHeaders: true,
    })
  );
  if (config.NODE_ENV !== ENV.Production) app.use(morgan('dev'));

  /* route composition (SRP) */
  app.use(healthRouter);
  app.use(rootRouter);

  /* central error handler placeholder */
  app.use((err: unknown, _req: any, res: any, _next: any) => {
    logger.error('Unhandled error', err);
    res.status(500).json({ error: 'Internal Server Error' });
  });

  return app;
}
