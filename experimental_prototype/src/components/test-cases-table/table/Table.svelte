<script lang="ts">
	import type { Action, Column } from '@marcellejs/design-system';
	import type { TableDataProvider } from '@marcellejs/design-system';
	import { createEventDispatcher } from 'svelte';
	import TableContentCell from './TableContentCell.svelte';
	import TableHeaderCell from './TableHeaderCell.svelte';
	import TableHeader from './TableHeader.svelte';
	// import { get } from 'svelte/store';
	import { onMount } from 'svelte';
  import { Instance, Dataset } from '@marcellejs/core';

	export let columns: Array<Column>;
	export let dataset: Dataset<Instance>;
	export let provider: TableDataProvider;
	export let showTotalItems: boolean = true;
	export let actions: Action[] = [];
	export let selectable = true;
	export let singleSelection: boolean;
	export let selection: Array<Record<string, unknown>> = [];

	let selected: number[] = [];

	$: data = provider.data;
	$: error = provider.error;
	
	dataset.$changes.subscribe(() => {
		selected = [];
		dispatchSelection();
	});

	const dispatch = createEventDispatcher();

	let sorting = { col: 'Order', ascending: false };

	function sort({ detail }: { detail: { col: string; ascending: boolean } }) {
		sorting = detail;
		provider.sort(detail);
		dispatch('sortChanged', sorting);
	}

	onMount(() => {
		provider.paginate(Infinity);
		provider.sort(sorting);
	});

	async function dispatchSelection() {
		selection = await Promise.all(selected.map(provider.get.bind(provider)));
		dispatch('selection', selection);
	}

	// function selectAll() {
	// 	if (selected.length === get(data).length) {
	// 		selected = [];
	// 	} else {
	// 		selected = get(data).map((x, i) => i);
	// 	}
	// 	dispatchSelection();
	// }

	function selectOne(
		index: number,
		e: MouseEvent & {
			currentTarget: EventTarget & HTMLInputElement;
		}
	) {
		if (singleSelection) {
			selected = e.currentTarget.checked ? [index] : [];
		} else {
			if (e.currentTarget.checked) {
				if (!selected.includes(index)) {
					selected = [...selected, index];
				}
			} else {
				selected = selected.filter((x) => x !== index);
			}
		}
		dispatchSelection();
	}

	async function propagateAction([actionName, sel]: [string, number | number[]]) {
		console.log('propagateAction', actionName, sel);
		const s = Array.isArray(sel)
			? await Promise.all(sel.map(provider.get.bind(provider)))
			: await provider.get(sel);
		
		dispatch(actionName, s);
	}

	// function handleCheckTestCases() {
	// 	dispatch('checkTestCases', true);
	// }

</script>

{#if $error}
	<div class="service-error">
		<sl-alert type="danger" open>
			<sl-icon slot="icon" name="check2-circle" />
			<strong>Table Data Error</strong><br />
			{$error}
		</sl-alert>
	</div>
{/if}
<div class="marcelle table-container">
	<TableHeader
		{provider}
		{actions}
		{showTotalItems}
		bind:selected
		on:selected={e => dispatchSelection()}
		on:deleted
		on:checkTestCases
		on:action={({ detail }) => propagateAction(detail)
	}
	/>
	<div class="table-wrapper">
		<table>
			<thead>
				<tr>
					{#if selectable}
						<th>
							<!-- {#if !singleSelection}
								<input
									type="checkbox"
									checked={selected.length > 0 && selected.length === $data.length}
									on:click={selectAll}
								/>
							{/if} -->
						</th>
					{/if}
					{#each columns as { name, sortable }}
						<TableHeaderCell {name} {sortable} {sorting} on:sort={sort} />
					{/each}
				</tr>
			</thead>
			<tbody>
				{#each $data as item, i}
					<tr>
						{#if selectable}
							<TableContentCell type="slot" name="">
								<input
									type="checkbox"
									checked={selected.includes(i)}
									on:click={(e) => selectOne(i, e)}
								/>
							</TableContentCell>
						{/if}
						{#each columns as { type, name }}
							<TableContentCell
								{type}
								{name}
								value={item[name]}
								on:action={({ detail }) => {
									propagateAction([detail, i]);
								}}
							/>
						{/each}
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
</div>

<style>
	.table-container {
		display: flex;
		width: 100%;
		flex-direction: column;
		font-size: 0.8rem;
		border: 1px solid rgb(229, 231, 235);
		border-radius: 0.5rem;
		overflow: hidden; /* Adjusted to hide the scrollbar from the container */
	}

	.table-wrapper {
		width: 100%;
		overflow-y: auto;
		max-height: 770px; /* Set your desired max height */
	}

	table {
		width: 100%;
		border-collapse: collapse;
	}

	thead {
		position: sticky;
		top: 0;
		background-color: rgb(249, 250, 251);
		z-index: 1;
	}

	thead tr {
		width: 100%;
	}

	thead tr th {
		text-align: left;
		padding-left: 1rem;
		padding-right: 1rem;
		padding-top: 0.75rem;
		padding-bottom: 0.75rem;
		line-height: 1rem;
		font-weight: 500;
		color: rgb(107, 114, 128);
		letter-spacing: 0.05em;
	}

	tbody {
		background-color: white;
	}

	tbody > :not([hidden]) ~ :not([hidden]) {
		border-top: 1px solid rgb(229, 231, 235);
	}

	.scrollable-table {
		display: block;
		width: 100%;
	}

</style>
