const { createDefaultPreset } = require('ts-jest')

/** @type {import("jest").Config} **/
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/src'],
  testMatch: ['<rootDir>/src/**/?(*.)+(spec|test).ts'],
  moduleNameMapper: {
    // whenever you import 'node-fetch', Jest will substitute our mock above
    '^node-fetch$': '<rootDir>/src/__mocks__/node-fetch.ts',
    '^@google-cloud/vertexai$': '<rootDir>/tests/helpers/mockVertex.ts',
  },
  transform: {
    ...createDefaultPreset().transform,
  },
}
