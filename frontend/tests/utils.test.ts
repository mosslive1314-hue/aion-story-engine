import { formatNumber, formatCurrency, truncateText, generateId } from '@/lib/utils';

describe('Utility Functions', () => {
  describe('formatNumber', () => {
    test('formats small numbers correctly', () => {
      expect(formatNumber(100)).toBe('100');
      expect(formatNumber(500)).toBe('500');
      expect(formatNumber(999)).toBe('999');
    });

    test('formats thousands correctly', () => {
      expect(formatNumber(1000)).toBe('1.0K');
      expect(formatNumber(1500)).toBe('1.5K');
      expect(formatNumber(9999)).toBe('10.0K');
    });

    test('formats millions correctly', () => {
      expect(formatNumber(1000000)).toBe('1.0M');
      expect(formatNumber(1500000)).toBe('1.5M');
      expect(formatNumber(9999999)).toBe('10.0M');
    });
  });

  describe('formatCurrency', () => {
    test('formats numbers as currency', () => {
      expect(formatCurrency(0)).toContain('$0.00');
      expect(formatCurrency(10.5)).toContain('$10.50');
      expect(formatCurrency(100)).toContain('$100.00');
      expect(formatCurrency(999.99)).toContain('$999.99');
    });
  });

  describe('truncateText', () => {
    test('returns original text if shorter than maxLength', () => {
      expect(truncateText('Short text', 20)).toBe('Short text');
      expect(truncateText('Exact', 5)).toBe('Exact');
    });

    test('truncates text longer than maxLength', () => {
      expect(truncateText('This is a long text', 10)).toBe('This is a ...');
      expect(truncateText('Another long text here', 15)).toBe('Another long tex...');
    });

    test('handles empty strings', () => {
      expect(truncateText('', 10)).toBe('');
    });

    test('handles maxLength of 0', () => {
      expect(truncateText('Any text', 0)).toBe('...');
    });
  });

  describe('generateId', () => {
    test('generates a string', () => {
      const id = generateId();
      expect(typeof id).toBe('string');
      expect(id.length).toBeGreaterThan(0);
    });

    test('generates unique IDs', () => {
      const id1 = generateId();
      const id2 = generateId();
      expect(id1).not.toBe(id2);
    });

    test('generates IDs with expected format', () => {
      const id = generateId();
      expect(id).toMatch(/^[a-z0-9]+$/);
    });
  });
});
