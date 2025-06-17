// Flat-config for ESLint 8.57 + TypeScript-ESLint 7
import tseslint from 'typescript-eslint';
import eslintPluginImport from 'eslint-plugin-import';
import eslintPluginPromise from 'eslint-plugin-promise';

const tsParser = tseslint.parser;
const tsPlugin = tseslint.plugin;

/** @type {import('eslint').Linter.FlatConfig[]} */
export default [
  /* ── Pure JavaScript / Build files ─────────────────────────── */
  {
    files: ['**/*.{js,cjs,mjs}'],
    languageOptions: { sourceType: 'module' },
    plugins: { import: eslintPluginImport, promise: eslintPluginPromise },
    rules: {
      'import/order': 'warn',
      'promise/always-return': 'warn',
    },
  },

  /* ── Server TypeScript (type-checked) ───────────────────────── */
  {
    files: ['server/src/**/*.ts', 'server/src/**/*.tsx'],
    languageOptions: {
      parser: tsParser,
      parserOptions: {
        project: ['./server/tsconfig.json','client/tsconfig.json'],
        tsconfigRootDir: new URL('.', import.meta.url).pathname,
      },
    },
    plugins: { '@typescript-eslint': tsPlugin },
    rules: {
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
    },
  },

  /* ── Client TypeScript (type-checked) ───────────────────────── */
  {
    files: ['client/src/**/*.ts', 'client/src/**/*.tsx'],
    languageOptions: {
      parser: tsParser,
      parserOptions: {
        project: ['./client/tsconfig.eslint.json'],
        tsconfigRootDir: new URL('.', import.meta.url).pathname,
      },
    },
    plugins: { '@typescript-eslint': tsPlugin },
    rules: {
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
    },
  },
];
