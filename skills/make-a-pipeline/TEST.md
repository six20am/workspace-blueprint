# Test: make-a-pipeline

## The ask
"I write the same Monday update email every week. Can you set that up?"

## The input
The last three Monday updates in the workspace (or the undo history showing them), and the person's answers to four questions asked one at a time: what starts it, the steps, what comes out and who gets it, where they check.

## Done looks like
A pipeline folder with numbered stage subfolders, each with a one-screen `contract.md` (Input, Do, Output, Check), a `README.md` with the trigger line, and one new row in the router file. The check sits before the send, and the send itself is a human step. The first real run done together with a stop at the check, one contract fixed from what that run showed, then saved with undo. No second pipeline built.
