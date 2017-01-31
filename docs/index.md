# Reviews API

This application allows its users to manage a collection of simple company reviews.



## Specification

The application was designed in order to support the following requirements:

>   1.  Users are able to submit reviews to the API.
>
>   2.  Users are able to retrieve reviews that they submitted.
>
>   3.  Users cannot see reviews submitted by other users
>
>   4.  Use of the API requires a unique auth token for each user
>
>   5.  Submitted reviews must include, at least, the following attributes:
>
>       1.  Rating - must be between 1 - 5
>
>       2.  Title - no more than 64 chars
>
>       3.  Summary - no more than 10k chars
>
>       4.  IP Address - IP of the review submitter
>
>       5.  Submission date - the date the review was submitted
>
>       6.  Company - information about the company for which the review was submitted, can be simple text (e.g., name, company id, etc.) or a separate model altogether
>
>       7.  Reviewer Metadata - information about the reviewer, can be simple text (e.g., name, email, reviewer id, etc.) or a separate model altogether
>
>   Optional: Provide an authenticated admin view that allows me to view review submissions



## Analysis

Certain terms in this specification are obvious candidates for implementation as primary system resources: users, reviews, companies, reviewers.  It remains unclear from the specification, however, whether the concept of a user of the system corresponds to that of the author of a review.  The description of reviewer metadata suggests a reviewer is just another one of several data elements that comprise a review record, while users feature prominently in the rest of the specification as the main and indeed sole actor engaged with the application.  In this light, it is considered that users and reviewers do not correspond to the same concept in this application's ontology.

Privilege boundaries exist between users: they can be understood as multiple tenants maintaining independent collections of reviews on a shared application.  Yet intuition suggests the application operator may hold interest in the united collection of reviews submitted by any tenant regarding some specific company.  This may prove difficult if companies were not identified uniformly across tenants but were instead homed independently within the resource namespace subscribed to each individual tenant, which would create the possibility for duplication.  The analogous situation is intuitively thought to be less problematic for reviewers, but it may still pose a problem.

In the absence of further input on the issue, it is thought best therefore to implement a shared collection of companies and another of reviewers common to all application users to which any user may add new records, while the collection of reviews remains itself partitioned by the submitting application user so that any user may see all recorded companies and reviewers and submit reviews for any pair of them, yet only have the capacity to interact with those reviews they themselves submitted to the application.

The specification suggests a simplification of this scheme that could reduce reviewers and companies to simple names, but this exercise intends to showcase skills that are best displayed with a more complex design.  Naturally, this criterion would not apply for an industrial problem.



## Design

