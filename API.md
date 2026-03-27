# Kamekverse API documentation

## `/api/server_config/`
Example: `{"server_name": "Kamekverse", "is_production": true, "is_development": false, "env_name": "prod", "env_id": "L1"}`

This endpoint returns basic info about the instance.

### `server_name`

Name of the instance.

### `is_production`

Is it prod?

### `is_development`

Is it dev? NOTE - is_development defines if the instance used to develop kamekverse itself or not.

### `env_name`

Long env name

### `env_id`

Env id. Starts with a letter, ends with a number by default, but instance owners may reconfigure it to whatever they want it to be.

## `/api/community/<olive_title_id>/<olive_community_id>/posts`

This endpoint will return posts from an public (!) community. You can give it a number in the GET param `amount` to specify the amount of posts in the output. Default is 200. If you will put in `all`, then the output will be every post in the community.

Example: `{"result": 200, "posts": [{"id": "AYMHAABBCAfnoS5ScY9mtw", "author": "superdumbmario2", "body": "Test post with an image", "yeah": 0, "nah": 0, "mii_expression": "happy", "is_spoiler": false, "is_featured": false, "replies": 0, "is_image": true, "image": "/cdn/post_images/6df90ed638bc41618ed8a97cd8b17ff4.png"}, {"id": "AYMHAABBuGW4DQiMm88I3g", "author": "superdumbmario2", "body": "Test post without an image", "yeah": 0, "nah": 0, "mii_expression": "normal", "is_spoiler": false, "is_featured": false, "replies": 0, "is_image": false}]}`

### Auth

You need an API key to access private communities' metadata.

Just pass in an `Authorization` header with value of `Beaver <api key>`, replacing <api key> with your own Kamekverse API key.

You only can do this if you are whitelisted in the said community.

### `result`

200 if successful.

404 if you try to obtain data from a non-existent community.

403 if you try to obtain data from a private community.

### `posts`

This will only exist if `result` = 200.

Is a list of posts.

#### `id`

Post ID.

#### `author`

Post author.

#### `body`

Post body.

#### `yeah`

Amount of yeahs.

#### `nah`

Amount of nahs.

#### `mii_expression`

The Mii expression set in the post.

#### `is_spoiler`

Is the post spoiler-tagged?

#### `is_featured`

is the post featured on the instance's homepage?

#### `replies`

Amount of replies on the post.

#### `is_image`

Does the post have an image?

#### `image`

A path to the image. Please note that it doesn't include the domain, so you will have to add that yourself.

## `api/user/<username>/profile`

This endpoint will return profile metadata (e.g mii, displayname, etc.) of a specific user.

Example: `{"result": 200, "username": "api_example", "mii_name": "API Example", "mii_method": "mii-pnid", "mii_value": "PN_Jon", "bio": "My bio", "follower_count": 0, "friend_count": 0, "follow_count": 0, "game_experience": "beginner", "karma": 0}`

### `result`

200 if successful.

404 if you try to obtain data from a non-existent user.

403 if you try to obtain data from a banned user.

### `username`

The user's username.

### `mii_name`

The user's Mii Name.

### `mii_method`

If a NNID is used, `mii-nnid`.

If a PNID is used, `mii-pnid`.

If raw Mii Data is used, `mii-data`.

If no Mii is present, `empty`.

### `mii_value`

If a NNID is used, then the NNID is here. If a PNID is used, then a PNID. If raw Mii data is used, then the data that was used. If no mii, then it may be anything.

### `bio`

User's bio

### `follower_count`

Amount of people that followed the user.

### `friend_count`

Amount of the user's friends.

### `follow_count`

Amount of people the user followed.

### `game_experience`

Set game experience, lowercase.

### `karma`

Amount of Mii Coins.

## `/api/community/<olive_title_id>/<olive_community_id>/metadata`

This endpoint will return metadata of a community.

Example: `{"result": 200, "name": "Test API community", "desc": "", "is_locked": false, "is_redesigned": false, "platform_name": "", "max_post_length": 2200, "max_comment_length": 2200, "is_special": false, "is_featured": false, "allow_comments": true, "offdevice_icon": "/cdn/community_icons/default.png", "has_badge": false, "console": 1, "author": "superdumbmario2"}`

### Auth

You need an API key to access private communities' metadata.

Just pass in an `Authorization` header with value of `Beaver <api key>`, replacing <api key> with your own Kamekverse API key.

You only can do this if you are whitelisted in the said community.

### `result`

200 if successful.

404 if you try to obtain data from a non-existent community.

403 if you try to obtain data from a private community.

### `name`

Community name.

### `desc`

Community description.

### `is_locked`

Can normal users post to it? true if no, false if yes

### `is_redesigned`

when/if i will add redesign features to kamekverse, this will be used to determine if a community will use redesign features.

### `platform_name`

Platform name.

### `max_post_length`

Max length of posts.

### `max_comment_length`

Max length of comments.

### `is_special`

Is the community on the special tab?

### `is_featured`

Is the community on the featured tab?

### `allow_comments`

Can you post comments on posts in this community?

### `offdevice_icon`

Path to the Community icon on offdevice and neo layouts. Note that it doesn't include the URL to the instance.

### `has_badge`

Does it have a blue badge?

### `badge`

Only exists if `has_badge` is `true`.

Contents of the blue badge.

### `console`

The ID of the console badge if the community has it. Currently unusable.

### `author`

If the community is user-created or an author acc was passed thru the admin panel, this will show the username of the author.

### `offdevice_banner`

If the community has it, it will link to the banner used on offdevice and neo layouts. Note that it doesn't include the URL to the instance.

## `/api/community/list`

Example: `[{"olive_title_id": 0, "olive_community_id": 0}, {"olive_title_id": 1, "olive_community_id": 1}, {"olive_title_id": 2, "olive_community_id": 2}, {"olive_title_id": 3, "olive_community_id": 3}, {"olive_title_id": 4, "olive_community_id": 4}]`

This endpoint returns a list of every public (!) community as olive_title_id and olive_community_id.

## Notes

To get the `olive_title_id` and `olive_community_id` values of a community, you just need to go to that community's page and look at the url.

Example url: `kamekverse.pythonanywhere.com/titles/123/456`

The first number in the url after `titles` is `olive_title_id`, the next number is `olive_community_id`.