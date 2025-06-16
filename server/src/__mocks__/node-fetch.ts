// server/src/__mocks__/node-fetch.ts
import { RequestInfo, RequestInit, Response } from 'node-fetch';

// a no-op fetch that always rejects (or you can have it return a dummy successful Response)
export default function fetch(
  _url: RequestInfo,
  _init?: RequestInit
): Promise<Response> {
  return Promise.reject(new Error('node-fetch is mocked; you need to override in your tests'));
}
