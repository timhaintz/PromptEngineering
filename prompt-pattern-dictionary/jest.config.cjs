/** @type {import('jest').Config} */
const nextJest = require('next/jest');
const createJestConfig = nextJest({
  dir: './',
});

/** @type {import('jest').Config} */
const customConfig = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/jest.setup.ts'],
  testMatch: ['**/tests/**/*.test.[jt]s?(x)'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1'
  }
};

module.exports = createJestConfig(customConfig);
