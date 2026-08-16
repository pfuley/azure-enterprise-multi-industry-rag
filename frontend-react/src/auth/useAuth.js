import {
    InteractionRequiredAuthError,
} from "@azure/msal-browser";

import {
    InteractionStatus,
} from "@azure/msal-browser";

import {
    useMsal,
} from "@azure/msal-react";

import {
    loginRequest,
} from "./msalConfig";


export function useAuth() {

    const {
        instance,
        accounts,
        inProgress,
    } = useMsal();


    const activeAccount =
        instance.getActiveAccount()
        || accounts[0]
        || null;


    const isInteractionInProgress =
        inProgress !== InteractionStatus.None;


    async function signIn() {

        if (isInteractionInProgress) {

            throw new Error(
                "Microsoft sign-in is already in progress."
            );
        }


        if (activeAccount) {

            return activeAccount;
        }


        const result =
            await instance.loginPopup({
                ...loginRequest,

                prompt:
                    "select_account",
            });


        if (result.account) {

            instance.setActiveAccount(
                result.account
            );
        }


        return result.account;
    }


    async function signOut() {

        if (isInteractionInProgress) {

            throw new Error(
                "An authentication operation is already in progress."
            );
        }


        const account =
            instance.getActiveAccount()
            || activeAccount;


        if (!account) {
            return;
        }


        await instance.logoutPopup({
            account,
            mainWindowRedirectUri:
                window.location.origin,
        });


        instance.setActiveAccount(
            null
        );
    }


    async function getAccessToken() {

        const account =
            instance.getActiveAccount()
            || activeAccount;


        if (!account) {

            throw new Error(
                "The user is not signed in."
            );
        }


        try {

            const result =
                await instance.acquireTokenSilent({
                    ...loginRequest,
                    account,
                });


            return result.accessToken;

        } catch (error) {

            if (
                error
                instanceof
                InteractionRequiredAuthError
            ) {

                if (isInteractionInProgress) {

                    throw new Error(
                        "Microsoft authentication is already in progress."
                    );
                }


                const result =
                    await instance.acquireTokenPopup({
                        ...loginRequest,
                        account,
                    });


                return result.accessToken;
            }


            throw error;
        }
    }


    return {
        account:
            activeAccount,

        isAuthenticated:
            Boolean(
                activeAccount
            ),

        isInteractionInProgress,

        signIn,
        signOut,
        getAccessToken,
    };
}