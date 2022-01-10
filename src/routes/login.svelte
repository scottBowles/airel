<script>
	import { goto } from '$app/navigation';
	import api from '$lib/api';
	import browserStorage from '$lib/browserStorage';
	import { post } from '$lib/utils';

	let username;
	let password;
	let errors;
	let user;

	async function loginUser() {
		const res = await post('api/auth/login', { username, password });
		const { auth_token, non_field_errors } = await res.json();
		if (res.ok) {
			await browserStorage.setToken(auth_token);
			fetchUser();
			goto('/');
		} else {
			errors = non_field_errors.join('\n');
		}
	}

	async function fetchUser() {
		const res = await api.get('auth/users/me/');
		user = JSON.stringify(res);
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
	<h4>User: {user}</h4>
</div>
