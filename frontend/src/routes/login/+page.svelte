<script lang="ts">
	import { goto } from '$app/navigation';
	import { authStore, user } from '$lib/stores/auth';
	import LoginForm from '$lib/components/LoginForm.svelte';

	$: if ($user) {
		goto('/dashboard');
	}
</script>

<LoginForm />

