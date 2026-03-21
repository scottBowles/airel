<script lang="ts">
	import { GetOrCreateGameLogStore } from '$houdini';
	import { toast } from 'svelte-sonner';

	let {
		open = false,
		onClose,
		onCreated = async () => {}
	}: {
		open?: boolean;
		onClose: () => void;
		onCreated?: (logId: string) => void | Promise<void>;
	} = $props();

	let addInput = $state('');
	let addPending = $state(false);
	let addErrorMessage = $state('');

	const createLogStore = new GetOrCreateGameLogStore();
	const focusOnAttach = ((element: HTMLElement) => {
		element.focus();
	}) satisfies import('svelte/attachments').Attachment<HTMLElement>;

	function normalizeLogUrl(rawUrl: string) {
		try {
			const url = new URL(rawUrl.trim());

			if (!['http:', 'https:'].includes(url.protocol)) {
				return null;
			}

			return url.toString();
		} catch {
			return null;
		}
	}

	function extractMutationErrorMessage(
		error: unknown,
		responseErrors?: Array<{ message: string }> | null
	): string | null {
		if (responseErrors?.[0]?.message) {
			return responseErrors[0].message;
		}

		if (error && typeof error === 'object') {
			const maybeError = error as {
				message?: string;
				errors?: Array<{ message?: string }>;
				graphQLErrors?: Array<{ message?: string }>;
				cause?: unknown;
			};

			if (maybeError.errors?.[0]?.message) {
				return maybeError.errors[0].message;
			}

			if (maybeError.graphQLErrors?.[0]?.message) {
				return maybeError.graphQLErrors[0].message;
			}

			if (maybeError.cause) {
				const causeMessage = extractMutationErrorMessage(maybeError.cause);

				if (causeMessage) {
					return causeMessage;
				}
			}

			if (typeof maybeError.message === 'string' && maybeError.message.trim()) {
				return maybeError.message;
			}
		}

		return null;
	}

	function resetForm() {
		addInput = '';
		addErrorMessage = '';
	}

	function closeModal() {
		if (addPending) return;

		resetForm();
		onClose();
	}

	async function addLog() {
		const normalizedUrl = normalizeLogUrl(addInput);

		if (!normalizedUrl) {
			addErrorMessage = 'Enter a valid Google Doc URL.';
			return;
		}

		addPending = true;
		addErrorMessage = '';

		try {
			const response = await createLogStore.mutate({
				url: normalizedUrl
			});
			const responseErrorMessage = extractMutationErrorMessage(null, response.errors);

			if (responseErrorMessage) {
				addErrorMessage = responseErrorMessage;
				toast.error(responseErrorMessage);
				return;
			}

			const payload = response.data?.getOrCreateGameLog;

			if (!payload) {
				throw new Error('No log payload returned.');
			}

			if (payload.__typename === 'OperationInfo') {
				const message = payload.messages[0]?.message ?? 'Failed to create log.';
				addErrorMessage = message;
				toast.error(message);
				return;
			}

			resetForm();
			onClose();
			toast.success(payload.title ? `Log ready: ${payload.title}` : 'Log created.');
			await onCreated(payload.id);
		} catch (error) {
			console.error('Failed to add log:', error);
			const message = extractMutationErrorMessage(error) ?? 'Failed to create log.';
			addErrorMessage = message;
			toast.error(message);
		} finally {
			addPending = false;
		}
	}

	function handleAddFormSubmit(event: SubmitEvent) {
		event.preventDefault();
		void addLog();
	}

	function handleAddFormKeydown(event: KeyboardEvent) {
		if (event.key !== 'Escape') return;

		event.preventDefault();
		closeModal();
	}
</script>

{#if open}
	<button
		type="button"
		class="fixed inset-0 z-60 bg-slate-950/80 backdrop-blur-sm"
		tabindex="-1"
		onclick={closeModal}
		aria-label="Close add log dialog"
	></button>

	<div
		role="dialog"
		aria-modal="true"
		aria-labelledby="add-log-dialog-title"
		tabindex={-1}
		onkeydown={handleAddFormKeydown}
		class="fixed inset-x-3 top-1/2 z-70 -translate-y-1/2 border border-slate-700 bg-slate-950/96 p-4 shadow-[0_20px_60px_rgba(0,0,0,0.45)] sm:right-auto sm:left-1/2 sm:w-[min(34rem,calc(100vw-3rem))] sm:-translate-x-1/2 sm:p-5"
	>
		<form class="space-y-4" onsubmit={handleAddFormSubmit}>
			<div class="space-y-2">
				<p class="font-mono text-[11px] tracking-[0.26em] text-slate-500 uppercase">Log Intake</p>
				<h3
					id="add-log-dialog-title"
					class="text-industrial-amber font-display text-xl tracking-[0.18em] uppercase"
				>
					Add Log From Google Doc
				</h3>
				<p class="copy-readable text-slate-400">
					Paste the Google Doc URL. On success, you will be redirected to the new log.
				</p>
			</div>

			<div class="space-y-2">
				<label
					class="font-mono text-[11px] tracking-[0.22em] text-slate-500 uppercase"
					for="log-url-input"
				>
					Google Doc URL
				</label>
				<input
					id="log-url-input"
					bind:value={addInput}
					type="url"
					{@attach focusOnAttach}
					placeholder="https://docs.google.com/..."
					aria-describedby={addErrorMessage ? 'log-url-error' : undefined}
					class="industrial-input w-full"
					disabled={addPending}
				/>
				{#if addErrorMessage}
					<p id="log-url-error" class="text-sm text-rose-300">{addErrorMessage}</p>
				{/if}
			</div>

			<div class="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
				<button
					type="button"
					onclick={closeModal}
					disabled={addPending}
					class="inline-flex min-h-11 items-center justify-center px-3 font-mono text-xs tracking-[0.18em] text-slate-500 uppercase transition-colors hover:text-slate-200 disabled:opacity-50"
				>
					Cancel
				</button>
				<button
					type="submit"
					disabled={addPending}
					class="industrial-btn text-industrial-amber border-industrial-dim hover:border-industrial-amber hover:text-industrial-amber min-w-32 justify-center bg-slate-950 disabled:opacity-50"
				>
					{addPending ? 'ADDING...' : 'ADD LOG'}
				</button>
			</div>
		</form>
	</div>
{/if}
