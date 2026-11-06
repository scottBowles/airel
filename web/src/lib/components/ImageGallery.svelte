<script lang="ts">
	import { env } from '$env/dynamic/public';
	import { graphql } from '$houdini';
	import { toast } from 'svelte-sonner';
	import { dndzone } from 'svelte-dnd-action';
	import { getUserContext } from '$lib/auth';
	import ImageIcon from '@lucide/svelte/icons/image';
	import Plus from '@lucide/svelte/icons/plus';
	import GripVertical from '@lucide/svelte/icons/grip-vertical';
	import Trash2 from '@lucide/svelte/icons/trash-2';
	import CloudinaryImage from '$lib/components/CloudinaryImage.svelte';
	import Panel from '$lib/components/Panel.svelte';
	import Button from '$lib/components/Button.svelte';
	import ConfirmDialog from '$lib/components/ConfirmDialog.svelte';

	let {
		entityId,
		imageIds = [],
		name = '',
	}: {
		entityId: string;
		imageIds: string[];
		name?: string;
	} = $props();

	const getUser = getUserContext();
	let isStaff = $derived(!!getUser()?.isStaff);

	let confirmDeleteId = $state<string | null>(null);

	const addImageMutation = graphql(`
		mutation EntityAddImage($input: EntityAddImageInput!) {
			entityAddImage(input: $input) {
				... on Artifact { id imageIds }
				... on Association { id imageIds }
				... on Character { id imageIds }
				... on Item { id imageIds }
				... on Place { id imageIds }
				... on Race { id imageIds }
			}
		}
	`);

	const setImageIdsMutation = graphql(`
		mutation EntitySetImageIds($input: EntitySetImageIdsInput!) {
			entitySetImageIds(input: $input) {
				... on Artifact { id imageIds }
				... on Association { id imageIds }
				... on Character { id imageIds }
				... on Item { id imageIds }
				... on Place { id imageIds }
				... on Race { id imageIds }
			}
		}
	`);

	// Local mutable copy for svelte-dnd-action — $derived is read-only and breaks drag
	// oxlint-disable-next-line svelte/prefer-writable-derived
	let localItems = $state<Array<{ id: string }>>([]);

	$effect(() => {
		localItems = imageIds.map((imgId) => ({ id: imgId }));
	});

	function openUploadWidget() {
		if (!window.cloudinary) {
			toast.error('Upload widget not loaded');
			return;
		}
		const widget = window.cloudinary.createUploadWidget(
			{
				cloudName: env.PUBLIC_CLOUDINARY_CLOUD_NAME,
				uploadPreset: env.PUBLIC_CLOUDINARY_UPLOAD_PRESET,
				multiple: true,
				sources: ['local', 'url', 'camera'],
			},
			async (error: unknown, result: CloudinaryUploadResult) => {
				if (error) {
					toast.error('Upload failed');
					return;
				}
				if (result.event === 'success') {
					try {
						const res = await addImageMutation.mutate({
							input: { id: entityId, imageId: result.info.public_id },
						});
						if (res.errors?.length) {
							toast.error(res.errors[0].message);
						}
					} catch {
						toast.error('Failed to save image');
					}
				}
			},
		);
		widget.open();
	}

	async function removeImage(imgId: string) {
		const newIds = imageIds.filter((id) => id !== imgId);
		try {
			const result = await setImageIdsMutation.mutate({
				input: { id: entityId, imageIds: newIds },
			});
			if (result.errors?.length) {
				toast.error(result.errors[0].message);
			}
		} catch {
			toast.error('Failed to remove image');
		}
	}

	function handleConsider(e: CustomEvent<{ items: Array<{ id: string }> }>) {
		localItems = e.detail.items;
	}

	async function handleFinalize(e: CustomEvent<{ items: Array<{ id: string }> }>) {
		localItems = e.detail.items;
		const newOrder = e.detail.items.map((item) => item.id);
		if (newOrder.join(',') !== imageIds.join(',')) {
			try {
				const result = await setImageIdsMutation.mutate({
					input: { id: entityId, imageIds: newOrder },
				});
				if (result.errors?.length) {
					localItems = imageIds.map((imgId) => ({ id: imgId }));
					toast.error(result.errors[0].message);
				}
			} catch {
				localItems = imageIds.map((imgId) => ({ id: imgId }));
				toast.error('Failed to reorder images');
			}
		}
	}
</script>

<ConfirmDialog
	open={!!confirmDeleteId}
	title="Remove Image"
	message="Remove this image from the entity?"
	confirmLabel="Remove"
	onconfirm={() => { if (confirmDeleteId) removeImage(confirmDeleteId); confirmDeleteId = null; }}
	oncancel={() => { confirmDeleteId = null; }}
/>

<Panel>
	<div class="mb-2 flex items-center justify-between">
		<h2 class="title-section flex items-center gap-2">
			<ImageIcon class="h-3 w-3 text-text-muted" />
			Images
		</h2>
		{#if isStaff}
			<Button size="sm" onclick={openUploadWidget}>
				<Plus class="mr-1 h-3 w-3" />
				Add Image
			</Button>
		{/if}
	</div>

	{#if localItems.length > 0}
		{#if isStaff}
			<div
				class="grid grid-cols-2 gap-1 sm:grid-cols-3"
				use:dndzone={{ items: localItems, flipDurationMs: 200 }}
				onconsider={handleConsider}
				onfinalize={handleFinalize}
			>
				{#each localItems as item (item.id)}
					<div class="group relative">
						<div class="absolute left-1 top-1 z-10 cursor-grab opacity-0 transition-opacity group-hover:opacity-100">
							<GripVertical class="h-4 w-4 text-white drop-shadow-lg" />
						</div>
						<button
							onclick={() => { confirmDeleteId = item.id; }}
							class="absolute right-1 top-1 z-10 cursor-pointer border border-border-dim bg-void/80 p-0.5 text-accent-red opacity-0 transition-opacity hover:bg-accent-red hover:text-white group-hover:opacity-100"
						>
							<Trash2 class="h-3 w-3" />
						</button>
						<CloudinaryImage
							imageId={item.id}
							alt={name}
							width={400}
							crop="fit"
							class="w-full"
						/>
					</div>
				{/each}
			</div>
		{:else}
			<div class="grid grid-cols-2 gap-1 sm:grid-cols-3">
				{#each localItems as item (item.id)}
					<CloudinaryImage
						imageId={item.id}
						alt={name}
						width={400}
						crop="fit"
						class="w-full"
					/>
				{/each}
			</div>
		{/if}
	{:else}
		<p class="py-4 text-center text-[10px] text-text-muted">No images</p>
	{/if}
</Panel>
