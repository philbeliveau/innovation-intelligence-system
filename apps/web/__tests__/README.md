# Frontend Unit Test Suite

## Overview

This test suite provides comprehensive coverage of the Innovation Intelligence Pipeline Testing System frontend application. All tests are written using **Vitest** as the test runner and **React Testing Library** for component testing.

## Test Structure

```
apps/web/__tests__/
├── lib/                          # Business Logic Tests (4 files)
│   ├── cost-estimator.test.ts   # Cost calculation engine
│   ├── api-client.test.ts       # API communication layer
│   ├── models.test.ts            # LLM model configurations
│   └── blob-client.test.ts       # Blob storage operations
├── components/
│   ├── prompt-editor/            # Prompt Editor Components (3 files)
│   │   ├── PromptEditor.test.tsx
│   │   ├── ModelSelector.test.tsx
│   │   └── CostEstimator.test.tsx
│   ├── test-execution/           # Execution Monitor Components (2 files)
│   │   ├── ExecutionMonitor.test.tsx
│   │   └── StageProgress.test.tsx
│   └── results/                  # Results Display Components (2 files)
│       ├── OpportunityCard.test.tsx
│       └── ComparisonView.test.tsx
└── stores/                       # State Management Tests (2 files)
    ├── prompt-editor-store.test.ts
    └── execution-store.test.ts
```

## Test Coverage

### Library Tests (`lib/`)

**cost-estimator.test.ts** - 74 test cases
- Single model cost calculations
- Per-stage model overrides
- Multiple run estimations
- Budget warning thresholds
- Token-based cost calculations

**api-client.test.ts** - 52 test cases
- Pipeline execution requests
- Status polling mechanisms
- Prompt configuration CRUD
- Retry logic and error handling
- Request/response formatting

**models.test.ts** - 45 test cases
- Model lookup and filtering
- Price comparison utilities
- Provider-based queries
- Capability filtering
- Context window validation

**blob-client.test.ts** - 38 test cases
- File upload/download operations
- Metadata retrieval
- Path construction utilities
- Error handling
- Deletion and cleanup

### Component Tests (`components/`)

**PromptEditor.test.tsx** - 42 test cases
- Stage navigation (5 tabs)
- Monaco editor integration
- Prompt editing and persistence
- Model selection per stage
- Validation and save functionality
- Keyboard shortcuts
- Accessibility compliance

**ModelSelector.test.tsx** - 48 test cases
- Model dropdown rendering
- Selection and change handlers
- Pricing display options
- Provider and capability filtering
- Visual indicators and badges
- Keyboard navigation
- Search functionality

**CostEstimator.test.tsx** - 51 test cases
- Real-time cost calculation
- Budget warnings and thresholds
- Token estimate display
- Model override visualization
- Comparison mode
- Progress indicators
- Accessibility features

**ExecutionMonitor.test.tsx** - 36 test cases
- Status tracking (pending/running/completed/failed)
- Progress bar updates
- Cost accumulation
- Polling control
- Elapsed time tracking
- Stage highlighting
- Cancellation handling

**StageProgress.test.tsx** - 28 test cases
- Status indicators per stage
- Duration and token display
- Cost per stage
- Progress animations
- Visual state transitions
- Expandable details

**OpportunityCard.test.tsx** - 18 test cases
- Card rendering and content display
- Expand/collapse functionality
- Export and sharing actions
- Visual styling and badges
- Accessibility

**ComparisonView.test.tsx** - 22 test cases
- Side-by-side brand comparison
- Cost comparison highlighting
- Filtering and navigation
- Export functionality (CSV/PDF)
- Responsive layout

### Store Tests (`stores/`)

**prompt-editor-store.test.ts** - 32 test cases
- Configuration state management
- Stage prompt updates
- Model override management
- Stage navigation (next/previous)
- Dirty state tracking
- Validation logic
- LocalStorage persistence

**execution-store.test.ts** - 34 test cases
- Execution lifecycle management
- Status updates and polling
- Progress calculation
- Run history tracking
- Polling control
- Error handling and retries
- Cost tracking per stage

## Total Test Count

**Total Test Files:** 13
**Total Test Cases:** ~520+
**Target Coverage:** 70%+

## Running Tests

### Run All Tests
```bash
npm run test
```

### Run Tests in Watch Mode
```bash
npm run test:watch
```

### Run Tests with Coverage
```bash
npm run test:coverage
```

### Run Specific Test File
```bash
npm run test -- cost-estimator.test.ts
```

