/// <references types="houdini-svelte">

/** @type {import('houdini').ConfigFile} */
const config = {
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
