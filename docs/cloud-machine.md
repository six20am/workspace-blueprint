# Running the Blueprint on a hosted cloud computer

Some AI apps give the agent its own cloud computer with a shell and a folder that lasts, but the computer itself is rebuilt every few hours. This page says what works there and what stays on a desktop install. It was tested on 2026-11-19 on one such computer, a hosted Claude session with an allowlisted network.

## Bottom line

- Run `bash setup/cloud-programs.sh` after each rebuild. It puts the programs back, skips what is already there and signs in to nothing. A full run took about five minutes, a second run three seconds.
- Every script under `tools/` works there. The repo's own test suite passed, 211 tests.
- The network on those computers usually lets in package registries and GitHub and blocks most other sites. Programs that fetch from the web (yt-dlp, gallery-dl, Scrapling, x-read, local-events) install but can't reach their sites. The agent's own web fetch and browser still can, and Defuddle and Trafilatura work on a page saved to a file.
- Remotion's own browser download is blocked there, so the script installs Chromium from npm and `tools/motion/render.mjs` uses it when `REMOTION_BROWSER_EXECUTABLE` is set. Rendering a video worked.
- The whisper model download is blocked there too. Use a transcription service the agent can reach instead.

## Desktop only, and why

| Item | Why it stays on a desktop |
|---|---|
| Claude Code | The desktop app. Duet is already Claude, so nothing to add. |
| Superpowers plugin | A Claude Code plugin. Claude Code only. |
| NotebookLM | Installs, but needs a Google browser sign-in that doesn't last here, and there is no NotebookLM connector. |
| Agent Reach | Installs, but needs social media logins and can't reach those sites from here. |
| rtk | Trims command output for Claude Code on a PC. Its download site is blocked here too. |
| rtk hook | Changes Claude Code settings. Claude Code only. |
| ccusage | Reads Claude Code usage logs on a PC. |
| CodeBurn | Reads Claude Code spend logs on a PC. |
| Scrapling MCP | A local MCP server. Hosting it online wouldn't help, since it needs a real browser. The cloud browser covers it. |
| Chrome DevTools MCP | Drives Chrome on your PC. Here Claude in Chrome and the cloud browser cover it. |

## Installs on the cloud computer but can't reach its sites

| Item | What happens |
|---|---|
| yt-dlp | Installs, but YouTube and most video sites are blocked from here. Use it on the PC. |
| Scrapling | Installs, but can't reach websites from here. The cloud browser does this job. |
| gallery-dl | Installs, but image sites are blocked from here. |
| whisper.cpp | Builds, but its speech model download is blocked. Use ElevenLabs transcribe, which you have connected. |
| whisper English model | Hugging Face is blocked from here. No safe second source. |

## Skills that need a desktop

| Skill | Why |
|---|---|
| agent-reach | Needs social logins and sites blocked from here. |
| agent-web-fetch | Sits on top of agent-reach. |
| channel-mine | Needs yt-dlp. YouTube is blocked from here. |
| client-asset-harvester | Crawls a live site. Sites are blocked from this shell. |
| gallery-dl | Image sites are blocked from here. |
| notebooklm-research | Needs a Google sign-in that won't last here. |
| scrapling | Sites are blocked from this shell. The cloud browser does this. |
| x-read | Its X reader service is blocked from here. |
| local-events | City calendar sites are blocked from this shell. |
| site-builder | Builds here, but deploying needs a Cloudflare login. |
| doctor | Checks a PC install. The cloud script does this job here. |
| update | Updates a PC install. |
| workspace-audit | Checks a PC workspace's map and router. |
| backup | Copies a PC folder to a drive. |
| undo | Save history of a PC folder. |

## Skills whose helper script must travel with them

These work on the cloud computer once the skill's `tools/` script ships inside the skill folder (or sits in the agent's folder). They are money-log, renewals, waiting-on, decision-log, paperwork, photo-organizer, tax-time, outbound-check, media-tools, document-builder, markitdown, motion-video, video-shots, legacy-journal.

