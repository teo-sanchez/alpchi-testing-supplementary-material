import { TestCasesTable } from './test-cases-table.component';

export function testCasesTable(...args: ConstructorParameters<typeof TestCasesTable>): TestCasesTable {
  return new TestCasesTable(...args);
}

export type { TestCasesTable };
