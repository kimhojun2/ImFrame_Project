# Samsung Account

## Redirect a user to the Samsung Account login

### signInGate

`https://account.samsung.com/accounts/v1/{APPALIAS}/signInGate`

- PATH PARAMETERS
  - APPALIAS: This path value is defined when OAuth 2.0 client is created and registered to the Samsung Account

- QUERY PARAMETERS
  - country_code: Two digit ISO 3166 country code
  - locale: Browser locale
  - client_id: Public client ID of your Samsung Account client
  - response_type: Fixed value CODE should always be used
  - redirect_uri: URI or callback location where the authorization code gets sent. It should match one of the registered redirect URIs for your Samsung Account client
  - scope: Access requested by the client app
  - state: Opaque value used by the client to maintain the state between the request and callback. The authorization server includes this value when redirecting the user back to the client
  - prompt: Option to display a user consent prompt
  - uaid: Correlation ID that's randomly generated per request to allow request tracking between client and server

### signOutGate

`https://account.samsung.com/accounts/v1/{APPALIAS}/signOutGate`

- PATH PARAMETERS
  - APPALIAS: This path value is defined when OAuth 2.0 client is created and registered to the Samsung Account

- QUERY PARAMETERS
  - signOutURL: URL for browser redirect after the user has signed out of Samsung Account
  - state: Opaque value used by the client to maintain the state between the request and callback. The authorization server includes this value when redirecting the user back to the client
  - client_id: Public client ID of your Samsung Account

## Get a Samsung Account access token

- Next, exchange the authorization code for a Samsung Account access token with the token endpoint using your Samsung Account client ID and secret

- client_id: your public Samsung Account client ID
- client_secret: your Samsung Account secret key
- grant_type: the OAuth 2.0 grant type; should always be set to authorization_code
- code: the authorization code extracted from the signInGate response
- redirect_uri: the same redirect_uri used when requesting the authorization code

## Sign your Client Identifier with your Samsung Account access token

```java
// Downloaded from the Knox Portal 
String clientIdentifier = <Your Client Identifier>; 
String downloadedKeys = <insert path to keys.json>; 

// Retrieved using the Samsung Account token API  
String saAccessToken = < Your Samsung Account access token >; 


String publicKey = KnoxTokenUtility.generateBase64EncodedStringPublicKey(
                                new FileInputStream(new File(downloadedKeys))); 
String signedClientIDJWT = KnoxTokenUtility.generateSignedclientIdentifierJwtWithIdpAccessToken(
                                new FileInputStream(new File(downloadedKeys)),
                                clientIdentifier, 
                                saAccessToken);
```

## Get a Knox Cloud Services access token

- When your Knox Cloud Services access token expires, you can use the accessTokenOAuth2 endpoint to repeatedly request a new access token until the session token is invalidated or expires. You must sign the Samsung Account access token before each of these requests to avoid replay attacks

## Sign your Knox Cloud Services access token

```java
String signedAccessToken = KnoxTokenUtility.generateSignedAccessTokenJWT(
                                new FileInputStream(new File(downloadedKeys)), 
                                < Your unsigned Knox Cloud Services access token >);
```

## Start making Knox Cloud Services API calls

- If this step fails, ensure that your end customers have established a full trust relationship with your portal

## Regenerate access token using refresh token

- You can regenerate the Knox Cloud Services access token when it expires using the Refresh Token
- The Refresh Token can be found in the response of Samsung Account access token

## Problems

- need a company verification for partner account
- sign up for a partner account with university first
