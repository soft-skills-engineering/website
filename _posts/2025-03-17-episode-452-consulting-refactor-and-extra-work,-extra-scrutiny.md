---
layout: post
title: "Episode 452: Consulting refactor and extra work, extra scrutiny"
date: 2025-03-17 05:00:00 -0700
guid: 4141f02c-db6a-404b-bb53-392e3914825d
duration: "25:12"
length: 23629791
file: "https://dts.podtrac.com/redirect.mp3/download.softskills.audio/sse-452.mp3"
categories: episode
---

In this episode, Dave and Jamison answer these questions:

1. I've been a developer for about 1.5 years. I work for a large consultancy. we provide services to big clients. I’m working on a front-end codebase that has been through three consulting companies already.
   
   Tired of just moving tickets and fixing bugs, I decided to refactor the front end of the entire application we support. Touching the codebase to add features gave me a pit in my stomach. No integration tests, no staging environment, huge functions with tons of parameters, etc.
   
   The client provided technical guidelines that were pretty solid, but the code just didn’t follow them at all. In the time left on the contract, I refactored the codebase to fix the biggest problems to align with the client’s technical guidelines. I did all this without my manager/PO/PM asking me to.
   
   But now, how do I communicate what I’ve done to the client and my manager? Can I get any recognition for it?

2. A listener named Mike asks,
   
   I've been in my role for about 1.5 years in a dev team of 7. I really like the job, it has a good culture and I'm learning. Sometimes I channel my desire to learn into improving our projects with small, self directed changes on my own time. I these changes are useful but aren’t high enough priority to make it into planned sprint work. I don't inundate the team with these requests, it happens maybe 1-2 times a month.
   
   We make a point of working in small steps, usually submitting several PRs per day each. I really like this approach, and I also keep my occasional self-directed bits of work small in scale. However, I've noticed these PRs receive more scrutiny and more "whataboutism" that our regular on-the-books PRs.
   
   For example, for regular sprint tickets there's an understanding that we're making progressive improvements or building small pieces of features that exist within the constraints of our systems. We might flag broader improvements to consider, but there's no expectation to re-boil the ocean every time we want to merge code.
   
   When I submit a self initiated piece of work there can be a long back and forth of suggestions that can involve changing other dependent code, changing internal APIs which may have side- effects, and generally a level of defensiveness in the code that we never normally expect. I understand that by submitting off the books PRs I am requiring some work-time from reviewers, but there is more pushback than I’d expect. It feels like because I get the ball rolling on my own time the normal cost-benefit constraints go out the window, and the code purists come out to play.
   
   Could I be annoying the team with these submissions? Have you experienced team members doing the same thing? Is there a way I can scratch my own itch by learning against our systems without creating this resistance?
