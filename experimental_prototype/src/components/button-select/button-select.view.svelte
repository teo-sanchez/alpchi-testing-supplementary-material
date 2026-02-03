<script lang="ts">
  import { Stream } from '@marcellejs/core';
  import { ViewContainer } from '@marcellejs/design-system';
  import { Button } from '@marcellejs/design-system';
  import { ButtonSelectOptions } from './button-select.component';

  export let title: string;
  export let options: Stream<ButtonSelectOptions>;

  export let items: Stream<string[]>;

  export let click: Stream<string>;
  export let pressed: Stream<boolean[]>;
  export let loading: Stream<boolean>;
  export let disabled: Stream<boolean[]>;

  function handleClick(idx: number) {
    return (event: CustomEvent) => {
      click.set(items.get()[idx]);
    };
  }
</script>

<ViewContainer {title} loading={$loading}>
  {#if $items}
    <div class="button-container">
    {#each $items as item, idx}
      <Button
        disabled={$disabled[idx]}
        variant={options.get().variant}
        type={options.get().type}
        size={options.get().size}
        round={options.get().round}
        bind:pressed={$pressed[idx]}
        on:click={handleClick(idx)}
      >
        {item}
      </Button>
    {/each}
    </div>
  {/if}
</ViewContainer>

<style>
  .button-container {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(100px, 1fr)); /* Adjust the minmax value to fit your button size */
    gap: 10px; /* Optional: adds spacing between buttons */
  }
</style>
