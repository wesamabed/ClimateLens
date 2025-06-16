import { EmbeddingClient } from '../infrastructure/ai/embedding.client';
import { GoogleGenAI } from '@google/genai';

jest.mock('@google/genai');
jest.mock('../core/config.factory', () => ({
  config: {
    VERTEX_EMBED_MODEL: 'dummy-model',
    GOOGLE_GENAI_USE_VERTEXAI: false,
    GEMINI_API_KEY: 'key',
    GOOGLE_CLOUD_PROJECT: '',
    GOOGLE_CLOUD_LOCATION: '',
  },
}));

describe('EmbeddingClient', () => {
  let client: EmbeddingClient;
  let mockEmbedContent: jest.Mock;

  beforeEach(() => {
    // reset the mock class
    (GoogleGenAI as jest.Mock).mockClear();

    // 1) Construct your client (this calls new GoogleGenAI(opts))
    client = new EmbeddingClient();

    // 2) Grab that single mocked instance, ensure it has a `models` map,
    //    then stub out embedContent
    const giInstance = (GoogleGenAI as jest.Mock).mock.instances[0] as any;
    if (!giInstance.models) {
      giInstance.models = {};
    }
    mockEmbedContent = (giInstance.models.embedContent = jest.fn());
  });

  it('extracts a raw number[] when embeddings is number[][]', async () => {
    mockEmbedContent.mockResolvedValue({ embeddings: [[0.1, 0.2]] });
    await expect(client.embed('foo')).resolves.toEqual([0.1, 0.2]);
  });

  it('extracts from { value: number[] }', async () => {
    mockEmbedContent.mockResolvedValue({ embeddings: [{ value: [1, 2, 3] }] });
    await expect(client.embed('foo')).resolves.toEqual([1, 2, 3]);
  });

  it('extracts from { embedding: number[] }', async () => {
    mockEmbedContent.mockResolvedValue({ embeddings: [{ embedding: [4, 5, 6] }] });
    await expect(client.embed('foo')).resolves.toEqual([4, 5, 6]);
  });

  it('extracts from any numeric‐array property', async () => {
    mockEmbedContent.mockResolvedValue({ embeddings: [{ foo: [7, 8, 9], bar: 'ignore' }] });
    await expect(client.embed('foo')).resolves.toEqual([7, 8, 9]);
  });

  it('throws if no embeddings returned', async () => {
    mockEmbedContent.mockResolvedValue({ embeddings: [] });
    await expect(client.embed('foo')).rejects.toThrow('No embeddings returned');
  });

  it('throws on unexpected format', async () => {
    mockEmbedContent.mockResolvedValue({ embeddings: [{ nothing: 'here' }] });
    await expect(client.embed('foo')).rejects.toThrow('Unexpected embedding format');
  });
});
