// server/src/infrastructure/ai/embedding.client.ts

import { GoogleGenAI } from '@google/genai';
import { config } from '../../core/config.factory';

/**
 * EmbeddingClient: calls GenAI embedContent and extracts a number[] vector
 * Handles multiple possible shapes of the SDK’s ContentEmbedding type.
 */
export class EmbeddingClient {
  private ai: GoogleGenAI;

  constructor() {
    const opts: any = {};
    if (config.GOOGLE_GENAI_USE_VERTEXAI) {
      opts.vertexai = true;
      opts.project   = config.GOOGLE_CLOUD_PROJECT;
      opts.location  = config.GOOGLE_CLOUD_LOCATION;
    } else {
      opts.apiKey = config.GEMINI_API_KEY;
    }
    this.ai = new GoogleGenAI(opts);
  }

  /** Embed text and return the raw number[] */
  async embed(text: string): Promise<number[]> {
    const resp = await this.ai.models.embedContent({
      model: config.VERTEX_EMBED_MODEL, // e.g. 'gemini-embedding-001'
      contents: text,
    });

    const embeddings = resp.embeddings;
    if (!embeddings || embeddings.length === 0) {
      throw new Error('No embeddings returned from embedContent');
    }

    const first = embeddings[0];
    let vector: number[] | undefined;

    // Case A: it's already a number[]
    if (Array.isArray(first) && typeof first[0] === 'number') {
      vector = first as number[];
    }
    // Case B: { value: number[] }
    else if (
      typeof first === 'object' &&
      first !== null &&
      'value' in first &&
      Array.isArray((first as any).value)
    ) {
      vector = (first as any).value as number[];
    }
    // Case C: { embedding: number[] }
    else if (
      typeof first === 'object' &&
      first !== null &&
      'embedding' in first &&
      Array.isArray((first as any).embedding)
    ) {
      vector = (first as any).embedding as number[];
    }
    // Case D: any other object with a numeric array property
    else if (typeof first === 'object' && first !== null) {
      for (const v of Object.values(first as any)) {
        if (Array.isArray(v) && typeof v[0] === 'number') {
          vector = v as number[];
          break;
        }
      }
    }

    if (!vector) {
      throw new Error(
        `Unexpected embedding format: ${JSON.stringify(first)}`
      );
    }
    return vector;
  }
}

export const embeddingClient = new EmbeddingClient();
