import { ButtonSelect, ButtonSelectOptions } from './button-select.component';

export function buttonSelect(categories: string[], options?: Partial<ButtonSelectOptions>): ButtonSelect {
  return new ButtonSelect(categories, options);
}

export type { ButtonSelect };
