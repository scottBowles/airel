import { getContext, setContext } from 'svelte';

const USER_KEY = 'app-user';

type UserInfo = { isStaff?: boolean; [key: string]: unknown } | null | undefined;

export function setUserContext(getter: () => UserInfo) {
	setContext(USER_KEY, getter);
}

export function getUserContext(): () => UserInfo {
	return getContext<() => UserInfo>(USER_KEY) ?? (() => null);
}
