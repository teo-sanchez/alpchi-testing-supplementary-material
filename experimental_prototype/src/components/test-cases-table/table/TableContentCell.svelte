<script lang="ts">
  import { formatDistanceToNow } from 'date-fns';
  import { createEventDispatcher } from 'svelte';
  import { Button } from '@marcellejs/design-system';
  import type { Column } from '@marcellejs/design-system';

  export let type: Column['type'] = 'generic';
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  export let name: string;
  export let value: any = null;

  const dispatch = createEventDispatcher();

  function getArrayShape(arr: unknown[]): number[] {
    if (!Array.isArray(arr)) return [];
    if (arr.length > 0 && Array.isArray(arr[0])) {
      return [arr.length, ...getArrayShape(arr[0])];
    }
    return [arr.length];
  }

  function formatDate(v: string) {
    try {
      return formatDistanceToNow(Date.parse(v), { includeSeconds: true, addSuffix: true });
    } catch (error) {
      // eslint-disable-next-line no-console
      console.log('Date Parsing Error', v, error);
      return v;
    }
  }
</script>

<td class="text-center" class:wrap-text={name === "Label" || name === "Predicted label"}>
  {#if type === 'image'}
    <img alt="thumbnail" src={value} width="150" height="150" style="max-width: 100%; max-height: 100%;"/>
  {:else if type === 'link'}
    <!-- svelte-ignore a11y-click-events-have-key-events -->
    <sl-button
      type="text"
      size="small"
      on:click={() => {
        // eslint-disable-next-line no-console
        console.log('GOTO:', value.href);
      }}>{value.text}</sl-button
    >
  {:else if type === 'action'}
    <Button size="small" on:click={() => dispatch('action', value)}>{value}</Button>
  {:else if type === 'slot'}
    <slot />
  {:else if type === 'date'}
    {formatDate(value)}
  {:else if type === 'array'}
    Array({getArrayShape(value).join(', ')})
  {:else if typeof value === 'number'}
    {value}
  {:else}
    {value}
  {/if}
</td>

<style>
  td {
    white-space: nowrap;
    padding-left: 0.5rem;
    padding-right: 0.5rem;
    padding-top: 0.25rem;
    padding-bottom: 0.25rem;
  }

  .wrap-text {
    white-space: normal; /* Allows text wrapping */
    word-wrap: break-word; /* Allows breaking long words */
    overflow-wrap: break-word; /* Ensures proper wrapping in most browsers */
    max-width: 50px; /* Adjust as necessary to limit cell width */
  }

</style>
