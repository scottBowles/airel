<script>
	let username;
	let password;

	const handleSubmit = (e) => {
		e.preventDefault();
		loginUser({ username, password });
	};

	const loginUser = ({ username, password }) => {
		fetch('http://127.0.0.1:8000/auth/jwt/create', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				username,
				password
			})
		})
			.then((res) => res.json())
			.then((json) => {
				localStorage.setItem('accessJwt', json.access);
				localStorage.setItem('refreshJwt', json.refresh);
			});
	};
</script>

<div>
	<form on:submit={handleSubmit}>
		<input type="text" name="username" placeholder="Username" bind:value={username} />
		<input type="password" name="password" placeholder="Password" bind:value={password} />
		<button type="submit">Login</button>
	</form>
</div>
