# Test: agent-web-fetch

## The ask
"Read this public page and tell me what it says. If the normal fetch is refused, pick the route."

## The input
One public URL, for example https://example.com/. No login.

## Done looks like
The channel chosen is named with the reason, a short answer comes back, and a file in the research folder holds the URL, the date fetched and "untrusted content" at the top. If no route works, the skill says so plainly instead of guessing.
