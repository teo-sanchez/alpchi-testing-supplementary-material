<script lang="ts">
  import type { Action } from '@marcellejs/design-system';
  import type { TableDataProvider } from '@marcellejs/design-system';
  import { createEventDispatcher } from 'svelte';
  import { Button } from '@marcellejs/design-system';
  import { Modal }  from '@marcellejs/design-system';
  import { get } from 'svelte/store';
  // import { Instance } from '@marcellejs/core';

  export let provider: TableDataProvider;
  export let actions: Action[];
  export let selected: number[];
  // export let selectedInstances: Instance[];

  const dispatch = createEventDispatcher();

  let selectedAction = '';
  let confirmActionPending = false;

  async function confirmAction() {
    if (selectedAction === 'delete') {
      // Sort the selected array in descending order to avoid deleting instances whose index might have shifted
      const sortedSelected = selected.slice().sort((a, b) => b - a);
      for (const i of sortedSelected) {
        if (i >= 0 && i < get(provider.total)) {
          await provider.delete(i); // delete item in provider
        } else {
          console.error('Invalid index', i);
        }
      }
      // After deletion, update the selected array
      selected = selected.filter((x) => sortedSelected.indexOf(x) === -1);;
      dispatch('deleted', sortedSelected);
    } else {
      dispatch('action', [selectedAction, selected]);
    }
    confirmActionPending = false;
    dispatch('selected', selected);
  }

  function handleAction(action: string, confirm: boolean) {
    selectedAction = action;
    if (!selectedAction || selected.length === 0) return;
    if (confirm) {
      confirmActionPending = true;
    } else {
      confirmAction();
    }
  }
</script>

<!-- <div class="table-actions"> -->
<div class="actions">
  {#each actions as { name, multiple, confirm }}
    <Button
      size="medium"
      disabled={multiple === false && selected.length > 1}
      type={name === 'delete' ? 'danger' : 'default'}
      on:click={() => handleAction(name, confirm)}>{name}</Button
    >
  {/each}
</div>
<!-- </div> -->

{#if confirmActionPending}
  <Modal>
    <div class="p-8">
      <p>Do you want to {selectedAction} the selected items?</p>
      <div class="w-full flex justify-end">
        <Button
          type="danger"
          on:click={() => {
            confirmActionPending = false;
          }}>Cancel</Button
        >
        <span class="w-2" />
        <Button variant="filled" on:click={confirmAction}>Confirm</Button>
      </div>
    </div>
  </Modal>
{/if}
