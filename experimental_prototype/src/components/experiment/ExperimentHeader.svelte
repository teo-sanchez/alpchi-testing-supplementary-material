<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    import { Button } from '@marcellejs/design-system';  
    export let title: string;
    export let items: { [slug: string]: string };
    export let current: string;
    export let closable: boolean;
    export let showSettings : boolean = false;
    export let freeNavigation : boolean;
    
    const dispatch = createEventDispatcher();

    // ? : Is this really neeeded?
    function handleClick(event: MouseEvent, name: string): void {
      if (!freeNavigation && current !== name) {
        event.preventDefault();
      }
    }


    export function quit(): void {
      setTimeout(() => {
        dispatch('quit');
      }, 400);
    }
  </script>
  
  <header class="bg-white text-gray-700 body-font w-full">
    <div class="mx-auto flex flex-wrap flex-col md:flex-row items-stretch w-full">
      <span
        class="flex p-3 title-font font-medium items-center text-gray-900 mb-4 md:mb-0 border-solid border-0 border-r border-gray-200"
      >
        <span class="mx-3 text-lg">{title}</span>
    </span>
      <nav class="flex items-stretch justify-start flex-wrap text-base grow mx-4">
        {#each Object.entries(items) as [slug, name], index}
          <a
            href={`#${slug}`}
            class:active={!showSettings && current === name}
            class:disabled-link={!freeNavigation && current !== name} 
            on:click={(event) => {
              dispatch("requestFullscreen");
              handleClick(event, name)
              }
            }
            class="ml-2 mr-5 flex items-center hover:text-black border-solid border-0 border-b-2 border-transparent"
          >
            {name}
          </a>
          {#if index < Object.entries(items).length - 1}
            <span class="ml-2 mr-5 flex items-center border-solid border-0 border-b-2 border-transparent">→</span> <!-- Arrow icon -->
          {/if}
        {/each}
      </nav>
      <div class="flex items-center">
        <!-- Deleted setting button -->
        <span class="w-1" />
        {#if closable}
          <Button round type="danger" on:click={quit}>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="feather feather-power"
              ><path d="M18.36 6.64a9 9 0 1 1-12.73 0" /><line x1="12" y1="2" x2="12" y2="12" /></svg
            >
          </Button>
          <span class="w-1" />
        {/if}
      </div>
    </div>
  </header>
  
  <style lang="postcss">
    a {
      color: inherit;
      text-decoration: inherit;
    }
  
    .active {
      @apply text-gray-900 border-yellow-500;
    }

    .disabled-link {
      color: lightgrey;
      pointer-events: none; /* Prevents clicking */
    }

  </style>
  