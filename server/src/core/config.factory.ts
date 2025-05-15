import path from 'path';
import dotenv from 'dotenv';
import { z } from 'zod';
import { ENV, EnvName } from './environments';

/* Load correct .env file --------------------------------------------------- */
const envFile =
  process.env.NODE_ENV === ENV.Test
    ? path.resolve(__dirname, '../../.env.test')
    : path.resolve(__dirname, '../../.env');
dotenv.config({ path: envFile });

/* Validate ----------------------------------------------------------------- */
const Schema = z.object({
  MONGODB_URI: z.string().url(),
  DB_NAME:     z.string().default('climate'),
  PORT:        z
    .string()
    .default('3000')
    .transform(Number)
    .refine((n) => n > 0 && Number.isFinite(n), 'PORT must be positive'),
  NODE_ENV:    z.enum([ENV.Development, ENV.Production, ENV.Test]).default(
    ENV.Development
  ),
});

export const config = Schema.parse(process.env) as {
  MONGODB_URI: string;
  DB_NAME:     string;
  PORT:        number;
  NODE_ENV:    EnvName;
};
