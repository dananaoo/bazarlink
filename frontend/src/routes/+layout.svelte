<script lang="ts">
	import '../app.css';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { authStore, user } from '$lib/stores/auth';
	import Layout from '$lib/components/Layout.svelte';
	import LoginLayout from '$lib/components/LoginLayout.svelte';

	let mounted = false;
	
	onMount(() => {
		mounted = true;
	});

	$: isAuthenticated = $user !== null;
	$: currentPath = $page.url.pathname;

	// Redirect to login if not authenticated and not on login page
	$: if (mounted && !isAuthenticated && currentPath !== '/login') {
		goto('/login');
	}
</script>

{#if isAuthenticated}
	<Layout>
		<slot />
	</Layout>
{:else}
	<LoginLayout>
		<slot />
	</LoginLayout>
{/if}
