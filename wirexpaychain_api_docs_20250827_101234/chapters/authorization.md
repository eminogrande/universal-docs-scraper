# Authorization

The **Wirex BaaS API** supports multiple authorization flows to meet varying integration needs. Whether you operate a backend system or embed authentication directly into your frontend, the platform supports flexible and secure methods for accessing user-specific resources.

---

## Anonymous

### Description
Public routes that require no authentication or authorization. These are typically informational or infrastructure-level endpoints.

### Example Use Case
Checking system status or retrieving static documentation.

---

## Auth0

### Description
Best suited for partners with their own backend, user database, and established authentication methods. This flow uses a **server-side token** to access and act on behalf of any user managed by the partner.

### How to Obtain the Token
Use the **Client Credentials Grant** flow by making a request to Auth0’s token endpoint:

```bash
curl --request POST \
  --url https://{authorization_provider_domain}/oauth/token \
  --header 'content-type: application/json' \
  --data '{
    "client_id": "{your_client_id}",
    "client_secret": "{your_client_secret}",
    "audience": "{api_host_you_want_to_access}",
    "grant_type": "client_credentials"
}'
```

**Example for Wirex BaaS Sandbox**:

```bash
curl --request POST \
  --url https://wirex-pay-dev.eu.auth0.com/oauth/token \
  --header 'content-type: application/json' \
  --data '{
    "client_id": "{your_client_id}",
    "client_secret": "{your_client_secret}",
    "audience": "https://api-business.wirexpaychain.tech",
    "grant_type": "client_credentials"
}'
```

**Example Response**:

```json
{
  "access_token": "{your_access_token}",
  "token_type": "Bearer",
  "expires_in": 86400
}
```

### Required authorization credentials
- **Authorization**: Auth0 server access token.
- One of:
    - **X-User-Email**: Email associated with the user on whos behalf the request should be made.
    - **X-User-Wallet**: Crypto wallet address associated with the user on whos behalf the request should be made.
    - **X-User-Id**: Wirex system identifier of the user.
- **X-Chain-Id**: EIP155 id of the chain for which you want this request to be executed

### Use Cases
- Performing any requests on behalf of **any** the user
- Registering new users

---

## Wirex Token

### Description
This token is issued by **Wirex** and is tied to a specific user. It’s used to authorize direct, user-specific operations—typically in frontend or delegated flows.

### How to Obtain the Token
You can obtain a Wirex token in two ways:

#### Using Auth0 Server Token
Please see [Authorization->Auth0](#tag/Authorization/Auth0) section for details on how to obtain Auth0 server token. Once obtained you can exchange it for a Wirex token by calling the dedicated endpoint [`POST /api/v1/user/authorize`](#tag/User/paths/~1api~1v1~1user~1authorize/post).
You'll need:
  - **Authorization**: Auth0 server access token.
  - One of:
      - **X-User-Email**: Email associated with the user on whos behalf the request should be made.
      - **X-User-Wallet**: Crypto wallet address associated with the user on whos behalf the request should be made.
      - **X-User-Id**: Wirex system identifier of the user.
  - **X-Chain-Id**: EIP155 id of the chain for which you want this request to be executed

       #### Example:

       ```bash
       curl --request POST \
         --url https://api-business.wirexpaychain.tech/api/v1/user/authorize \
         --header 'Authorization: Bearer {your_auth0_access_token}' \
         --header 'X-User-Email: a.grey@wirexpaychain.com' \
         --header 'X-Chain-Id: 1001996' \
         --header 'Content-Type: application/json'
       ```

       **Response:**
       ```json
       {
         "token": "{wirex_pay_user_token}"
       }
       ```

#### Using Privy SDK  
Please see [Onboarding->Privy](#tag/OnboardingOffChain/Privy-SDK) section for details on integrating Privy SDK into your application. Once integrated you can use its hooks to obtain Access and Identity tokens with a call that would look something like this
```javascript
import {useIdentityToken, useToken, usePrivy} from '@privy-io/react-auth';

function getPrivyTokens() {
  const {getAccessToken} = useToken();
  const {identityToken} = useIdentityToken();
  const {ready, user} = usePrivy();
  useEffect(() => {
    if (user && ready) {
      getAccessToken().then((accessToken) => {
        console.log('access token: ', accessToken);
        console.log('identity token: ', identityToken);
      });
    }
  }, [ready, user]);
}
```
Once obtained you can exchange them for a Wirex token by calling the dedicated endpoint [`POST /api/v1/user/authorize`](#tag/User/paths/~1api~1v1~1user~1authorize/post).
You'll need:
- **Authorization**: Your Privy Access token
- **Identity**: Your Privy Identity token
- **X-Chain-Id**: EIP155 id of the chain for which you want this session to be effective for

  #### Example:

   ```bash
   curl --request POST \
     --url https://api-business.wirexpaychain.tech/api/v1/user/authorize \
     --header 'Authorization: Bearer {your_privy_access_token}' \
     --header 'Identity: Bearer {your_privy_identity_token}' \
     --header 'X-Chain-Id: 1001996' \
     --header 'Content-Type: application/json'
   ```

  **Response:**
   ```json
   {
     "token": "{wirex_pay_user_token}"
   }
   ```

### Required authorization credentials
- **Authorization**: Token issued using one of two methods described above

### Use Cases
- Performing any API requests **on behalf of a specific user**

---

## Summary of Authorization Flows

| **Flow Type**   | **Headers**                                                                                          | **Use Case**                                                   |
|-----------------|------------------------------------------------------------------------------------------------------|----------------------------------------------------------------|
| Anonymous       | None                                                                                                 | Public routes, no authentication required                      |
| Auth0           | **Authorization** (Auth0 server token) + **(X-User-Email/X-User-Wallet/X-User-Id)** + **X-Chain-Id** | Server-side access to perform operations on behalf of any user |
| Wirex Token | **Authorization** (user token)                                                                       | Frontend or delegated access for specific user actions         |

## POST /api/v1/user/authorize

**Summary:** Login as user

**Description:** Retrieve access token for a specific user that can be used to interact with all other APIs on his behalf

### Parameters

| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| bodyData | body | string |  | Body data |

### Responses

#### 200

OK

#### 400

Bad Request

#### 500

Internal Server Error

---

