<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { user } from '$lib/stores/auth';

	onMount(() => {
		// Redirect to dashboard if authenticated
		if ($user) {
			goto('/dashboard');
		} else {
			goto('/login');
		}
	});
</script>

