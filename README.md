# reply-radar

A daily shortlist of X posts worth replying to. Distribution, not content, is the binding constraint on a small account, so this exists to find the right conversations, not to write more threads.

## The rule

Replies grow small accounts. Threads do not. Every morning the radar scans the last 24 hours of X for high-reach posts in wes's niche where a substantive reply from him would add something only he could say. It hands him the shortlist with a reply angle for each. He writes the replies himself, in his own voice.

The radar never posts, never drafts copy-paste replies, never touches his account. Read-only research, committed to this repo.

## wes's reply territory

Angles are only suggested when they draw on something he has actually built or measured:

- AI agent infrastructure and session management (DashClaw, LegCli session handoff)
- Token and cost economics of agent loops (measured subagent token costs, the $27.72 math-records run, plateau detectors)
- AI governance and agent guardrails (DashClaw catastrophe floor, approval gating, governed unattended runs)
- Coding agents and usage limits (where coding agents hide their limits)
- Dev-tool launches and building in public (Practical Systems blog, LegCli launch)

If a post does not connect to one of these, it is not an opportunity, no matter how viral it is.

## What a run produces

`radar/YYYY-MM-DD.md`: 5 to 10 opportunities, each with:

- the post (author, handle, one-line summary)
- a verbatim link to the post
- why it fits wes (which of his experiences applies)
- a reply angle: 2 to 3 sentences on the point to make, never a canned reply

Quality bar over quota. If fewer than 3 genuine opportunities exist, the file says the day was quiet and why.

## Selection rules

- Post is from the last 24 hours.
- Prefer accounts with real reach (10k+ followers or clearly high engagement), verified from the search results, never invented.
- Skip crypto and meme spam, rage-bait, posts already saturated with 50+ replies, and anything requiring knowledge wes does not have.
- Never invent follower counts, engagement numbers, or people. Only report what the search results show.
- No em dashes.

## Files

- `radar/` — one shortlist per day.
- `WATCHLIST.md` — starter accounts to check, curated by wes. Topic search runs regardless.
- `README.md` — this file.
