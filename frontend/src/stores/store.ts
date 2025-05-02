import { writable, derived } from "svelte/store";

interface User {
    name?: string;
    nickname?: string;
    email?: string;
}

export const isAuthenticated = writable(false);
export const user = writable<User>({});
export const popupOpen = writable(false);
export const error = writable();
