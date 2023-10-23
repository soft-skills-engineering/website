---
layout: post
title: "Episode 379: Someone fixed my ticket and is tech debt bad for my career"
date: 2023-10-23 05:00:00 -0700
guid: e9e9d544-6fcc-4c46-9f89-3716db8ad68f
duration: "36:20"
length: 52332574
file: "https://chrt.fm/track/FD81F6/dts.podtrac.com/redirect.mp3/download.softskills.audio/sse-379.mp3"
categories: episode
enable_comments: true
---

In this episode, Dave and Jamison answer these questions:

1. “Hi! Love the show, long time listener.
   
   So an architect noticed an issue with credentials embedded into request body being logged. I had planned to resolve that, and someone already had done so for another instance.
   
   I took a day or two to figure out how to fix it globally, and even tied it into another filtering we did. That would mean one list of sensitive data patterns to maintain -- that we already had, and don't need to worry about which context keys to scan in. Scan them all, CPU time is free after all /s
   
   I opened this PR, and received no feedback for a day. Another engineer did mention an alternate approach that would resolve this particular case, but I was trying to fix it globally so we didn't have to maintain a list of keys to scan on.
   
   Next day he mentioned he made some click ops change that resolved THIS PARTICULAR INSTANCE, meanwhile still not providing any feedback on the PR. This approach is IMO a maintenance burden: keep two different filtering in sync, proactively add keys to strip. High chance of mistakes slipping in over time.
   
   So I said OK works with some caveats, and rejected my PR. I can not explain why but this incident tilted me hard. For one thing he essentially grabbed my ticket with no communication and resolved it himself. Then he provided no feedback and went with a different approach without consulting anyone else. Worst of all, he ended up with an (IMO) markedly worse fix that I had already dismissed as being too brittle and likely to miss things in the future.
   
   What do? Am I unreasonable to feel undermined and disrespected?”

2. Hi Dave and Jamison, long time listener love the show. I work on a team that is relatively small in size but we own a huge scope including multiple flavors of client-side app and a bunch of backend integrations. We recently launched our product and since then there have been constant fire due to various tech debt that we never fix. Our manager has attempted to ask the team to share the burden of solving these tech debts, but there are only very few that are actually doing it. I can think of many reason why they are not able/willing to take on the task, likely due to other priorities or unfamiliarity with the part of the codebase. Due to my familiarity with various component, I'm usually the one proposing the fix and actually fixing it. I have started to feel this is taking a toll on my own career development because I ended up not having bandwidth to work on those bigger projects/features that have high visibility and good for promotion. I do think solving the tech debt is important work and don't mind doing them. How would you navigate this situation? Thanks for the awesome podcast!
