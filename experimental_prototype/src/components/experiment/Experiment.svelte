<script lang="ts">
    import {onMount, createEventDispatcher} from 'svelte';
    import {blur} from 'svelte/transition';
    import Routie from './routie';
    import ExperimentPageComponent from './ExperimentPage.svelte';
    import ExperimentSettingsComponent from './ExperimentSettings.svelte';
    import type {ExperimentPage} from './experiment_page';
    import type {Stream} from '@marcellejs/core';
    import ExperimentHeader from './ExperimentHeader.svelte';
    import ExperimentFooter from './ExperimentFooter.svelte';
    import ExperimentSettings from './ExperimentSettings.svelte';
    import {string2slug} from './utils';

    const dispatch = createEventDispatcher();

    export let title: string;
    export let author: string;
    export let experimentPanels: Stream<Record<string, ExperimentPage>>;
    export let settings: ExperimentSettings;
    export let currentPageSlug: Stream<string>;
    export let closable: boolean;
    export let freeNavigation: boolean; 
    export let showHeader: boolean;
    export let showFooter: boolean;

    const initialFreeNavigation = freeNavigation;

    let showApp = false;

    onMount(() => {
        showApp = true;
    });


    export function quit(): void {
        showApp = false;
        setTimeout(() => {
            dispatch('quit');
        }, 400);
    }

    let showSettings = false;
    // ! Not needed since we have the currentPage stream which contains the current page full name (uppercase and spaces)
    let currentExperiment = Object.keys(experimentPanels.get())[0] || undefined; // Same format as page names (uppercase and spaces)
    // console.log(currentExperiment);

  $: experimentNames = Object.keys(experimentPanels.get()); // Same format as page names (uppercase and spaces)
  $: experimentSlugs = [''].concat(experimentNames.slice(1).map(string2slug));
  

  // Routing
  onMount(() => {
    try {
        const router = new Routie();
        router.route('settings', () => {
            freeNavigation = true;
            showSettings = true;
            if (currentExperiment) experimentPanels.get()[currentExperiment].destroy();
            currentPageSlug.set('settings');
        });
        experimentSlugs.forEach((slug, i) => {
          router.route(slug, () => {
            freeNavigation = initialFreeNavigation;
            showSettings = false;
            if (currentExperiment === experimentNames[i]){
              return;
            }
            if (currentExperiment) {
              experimentPanels.get()[currentExperiment].destroy();
            } 
            currentExperiment = experimentNames[i];

            currentPageSlug.set(slug === '' ? string2slug(experimentNames[0]) : slug);
        });
      });
    } catch (error) {
        // eslint-disable-next-line no-console
        console.error('Could not enable router', error);
    }
    });
</script>

<svelte:head>
  <title>{title}</title>
</svelte:head>


{#if showApp}
  <div
    class="marcelle fixed h-screen w-full max-w-full overflow-y-scroll overflow-x-hidden top-0 left-0 z-50"
  >
    <div class="app-container" transition:blur={{ amount: 10, duration: closable ? 400 : 0 }}>
      {#if showHeader}
        <ExperimentHeader
          {title}
          items={experimentSlugs.reduce((o, x, i) => ({ ...o, [x]: experimentNames[i] }), {})}
          current={currentExperiment}
          {showSettings}
          {closable}
          {freeNavigation}
          on:quit={quit}
          on:requestFullscreen={() => dispatch('requestFullscreen')}
        />
      {/if}

      <main class="main-container">
        {#if showSettings}
          <ExperimentSettingsComponent {settings} />
        {:else if currentExperiment}
          <ExperimentPageComponent experimentPage={experimentPanels.get()[currentExperiment]} />
        {/if}
      </main>
        
      {#if showFooter}
        <ExperimentFooter {author} />
      {/if}
    </div>
  </div>
{/if}

<style lang="postcss">
  .app-container {
    @apply flex flex-col absolute top-0 left-0 w-full min-h-screen z-10;
  }

  .main-container {
    @apply box-border w-full p-1 flex flex-col flex-nowrap grow bg-gray-100;
    background-color: rgb(237, 242, 247);
  }

  @screen lg {
    .main-container {
      @apply flex-row;
    }
  }
</style>
