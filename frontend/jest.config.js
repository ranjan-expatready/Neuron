const nextJest = require("next/jest");

const createJestConfig = nextJest({
  dir: "./",
});

/** @type {import('jest').Config} */
const customJestConfig = {
  setupFilesAfterEnv: ["<rootDir>/setupTests.ts"],
  testEnvironment: "jest-environment-jsdom",
  moduleNameMapper: {
    "^@/(.*)$": "<rootDir>/frontend/src/$1",
  },
  testMatch: ["**/frontend/tests/**/*.(test|spec).(ts|tsx)"],
};

module.exports = createJestConfig(customJestConfig);

