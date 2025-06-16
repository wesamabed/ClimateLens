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
  VERTEX_PROJECT: z.string().default('climatelens-dev'),
  VERTEX_REGION: z.string().default('us-central1'),
  VERTEX_MODEL: z.string().default('gemini-embedding-001'),
  VERTEX_EMBED_MODEL: z.string().default('gemini-embedding-001'),
  VERTEX_LLM_MODEL: z.string().default('gemini-2.0-flash'),
  GEMINI_API_KEY: z.string().optional(),
  GOOGLE_GENAI_USE_VERTEXAI: z
    .string()
    .default('true')
    .transform((v) => v.toLowerCase() === 'true'),
  GOOGLE_CLOUD_PROJECT: z.string().default('climatelens-dev'),
  GOOGLE_CLOUD_LOCATION: z.string().default('us-central1'),
  CACHE_TTL_SECONDS: z
    .string()
    .default('3600')
    .transform(Number)
    .refine((n) => n >= 0, 'CACHE_TTL_SECONDS must be non-negative'),
});

export const config = Schema.parse(process.env) as {
  MONGODB_URI: string;
  DB_NAME:     string;
  PORT:        number;
  NODE_ENV:    EnvName;
  VERTEX_PROJECT: string;
  VERTEX_REGION: string;
  VERTEX_MODEL: string;
  VERTEX_EMBED_MODEL: string;
  VERTEX_LLM_MODEL: string;
  GEMINI_API_KEY?: string;
  GOOGLE_GENAI_USE_VERTEXAI: boolean;
  GOOGLE_CLOUD_PROJECT: string;
  GOOGLE_CLOUD_LOCATION: string;
  CACHE_TTL_SECONDS: number;
};
