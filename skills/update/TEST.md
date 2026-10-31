# Test: update

## The ask
"What is new in the blueprint? Update me."

## The input
A workspace with a version file dated more than 30 days ago.

## Done looks like
The skill checks first and changes nothing, lists what is new, asks before applying, and never touches the owner's own files. The version file is updated only after the update runs.