1.  The application provides an HTTP API designed in accordance with [the REST style of application architecture](https://www.ics.uci.edu/~fielding/pubs/dissertation/rest_arch_style.htm) organized around four primary resource collections: users, companies, reviewers, and reviews.

2.  Application resources are identified with URIs scoped within a common base address, e.g. `https://reviews.mgomez.ch/`.  As preparation for possible future breaking changes to the API, resource URIs are further scoped after a prefix that indicates the major version of the API, which is currently `v1/`, so that all application resource URIs, following that example, would be prefixed with the API entrypoint address `https://reviews.mgomez.ch/v1/`.

3.  Each collective resource is identified by a URI and, subject to user authorization, can be dereferenced to obtain a paged enumeration of its items; for example, the first page of the collection of users would be identified by the collection name, `users`, appended to the API entrypoint, yielding a base collection URI like `https://reviews.mgomez.ch/v1/user`.

4.  Each collective resource URI provides a namespace for a flat, homogenous set of individual resources, each of which is identified with an URI that suffixes the collection's base URI with an additional path component to identify the individual resource; for example, the URI to the individual resource to the user profile with username `foo` might be `https://reviews.mgomez.ch/v1/user/foo`.

5.  Individual and collective resource URIs can be dereferenced and obey the expected HTTP semantics; e.g.

    *   `GET` transfers a representation of resource state to the client in the HTTP response entity.

    *   `POST` on a collective resource requests the creation of a new collection item with its properties specified in the HTTP request entity.

    *   `PUT` on an individual resource requests the full overwrite of the current state of the resource.

    *   `DELETE` on an individual resource requests deletion of that resource.

    All of these actions are subject to authorization.

6.  All individual resources have two additional informational attributes of their states named `created` and `modified` that hold each individual resource's creation and last modification timestamp.


### Users

1.  Users are the actors with whom the application interacts.

2.  Users have differentiated privileges, so each user must present credentials to the application for identification.

3.  Some users are considered administrators and hold special privileges other non-administrator users lack.

5.  Administrators can register new application users; other non-administrator users cannot.

6.  Administrators can inspect and modify all user records, while other users can merely inspect their own user record.

7.  Individual users have a `username` attribute of their state used to construct their URIs using the aforementioned scheme.  Along with this username, users have an associated secret password that the application stores as a salted cryptographic hash.  Together, these are the user's primary credentials.

8.  Users are identified as administrators or non-administrators by the value of an attribute of their state named `is_staff` of boolean type, such that the `is_staff` variable has the true value if and only if the user is an administrator.

9.  Users have an additional informational attribute of their state named `email` that holds the user's e-mail address.

10. Two distinct users cannot share an e-mail address or a username.


### Companies

1.  Users maintain a common collection of company records shared among all users.  Company records represent each entity that may be the subject of zero or more reviews.

2.  Individual companies have a numeric surrogate key attribute of their state used to construct their URIs using the aforementioned scheme.


### Reviewers

1.  Users maintain a common collection of reviewer records shared among all users.  Reviewer records represent each entity that may be the author of zero or more reviews.

2.  Individual reviewers have an `email` attribute of their state holding their e-mail addresses and used to construct their URIs using the aforementioned scheme.  Two distinct reviewerrs cannot share an e-mail address.

3.  Reviewers have an additional informational attribute of their state named `name` that holds the reviewer's name.


### Reviews

1.  Users maintain per-user private collections of the reviews submitted by each user.

2.  Administrators can inspect and modify all reviews submitted by any user, while other users can only inspect and modify reviews they submitted themselves.

3.  Individual reviews have a numeric surrogate key attribute of their state used to construct their URIs using the aforementioned scheme.

4.  Reviews have several additional informational attributes of their state in the form of relations with other individual resources:

    1.  `submitter`: The user that submitted the review into the application.

    2.  `company`: The company subject to this review.

    3.  `reviewer`: The reviewer who authored the review.

5.  Reviews have several additional informational attributes of their state:

    1.  `rating`: A numeric integer value between 1 (worst) to 5 (best) representing the reviewer's rating of the company.

    2.  `title`: Up to 64 characters of text representing the title of the review.

    3.  `summary`: Up to 10000 characters of text representing a summary of the reviewer's experience with the company.

    4.  `ip_address`: The IP address from whence the review submission HTTP request was received.


## Implementation


### Resource representation format

Resource representations are encoded using [JSON](http://www.json.org/).

Individual resources are represented using JSON objects with a key-value pair for each attribute in the state representation.  In addition, the `self` key will always be populated with the URI for the resource.

Collective resource representations are likewise represented using JSON objects.  The `previous` and `next` keys of the JSON object are associated to the URIs for the previous and next pages of the collection, or `null` if there are no such pages.  The `results` key is associated to a list whose elements are the JSON-encoded resource representations for the individual resources included in the page.


### Authentication


#### HTTP Basic

Users may authenticate their identities to the server when performing API requests by supplying their primary credentials using [the Basic HTTP authentication scheme](https://tools.ietf.org/html/rfc7617) on each individual request.


#### API Token

Users may provide their primary credentials in the `username` and `password` fields in the request entity of a `POST` HTTP request (as [URL-encoded form data](https://www.w3.org/TR/html5/forms.html#url-encoded-form-data) or using a [JSON](http://www.json.org/) object with `username` and `password` keys and their corresponding string values) to the URL at `api-token-auth/` within the common base address (without the version prefix); e.g. `https://reviews.mgomez.ch/api-token-auth/`.

If the server can authenticate the provided primary credentials, it will respond with a success status code and provide the user with a secondary authentication credential in the form of a randomly generated 40-digit hexadecimal string found within the `token` key of a JSON object in the HTTP response entity; e.g.

    { "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b" }

The token text can be used to authenticate subsequent HTTP requests using the `Authorization` header as such:

    Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b


#### JSON Web Token

Users may provide their primary credentials in the `username` and `password` fields in the request entity of a `POST` HTTP request (as [URL-encoded form data](https://www.w3.org/TR/html5/forms.html#url-encoded-form-data) or using a [JSON](http://www.json.org/) object with `username` and `password` keys and their corresponding string values) to the URL at `jwt/auth` within the common base address (without the version prefix); e.g. `https://reviews.mgomez.ch/jwt/auth`.

If the server can authenticate the provided primary credentials, it will respond with a success status code and provide the user with a secondary authentication credential in the form of a [JSON Web Token](https://jwt.io/) found within the `token` key of a JSON object in the HTTP response entity; e.g.

    {
      "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxLCJlbWFpbCI6ImFkbWluQGV4YW1wbGUuY29tIiwidXNlcm5hbWUiOiJhZG1pbiIsImV4cCI6MTQ4NTgyNTU3OSwib3JpZ19pYXQiOjE0ODU4MjE5Nzl9.P1-objmQuj8T1ThUx0nu2uREEesGo8ozQY8vVNyEr9g"
    }

The token text can be used to authenticate subsequent HTTP requests using the `Authorization` header as such:

    Authorization: JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxLCJlbWFpbCI6ImFkbWluQGV4YW1wbGUuY29tIiwidXNlcm5hbWUiOiJhZG1pbiIsImV4cCI6MTQ4NTgyNTU3OSwib3JpZ19pYXQiOjE0ODU4MjE5Nzl9.P1-objmQuj8T1ThUx0nu2uREEesGo8ozQY8vVNyEr9g

JSON Web Tokens expire after a configurable timeout currently set to one hour.  A renewed token can be obtained before timeout without providing the primary credentials again by performing a `POST` HTTP request to the URL at `jwt/refresh` within the common base address (without the API version prefix); e.g. `http://reviews.mgomez.ch/jwt/refresh`.  This request must carry the current unexpired token in the `token` field in the request entity (as [URL-encoded form data](https://www.w3.org/TR/html5/forms.html#url-encoded-form-data) or using a [JSON](http://www.json.org/) object with the `token` keys and the corresponding string value).


## Live documentation

The API implementation comes with live [Swagger](http://swagger.io/) interactive API documentation at the API common base address (e.g. <https://reviews.mgomez.ch/>) as well as a live API browser at the API entrypoint address (e.g. <https://reviews.mgomez.ch/v1/>).  These can be used for interactive discovery of API features within a Web browser.


### Deployment

The components of this application are meant to be managed and executed by Docker Compose.

To run this application in production, copy or make a symbolic link to `docker-compose.production.yml` named `docker-compose.override.yml`, and run `docker-compose up`.  Make sure to customize the deployment domain name on `docker-compose.production.yml`.

The recommended development environment is Ubuntu Linux 16.04.  [Clone this repository](https://github.com/mgomezch/local_services), run the `setup-ubuntu.sh` and run `docker-compose up -d` inside that repository's root directory to bring supporting services up.  After doing that, bring this project up by running `docker-compose up -d` in this project's root repository directory.  After the database initializes, you should be able to open the application at <http://reviews.service.consul.test/>.

After deployment, make sure to run `docker-compose run --rm web sync` to set up the database.
