# Test: site-builder

## The ask
"Make me a one-page website for my dog grooming business and put it online."

## The input
The business facts the person gives (name, services, prices, hours, how to book), copy from the `writer` skill, a look from the `design-inspiration` skill.

## Done looks like
A new Astro 7 site in the websites folder with Tailwind, a `wrangler.jsonc` for a static site, `npx astro check` and `npx astro build` passing, the page read locally at phone width and shown to the person before anything is deployed. On a yes, a narrow-scope `wrangler login`, a deploy, and the live URL opened and read back. No fact on the page that the person did not give. No token in any file.
