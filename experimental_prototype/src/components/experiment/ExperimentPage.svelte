<script lang="ts">
  import { afterUpdate, onDestroy } from 'svelte';
  import type { ExperimentPage } from './experiment_page';
  export let experimentPage: ExperimentPage;
  import { onMount } from 'svelte';
  import {Button} from "@marcellejs/design-system";

  $: options = experimentPage.options;
  $: buttonDisabled = true;

  experimentPage.$buttonDisabled.subscribe(value => {
    buttonDisabled = value;
  });

  let initialTopOffset;

  onMount(() => {
    initialTopOffset = window.scrollY; // Get current scroll position
    document.documentElement.style.setProperty('--initial-top-offset', `${initialTopOffset}px`);
  });

  afterUpdate(() => {
    experimentPage.mount();
    experimentPage.$terminationDisplay.subscribe(value => {
      const terminationElement = document.querySelector('.termination-criteria');
      if (terminationElement) {
        terminationElement.textContent = value;
      }
    });
  });

  onDestroy(() => {
    experimentPage.destroy();
  });

  // Reactive statement to update CSS variables based on experimentPage options
  $: {
    const rootElement = document.documentElement; // Or use a specific element if more appropriate
    const leftRatio = options.showLeftSidebar ? options.ratioLeftSidebar : 0;
    const rightRatio = options.showRightSidebar ? options.ratioRightSidebar : 0;
    
    rootElement.style.setProperty('--ratio-left-sidebar', `${leftRatio * 100}%`);
    rootElement.style.setProperty('--ratio-right-sidebar', `${rightRatio * 100}%`);
    
    // Calculate and update the middle width dynamically
    const middleWidth = 1 - leftRatio - rightRatio;
    rootElement.style.setProperty('--middle-width', `${middleWidth * 100}%`);
  }


</script>

<div class="page-container">

  {#if options.showInstructions}
    <div class="instructions-wrapper">
      <div class="instructions-text">
        <p><b>Instructions: </b>{options.instructions}</p>
      </div>
      <div class="termination-criteria" style="font-size: 2rem;">
      </div>
    </div>
  {/if}


<div class="page-content">
{#if options.showLeftSidebar && options.ratioLeftSidebar != 0}
  <div class="left">
    {#each experimentPage.componentsLeft as m}
      {#if Array.isArray(m)}
        <div class="flex flex-row flex-wrap items-stretch">
          {#each m as { id }}
            <div {id} class="card flex-none xl:flex-1 w-full xl:w-auto" />
          {/each}
        </div>
      {:else if typeof m === 'string'}
        <h2>{m}</h2>
      {:else}
        <div id={m.id} class="card" />
      {/if}
    {/each}
  </div>
{/if}

<div class="middle">
  {#each experimentPage.components as m}
    {#if Array.isArray(m)}
      <div class="flex flex-row flex-wrap items-stretch">
        {#each m as { id }}
          <div {id} class="card flex-none xl:flex-1 w-full xl:w-auto" />
        {/each}
      </div>
    {:else if typeof m === 'string'}
      <h2>{m}</h2>
    {:else}
      <div id={m.id} class="card" />
    {/if}
  {/each}
</div>


{#if options.showRightSidebar && options.ratioRightSidebar != 0}
  <div class="right">
    {#each experimentPage.componentsRight as m}
      {#if Array.isArray(m)}
        <div class="flex flex-row flex-wrap items-stretch">
          {#each m as { id }}
            <div {id} class="card flex-none xl:flex-1 w-full xl:w-auto" />
          {/each}
        </div>
      {:else if typeof m === 'string'}
        <h2>{m}</h2>
      {:else}
        <div id={m.id} class="card" />
      {/if}
    {/each}
  </div>
{/if}
</div>
</div>

{#if (options.navigationButtons === 'both' || options.navigationButtons === 'previous') && experimentPage.previousPageSlugDefined}
    <div class="previous-phase-button">
      <Button disabled={buttonDisabled}
              type="warning"
              size="large"
              variant="light"
              on:click={() => {
                buttonDisabled = true;
                experimentPage.parentExperiment.setFullscreen(experimentPage.parentExperiment.fullscreen);
                experimentPage.$clickPrevious.set("previous");
                experimentPage.parentExperiment.goToPage(experimentPage.previousPageSlug)}
              }>
              ← Previous phase</Button>
    </div>
  {/if}

{#if options.navigationButtons !== 'none'}
  {#if (options.navigationButtons === 'both' || options.navigationButtons === 'next') && experimentPage.nextPageSlugDefined}
    <div class="next-phase-button">
      <Button disabled={buttonDisabled} 
              type="warning" 
              size="large"
              variant="light"
              on:click={() => {
                buttonDisabled = true;
                experimentPage.parentExperiment.setFullscreen(experimentPage.parentExperiment.fullscreen);
                experimentPage.$clickNext.set("next");
                experimentPage.parentExperiment.goToPage(experimentPage.nextPageSlug)}
                }>
              Next phase →</Button>
    </div>
  {/if}

  
{/if}

<style type="text/postcss">


  .page-container {
    @apply w-full;
    flex-direction: column;
    width: 100vw;
  }

  .instructions-wrapper {
    @apply bg-yellow-100 border-l-4 border-yellow-600 text-yellow-900 p-4 w-full shadow-md;
    display: flex;
    position: sticky;
    /* the exact distance between the top of the screen and the top of the instruction-wrapper bar when initialized? */
    top: calc(var(--initial-top-offset) * -1);
    z-index : 900;
  }

  .instructions-text {
    flex: 3;
    font-size: 0.875rem;
  }
  .termination-criteria {

    flex: 1;
    font-size: 0.875rem; /* Adjust font size as needed */
  }

  .instructions-text {
    @apply text-black;
  }

  .termination-criteria {
    @apply text-right text-black;
    overflow: hidden;
  }

  .instructions-bar {
    @apply bg-yellow-100 border-l-4 border-yellow-600 p-4 w-full;
  }

  .page-content {
    @apply w-full;
    display: flex;
    flex-direction: row;
  }

  .left {
    @apply shrink-0 p-1;
    width: var(--ratio-left-sidebar);
  }

  .right {
    @apply shrink-0 p-1;
    width: var(--ratio-right-sidebar);
  }

  .middle {
    @apply p-1;
    width: var(--middle-width);
  }

  h2 {
    @apply font-medium text-gray-700 ml-2 text-2xl;
  }

  .navigation-footer {
    @apply flex justify-between p-2;
    position: fixed;
    bottom: 0;
    width: 100%;
    /* transparent */
    background-image: linear-gradient(to top, rgba(255, 255, 255, 1), rgba(255, 255, 255, 0));

  }
  
  .next-phase-button {
    @apply shadow-md;
    position: fixed;
    bottom: 0.5rem;
    right: 1rem; /* Align to left edge directly */
    width: fit-content; /* Adjust width as needed */
    padding: 0; /* Add some padding (optional) */
    margin: 0;
    background-color: transparent; /* Optional background color */
    z-index: 2; /* Ensure button is above other elements */
  } 

  .previous-phase-button {
    @apply shadow-md;
    position: fixed;
    bottom: 0.5rem;
    left: 1rem; /* Align to left edge directly */
    width: fit-content; /* Adjust width as needed */
    padding: 0; /* Add some padding (optional) */
    margin: 0;
    background-color: transparent; /* Optional background color */
    z-index: 2; /* Ensure button is above other elements */
  } 

</style>
