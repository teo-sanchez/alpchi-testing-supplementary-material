<script lang="ts">
	import type { Action } from '@marcellejs/design-system';
	import type { TableDataProvider } from '@marcellejs/design-system';
	import TableActions from './TableActions.svelte';
	import { Button } from '@marcellejs/design-system';
	import { createEventDispatcher } from 'svelte';

	export let provider: TableDataProvider;
	export let actions: Action[];
	export let selected: number[];
	export let showTotalItems: boolean = true;

	const dispatch = createEventDispatcher();

	let page = 1;
	let start = 0;
	let end = 0;
	let total = 0;
	let unsub = () => {};

	$: {
		unsub();
		unsub = provider.total.subscribe((t) => {
			if (t === undefined || t === 0) {
				start = 0;
				end = 0;
				total = 0;
			} else {
				start = 1;
				end = t;
				total = t;
			}
		});
	}

	function handleCheckTestCases() {
		dispatch('checkTestCases', true);
	}

	// function handleAction(e : any) {
	// }

	// Function to fetch all items (no pagination)
	function fetchAllItems(): void {
		provider.paginate(Infinity);
		page = 1;
	}

	fetchAllItems();

</script>

<div class="table-header">
	<div class="w-full text-center">
		<Button 
			type="default"
			variant="light"
			disabled={false}
			on:click={handleCheckTestCases}
		>
		<span class="text-lg">
		Check test cases
		</span>
		</Button>
	</div>
	<div class="flex justify-between items-center w-full">
		<div class="actions flex items-center">
			{#if actions.length > 0 && selected.length > 0}
				<TableActions 
					{provider} 
					{actions} 
					bind:selected 
					on:selected={e => dispatch('selected', e.detail)}
					on:deleted
					on:action/>
			{/if}
		</div>
		{#if showTotalItems}
			<div class="flex items-center text-lg">
				Total items: {total}
			</div>
		{/if}
	</div>
</div>

<style>
	.table-header {
		display: flex;
		flex-direction: column;
		align-items: center;
		padding-left: 0.5rem;
		padding-right: 0.5rem;
		padding-top: 0.75rem;
		padding-bottom: 0.75rem;
		border-top: 1px solid rgb(229, 231, 235);
	}
	.actions {
		justify-content: flex-start;
	}

	.text-lg {
		justify-content: flex-end
	}
</style>
