<script>
	import { goto } from '$app/navigation';
	import api from '$lib/api';
	import { post } from '$lib/utils';

	let username;
	let password;
	let errors;
	let token;
	let user;

	async function loginUser() {
		const res = await post('api/auth/login', { username, password });
		const json = await res.json();
		const { auth_token, non_field_errors } = json;
		if (res.ok) {
			token = auth_token;
			fetchUser();
			goto('/');
		} else {
			errors = non_field_errors.join('\n');
		}
	}

	async function fetchUser() {
		const res = await api.get('auth/users/me/', token);
		const json = await res.json();
		user = JSON.stringify(json);
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
