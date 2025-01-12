import '@testing-library/jest-dom/extend-expect';
import { configure } from '@testing-library/react';

// Configurações globais para os testes
configure({
  testIdAttribute: 'data-testid',
});