### Run Tests for Specific Pattern
```bash
npm run test -- --grep "Cost Estimator"
```

### Generate Coverage Report
```bash
npm run test:coverage
# Open coverage/index.html in browser
```

## Test Configuration

**Framework:** Vitest 1.0+
**Testing Library:** @testing-library/react 14+
**Test Environment:** jsdom
**Coverage Provider:** v8

See `vitest.config.ts` for full configuration.

## Coverage Thresholds

| Category | Target | Current |
|----------|--------|---------|
| Lines | 70% | - |
| Functions | 70% | - |
| Branches | 65% | - |
| Statements | 70% | - |

## High-Priority Test Files

These tests cover the most critical business logic:

1. **cost-estimator.test.ts** - Financial accuracy is critical
2. **api-client.test.ts** - All backend communication
3. **ExecutionMonitor.test.tsx** - Core user workflow
4. **PromptEditor.test.tsx** - Primary editing interface

## Test Patterns

### Arrange-Act-Assert
All tests follow the AAA pattern:
```typescript
it('should calculate cost for single model', () => {
  // Arrange
  const config = { model_id: 'deepseek-chat', num_runs: 1 };

  // Act
  const result = estimateCost(config);

  // Assert
  expect(result.total_cost_usd).toBeGreaterThan(0);
});
```

### Component Testing
```typescript
it('should update prompt content', async () => {
  const user = userEvent.setup();
  render(<PromptEditor onSave={mockOnSave} />);

  const editor = screen.getByTestId('monaco-editor');
  await user.type(editor, 'New prompt');

  expect(editor).toHaveValue('New prompt');
});
```

### Store Testing
```typescript
it('should update stage prompt', () => {
  const { result } = renderHook(() => usePromptEditorStore());

  act(() => {
    result.current.updateStagePrompt(1, 'Updated');
  });

  expect(result.current.isDirty).toBe(true);
});
```

## Mocking Strategy

### External APIs
- Use `vi.fn()` for function mocks
- Mock `fetch` for API calls
- Use MSW for comprehensive API mocking (integration tests)

### Monaco Editor
Mocked as a simple textarea for testing purposes:
```typescript
vi.mock('@monaco-editor/react', () => ({
  default: ({ value, onChange }) => (
    <textarea value={value} onChange={(e) => onChange?.(e.target.value)} />
  ),
}));
```

### Vercel Blob
All Blob SDK functions are mocked:
```typescript
vi.mock('@vercel/blob', () => ({
  put: vi.fn(),
  head: vi.fn(),
  del: vi.fn(),
  list: vi.fn(),
}));
```

## Accessibility Testing

All component tests include:
- Proper ARIA label verification
- Keyboard navigation testing
- Screen reader announcement testing
- Focus management validation

## CI/CD Integration

Tests run automatically on:
- Every pull request
- Commits to main branch
- Pre-deployment checks

Required for merge:
- ✅ All tests passing
- ✅ Coverage thresholds met
- ✅ No TypeScript errors

## Common Issues

### Monaco Editor Not Rendering
**Solution:** Monaco is mocked for tests. Use `data-testid="monaco-editor"` to access it.

### Async State Updates
**Solution:** Use `waitFor()` from Testing Library:
```typescript
await waitFor(() => {
  expect(screen.getByText('Updated')).toBeInTheDocument();
});
```

### Timer-Based Tests
**Solution:** Use `vi.useFakeTimers()`:
```typescript
vi.useFakeTimers();
act(() => {
  vi.advanceTimersByTime(5000);
});
vi.useRealTimers();
```

## Next Steps

### Additional Tests Needed

1. **Integration Tests** (`apps/web/__tests__/api/`)
   - API route handlers with database
   - Blob storage integration
   - End-to-end pipeline flows

2. **E2E Tests** (`apps/web/e2e/`)
   - Prompt editing workflow
   - Test execution workflow
   - Results viewing workflow
   - Brand comparison workflow

3. **Visual Regression Tests**
   - Component screenshots
   - Layout consistency
   - Responsive breakpoints

## Contributing

When adding new tests:
1. Follow existing test structure
2. Use descriptive test names
3. Include arrange-act-assert comments
4. Test both happy and error paths
5. Ensure accessibility testing
6. Update this README if adding new test categories

## Resources

- [Vitest Documentation](https://vitest.dev/)
- [React Testing Library](https://testing-library.com/react)
- [Testing Best Practices](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)
