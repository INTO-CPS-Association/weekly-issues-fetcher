# weekly-issues-fetcher

Simple Python script for fetching all currently open issues from the issue trackers of all partners.

# Configuration

The RTT issue tracker needs authentication before you can fetch the issues. The issue fetcher supports this my creating a file in your home directory called `fetch-issues.json`. Inside this file put something on the following form:

```
{
    "rtt_headers": {
        "Cookie": "MANTIS_STRING_COOKIE=<AUTH_TOKEN>; MANTIS_VIEW_ALL_COOKIE=793"
    }
}
```

Where `<AUTH_TOKEN>` is the authentication token you receive in the HTTP header after logging in to the RTT issue tracker using your credentials. An easy way to get this is simply by e.g. using the Developer Tools in Google Chrome. Open the Network tab, log in, and then look at the response header.
