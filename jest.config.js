module.exports = {
    testMatch: [
        '**/*.test.js'
    ],
    testPathIgnorePatterns: [
        'node_modules',
        'gulp'
    ],
    automock: true,
    globals: {
        __DEV__: true
    },
    rootDir: 'response_operations_ui'
};
