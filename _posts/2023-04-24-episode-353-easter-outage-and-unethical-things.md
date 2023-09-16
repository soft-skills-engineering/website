---
layout: post
title: "Episode 353: Easter outage and unethical things"
date: 2023-04-24 05:00:00 -0700
guid: 37457223-4ee4-40b9-aca4-b39105ca5413
duration: "30:30"
length: 25970712
file: "https://chrt.fm/track/FD81F6/dts.podtrac.com/redirect.mp3/download.softskills.audio/sse-353.mp3"
categories: episode
enable_comments: true
---

In this episode, Dave and Jamison answer these questions:

1. I work for a startup with a distributed team. Recently one of our clients experienced a production outage. As a small startup, we do not have an on-call rotation, and teams usually resolve issues during business hours. However, during this particular incident, most of my colleagues were on annual leave due to an Easter break, leaving only 10 out of 70 engineers available to assist. Although none of these 10 engineers were part of the team responsible for the outage, I was familiar with their codebase and knew how to fix the problem. Additionally, I had admin access to our source control system which allowed me to merge the changes required to resolve the issue. This was the first time I had done this, but my changes were successful and the problem was resolved.
   
   Now that the break is over, the team responsible for the codebase is blaming me for breaking the process that requires each pull request to have at least one approval and for making changes to "their" codebase without their approval. They want to revoke admin access from everyone as a result. However, I disagree with their assessment. While it is true that I made changes to a codebase that was not directly under my responsibility, I was the only engineer available who could resolve the issue at the time. I believe that helping our clients should be the priority, even if it means bending the rules occasionally.
   
   Did I make a mistake by making changes to a codebase that was owned by another team without their approval? Should I have refrained from getting involved in the issue and adopted a "not my problem" attitude since the responsible team was not available?
   
   Thanks and I hope I'm not getting fired for helping a paying client!

2. J Dot Dev asks,
   
   ‌
   
   What's the worst thing you've had to do as a software engineer with direction from your employer?
   
   Years ago at a webdev shop we had a client who didn't want to pay for e-commerce set up.
   
   My boss' solution was to implement a form that included name, address, and credit card information fields that we would read on form submission and then email all of that information to our client in plain text.
   
   "Is that really ok?" I asked my boss.
   "Why wouldn't it be?"
   "Isn't that insecure?"
   "Only if they have her password. Just make it work so we can be done with them."
   
   To top it off, they also had me email the information to myself just in case the email didn't go through to the client or in case they accidentally deleted it, so I'd have all of this information just hitting my inbox.
