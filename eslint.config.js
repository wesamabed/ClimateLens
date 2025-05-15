import tseslint from 'typescript-eslint';
import eslintPluginImport from 'eslint-plugin-import';
import eslintPluginNode from 'eslint-plugin-n';
import eslintPluginPromise from 'eslint-plugin-promise';

/** @type {import('eslint').Linter.FlatConfig[]} */
export default [
  // base eslint rules
  {
    files: ['**/*.{js,cjs,mjs,ts,tsx}'],
    languageOptions: {
      sourceType: 'module',
      parserOptions: {
        project: ['./server/tsconfig.json', './client/tsconfig.json'],
      },
    },
    rules: {
      'no-unused-vars': 'error',
      'no-undef': 'error',
    },
  },
  // TypeScript rules
  ...tseslint.configs.recommended,
  {
    files: ['**/*.ts', '**/*.tsx'],
    plugins: {
      '@typescript-eslint': tseslint.plugin,
    },
    rules: {
      '@typescript-eslint/consistent-type-imports': 'error',
    },
  },
  // Import / Node / Promise rules
  eslintPluginImport.configs.recommended,
  eslintPluginNode.configs['flat/recommended'],
  eslintPluginPromise.configs.recommended,
];
