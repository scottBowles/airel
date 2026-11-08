/// <references types="houdini-svelte">

/** @type {import('houdini').ConfigFile} */
const config = {
	// Houdini 2.0 defaults to .houdini/schema.graphql; keep the committed copy, which CI builds from.
	schemaPath: './schema.graphql',
	// Houdini 2.0 bakes the API URL into the generated runtime at build time (it used to be read
	// at runtime by src/client.ts), so PUBLIC_GRAPHQL_ENDPOINT must be set when building.
	url: import.meta.env.PUBLIC_GRAPHQL_ENDPOINT,
	watchSchema: {
		url: 'env:PUBLIC_GRAPHQL_ENDPOINT'
	},
	scalars: {
		DateTime: {
			type: 'Date',
			unmarshal(val) {
				return new Date(val);
			},
			marshal(date) {
				return date.toISOString();
			}
		}
	},
	plugins: {
		'houdini-svelte': {}
	}
};

export default config;
