<script lang="ts">
  import type { Dataset, Instance, Stream } from '@marcellejs/core';
  import type { Column } from '@marcellejs/design-system';
  import { onMount, tick } from 'svelte';
  import { TableServiceProvider } from '@marcellejs/design-system';
  import { Spinner, ViewContainer} from '@marcellejs/design-system';
  import { Table } from './table';
  import { UserInteraction } from "./test-cases-table.component";
  // ----------------------------------------------
  // Import properties from the parent component
  // ----------------------------------------------

  export let title: string;
  export let dataset: Dataset<Instance>;
  export let columns: Column[];
  export let singleSelection: boolean;
  export let selection: Stream<Instance[]>;
  export let interactions: Stream<UserInteraction>;
  export let showTotalItems: boolean = true;

  dataset.$changes
    .filter((e) => Array.isArray(e))
    .filter((e) => e.length > 0)
    .filter((e) => e[0]["type"] !== undefined)
    .filter((e) => e[0]["type"] === "created" && e[0]["data"] !== undefined)
    .subscribe((e) => {
    handleAddTestCases(e);
  });

  let provider: TableServiceProvider;

  async function handleCheckTestCases() {
    const unlabeledTestCases = await dataset.items().filter(item => item['Pass/Fail'] === "").toArray();
    // Remove the 'thumbnail' key from each object (too large to be stored in the interaction log)
    const processedTestCases = unlabeledTestCases.map(item => {
      const { thumbnail, Embedding, ...rest } = item;
      return rest;
    });

    let msg : UserInteraction  = {
      action : "check",
      // Count empty string in dataset column 'Pass/Fail'
      numberOfItemsAffected : unlabeledTestCases.length,
      object : processedTestCases,
      timestamp : Date.now()
    }
    interactions.set(msg);
  }

  function handleAddTestCases(e: any) {
    let msg : UserInteraction  = {
      action : "add",
      object : e[0]["data"],
      timestamp : Date.now()
    }
    interactions.set(msg);
  }

  function handleSortTestCases(sorting : any) {
    let msg : UserInteraction  = {
      action : "sort",
      object : sorting.col,
      ascending : sorting.ascending,
      timestamp : Date.now()
    }
    interactions.set(msg);
  }

  function handleSelectTestCases(selected : any) {
    if (selected.length === 0) return;
    let msg : UserInteraction  = {
      action : "select",
      numberOfItemsAffected : selected.length,
      object : selected,
      timestamp : Date.now()
    }
    interactions.set(msg);
  }

  async function handleDeleteTestCases(selected : any) {
    let msg : UserInteraction  = {
      action : "remove",
      numberOfItemsAffected : selected.length,
      object : await Promise.all(selected.map(provider.get.bind(provider))),
      timestamp : Date.now()
    }
    interactions.set(msg);
  }

  onMount(async () => {
    await tick();
    await dataset.ready;
    
    provider = new TableServiceProvider({ service: dataset.instanceService, columns});
  });


</script>

<ViewContainer {title} >
  {#await dataset.ready}
    <Spinner />
  {:then}
    {#if provider}
      <Table
        {provider}
        {dataset}
        {columns}
        {singleSelection}
        {showTotalItems}
        on:checkTestCases = {handleCheckTestCases}
        on:deleted = {({detail}) => {handleDeleteTestCases(detail)}}
        on:sortChanged = {(evt) => handleSortTestCases(evt.detail)}
        on:selection={({ detail }) => {
          handleSelectTestCases(detail);
          selection.set(detail);
        }}
        actions={[{ name: 'delete', multiple: true, confirm: false}]}
      />
    {/if}
  {/await}
</ViewContainer>