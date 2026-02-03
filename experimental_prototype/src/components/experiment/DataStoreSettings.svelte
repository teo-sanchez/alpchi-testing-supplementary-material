<script lang="ts">
    import { ViewContainer } from '@marcellejs/design-system';
    import type { DataStore } from '@marcellejs/core';
    import { Button, Spinner } from '@marcellejs/design-system';
  
    export let dataStore: DataStore;
  
    $: services = dataStore.$services;
  
    function logout() {
      dataStore.logout();
    }
  </script>
  
  <ViewContainer title="data store ({dataStore.location})">
    {#if dataStore.requiresAuth}
      {#await dataStore.connect()}
        <Spinner />
      {:then user}
        <p class="pb-2">Hello, {user.email}</p>
        <div class="flex"><Button on:click={logout}>Log out</Button></div>
      {/await}
      <!-- {:else}
      <div>This dataStore does not require authentication</div> -->
    {/if}
    {#if $services}
      <div>This data store contains the following services:</div>
      <div class="service-list">
          {#each $services as service}
            <div class="service-item">&#8226; {service}</div>
          {/each}
      </div>
    {/if}
  </ViewContainer>
  
  <style>
    .service-list {
      margin-top: 10px; /* Example margin for spacing */
    }
    .service-item {
      margin-bottom: 5px; /* Example margin for spacing */
    }
  </style>
  