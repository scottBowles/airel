<script>
	import { session } from '$app/stores';
	import { goto } from '$app/navigation';
	import { get, post } from '$lib/utils';

	let username;
	let password;
	let errors;

	async function loginUser() {
		const res = await post('api/auth/login', { username, password });
		if (res.ok) {
			fetchUser();
			goto('/');
		} else {
			const { non_field_errors } = await res.json();
			errors = non_field_errors.join('\n');
		}
	}

	async function fetchUser() {
		const res = await get('api/auth/me');
		const user = await res.json();
		$session.user = user;
	}
</script>

<div>
	<form on:submit|preventDefault={loginUser}>
		<input
			type="text"
			name="username"
			placeholder="Username"
			bind:value={username}
		/>
		<input
			type="password"
			name="password"
			placeholder="Password"
			bind:value={password}
		/>
		<button type="submit">Login</button>
	</form>
	<h4>{errors}</h4>
</div>
