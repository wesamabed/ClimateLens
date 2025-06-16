import express from 'express';
import helmet from 'helmet';
import cors from 'cors';
import compression from 'compression';
import rateLimit from 'express-rate-limit';
import morgan from 'morgan';

import { config } from '../../core/config.factory';
import { ENV } from '../../core/environments';

import { mongoSingleton } from '../../infrastructure/database/mongo.singleton';

import { errorHandler } from './middleware/errorHandler';

import { rootRouter } from './routes/root.router';
import { healthRouter } from './routes/health.router';
import { askRouter } from './routes/ask.router';

export async function buildExpressApp() {
  await mongoSingleton.connect();

  const app = express();
  app.use(helmet());
  app.use(cors({ origin: '*' }));
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

  app.use(healthRouter, rootRouter, askRouter);
  app.use(errorHandler);

  return app;
}
