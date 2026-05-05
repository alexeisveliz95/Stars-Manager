## Credit consumption details

[Credits Consumption Documentation](https://docs.x.com/x-api/getting-started/pricing#credit-consumption-details)

All prices are per resource fetched (reads) or per request (writes/actions). [Purchase credits](https://console.x.com) in the Developer Console.

### ​ Read operations
[Read Operations Doccumentation](https://docs.x.com/x-api/getting-started/pricing#read-operations)

Charged per resource returned in the response.

|Resource|Unit Cost|
|---|---|
|**Posts: Read**|$0.005 per resource|
|**User: Read**|$0.010 per resource|
|**DM Event: Read**|$0.010 per resource|
|**Following/Followers: Read**|$0.010 per resource|
|**List: Read**|$0.005 per resource|
|**Space: Read**|$0.005 per resource|
|**Community: Read**|$0.005 per resource|
|**Note: Read**|$0.005 per resource|
|**Media: Read**|$0.005 per resource|
|**Analytics: Read**|$0.005 per resource|
|**Trend: Read**|$0.010 per resource|

###  Write operations

[​Write Operations Documentation](https://docs.x.com/x-api/getting-started/pricing#write-operations)

Charged per request.

|Action|Unit Cost|
|---|---|
|**Content: Create**|$0.015 per request|
|**Content: Create (with URL)**|$0.200 per request|
|**DM Interaction: Create**|$0.015 per request|
|**User Interaction: Create**|$0.015 per request|
|**Interaction: Delete**|$0.010 per request|
|**Content: Manage**|$0.005 per request|
|**List: Create**|$0.010 per request|
|**List: Manage**|$0.005 per request|
|**Bookmark**|$0.005 per request|
|**Media Metadata**|$0.005 per request|
|**Privacy: Update**|$0.010 per request|
|**Mute: Delete**|$0.005 per request|
|**Counts: Recent**|$0.005 per request|
|**Counts: All**|$0.010 per request|

Prices are subject to change. Current rates are always available in the [Developer Console](https://console.x.com) and on the [developer.x.com pricing page](https://developer.x.com/#pricing).

---

##  Owned Reads

[​Owned Read Documentattion](https://docs.x.com/x-api/getting-started/pricing#owned-reads)

Owned Reads are requests made by your own developer app for your own data (posts, bookmarks, followers, likes, lists, and more). These endpoints are priced at **$0.001 per resource** (1,000 resources for $1). The following endpoints qualify for Owned Read pricing when `{id}` matches the authenticated user and that user is the owner of the developer app:

|Endpoint|Description|
|---|---|
|`GET /2/users/{id}/tweets`|Your own posts|
|`GET /2/users/{id}/mentions`|Your mentions|
|`GET /2/users/{id}/liked_tweets`|Posts you liked|
|`GET /2/users/{id}/bookmarks`|Your bookmarks|
|`GET /2/users/{id}/followers`|Your followers|
|`GET /2/users/{id}/following`|Accounts you follow|
|`GET /2/users/{id}/blocking`|Accounts you blocked|
|`GET /2/users/{id}/muting`|Accounts you muted|
|`GET /2/users/{id}/owned_lists`|Lists you own|
|`GET /2/users/{id}/followed_lists`|Lists you follow|
|`GET /2/users/{id}/list_memberships`|Lists you belong to|
|`GET /2/users/{id}/pinned_lists`|Your pinned lists|