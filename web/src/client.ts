import { HoudiniClient } from '$houdini';

export default new HoudiniClient({
    url: 'env:PUBLIC_GRAPHQL_ENDPOINT',

    // You can add validation logic, authentication, etc. here
    // fetchParams({ session }) {
    //     return {
    //         headers: {
    //             Authorization: `Bearer ${session.token}`,
    //         }
    //     }
    // }
})
