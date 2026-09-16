#!/usr/bin/env python3
"""
Build the static pages for speakwithkevin.

Every page shares one shell (head, nav, footer) defined here, so changing the
navigation is one edit rather than twelve. Run `python3 tools/build.py` from
the repo root; it writes the .html files in place. There is no dependency and
no install step — Vercel just serves the output.
"""

import pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent

SITE = "Kevin Koym"
YEAR = "2026"

# ── shell ────────────────────────────────────────────────────────────────────

NAV = """
<nav class="nav">
  <a class="nav-brand" href="/">Kevin Koym</a>
  <a class="nav-link{a_speaking}" href="/speaking">Speaking</a>
  <a class="nav-link{a_program}" href="/program">Program</a>
  <a class="nav-link{a_campfire}" href="/campfire">Campfire</a>
  <a class="nav-link{a_about}" href="/about">About</a>
  <a class="nav-link{a_work}" href="/work-with-me">Work with me</a>
  <a class="btn btn-primary nav-keep" href="/book">Book Kevin</a>
</nav>
"""

FOOTER = f"""
<footer class="footer">
  <div class="wrap stack">
    <div class="footer-links">
      <a href="/speaking">Speaking</a>
      <a href="/program">Program</a>
      <a href="/campfire">Campfire</a>
      <a href="/about">About</a>
      <a href="/work-with-me">Work with me</a>
      <a href="/faq">FAQ</a>
      <a href="/book">Book Kevin</a>
    </div>
    <hr class="rule">
    <p class="footer-fine">Kevin Koym · Austin, Texas · Tech Ranch · © {YEAR}</p>
  </div>
</footer>
"""

SHELL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<script src="/support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png">
<link rel="icon" type="image/png" sizes="512x512" href="/assets/favicon-512.png">
<link rel="apple-touch-icon" href="/assets/favicon-180.png">
<link rel="stylesheet" href="/_ds/orbit/styles.css">
<script src="/image-slot.js"></script>
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
</helmet>

<a class="skip" href="#main">Skip to content</a>
{nav}
<main id="main">
{body}
</main>
{footer}
{extra}
</x-dc>
</body>
</html>
"""


def page(path, title, desc, body, active=None, extra=""):
    keys = {f"a_{k}": "" for k in ("speaking", "program", "campfire", "about", "work")}
    if active:
        keys[f"a_{active}"] = '" aria-current="page'
    html = SHELL.format(
        title=title, desc=desc, body=body.strip(),
        nav=NAV.format(**keys).strip(), footer=FOOTER.strip(), extra=extra,
    )
    out = ROOT / path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html)
    return path


# ── reusable fragments ───────────────────────────────────────────────────────

def cta_band(kicker, heading, lead=None, primary=("Book Kevin to speak", "/book"),
             secondary=("Send a voice note", "https://cv.chat/kkoym")):
    lead_html = f'<p class="body">{lead}</p>' if lead else ""
    return f"""
<section class="band band-deep">
  <div class="wrap">
    <div class="stack" style="align-items:flex-start">
      <p class="eyebrow eyebrow-brick">{kicker}</p>
      <h2 class="d2" style="max-width:22ch">{heading}</h2>
      {lead_html}
      <div class="btn-row" style="margin-top:10px">
        <a class="btn btn-primary" href="{primary[1]}">{primary[0]}</a>
        <a class="btn btn-secondary" href="{secondary[1]}">{secondary[0]}</a>
      </div>
    </div>
  </div>
</section>
"""


def talk_entries(exclude=None):
    talks = [
        ("/speaking/personal-revolution",
         "Don't Just Start a Startup, Launch a Personal Revolution",
         ["Keynote", "15 / 20 min · long-form"],
         "Kennedy's two-a.m. question in 1960, my father's answer to it, and the argument that nobody is coming to ask us — so we ask each other. Closes on building a bridge, in both directions."),
        ("/speaking/market-entry",
         "U.S. Market Entry: Five Lenses for Crossing Borders",
         ["Workshop", "2–2.5 hrs", "Signature"],
         "Why Texas and Austin specifically, the second valley of death nobody plans for, and how to pick a beachhead small enough to actually win. Run as a conversation, not a lecture."),
        ("/speaking/austin-advantage",
         "Why Austin Is Overtaking Silicon Valley",
         ["Talk", "30–45 min"],
         "What international founders get wrong about the United States, and the three things you need before you land: mindset, relationships, and ecosystem fluency."),
        ("/speaking/age-of-disruption",
         "Creating a Powerful Future Together in an Age of Disruption",
         ["Talk", "~30 min"],
         "Care, connection, creation — and why the places that have already lived through the worst of it tend to understand this fastest."),
    ]
    rows = []
    for href, name, meta, desc in talks:
        if href == exclude:
            continue
        meta_html = "".join(f"<span>{m}</span>" for m in meta)
        rows.append(f"""      <a class="entry" href="{href}">
        <div>
          <h3 class="entry-title">{name}</h3>
          <div class="entry-meta">{meta_html}</div>
        </div>
        <p class="entry-desc">{desc}</p>
        <span class="entry-go">Read →</span>
      </a>""")
    return '<div class="entries">\n' + "\n\n".join(rows) + "\n    </div>"


LADDER = """
    <div class="ladder">
      <div class="rung">
        <span class="rung-n">II</span>
        <span class="rung-name">First engagements</span>
        <span class="rung-detail">Online, with your partner team. Webinars, planning, working out what your place actually needs.</span>
      </div>
      <div class="rung">
        <span class="rung-n">III</span>
        <span class="rung-name">In-person training</span>
        <span class="rung-detail">Two days in your city with roughly fifteen startups. Assessment, matching, pitching, and how to enter U.S. culture. This is the signature workshop.</span>
      </div>
      <div class="rung">
        <span class="rung-n">IV</span>
        <span class="rung-name">Virtual workshops</span>
        <span class="rung-detail">Packaging the venture — documents, culture awareness, English preparation, channel partners.</span>
      </div>
      <div class="rung">
        <span class="rung-n">V</span>
        <span class="rung-name">Austin engagement</span>
        <span class="rung-detail">One to two weeks on the ground. Investor, sales and product pitches, real meetings, and an honest go / no-go.</span>
      </div>
      <div class="rung">
        <span class="rung-n">VI</span>
        <span class="rung-name">Land and launch</span>
        <span class="rung-detail">Three to twelve months. Office, legal, operations, investment, sales, marketing.</span>
      </div>
    </div>
"""


def talk_page(slug, title, kicker, headline, lengths, abstract, takeaways,
              pull, aside_title=None, aside_items=None, desc=None):
    take = "\n".join(f"          <li>{t}</li>" for t in takeaways)
    abst = "\n".join(f'        <p class="body">{p}</p>' for p in abstract)
    aside = ""
    if aside_title:
        items = "\n".join(f"          <li>{i}</li>" for i in aside_items)
        aside = f"""
      <div class="stack">
        <p class="eyebrow">{aside_title}</p>
        <ul class="list">
{items}
        </ul>
      </div>"""

    body = f"""
<section class="band">
  <div class="wrap stack">
    <p class="eyebrow eyebrow-brick">{kicker}</p>
    <h1 class="d2" style="max-width:24ch">{title}</h1>
    <p class="lede" style="max-width:46ch">{headline}</p>
    <div class="entry-meta" style="margin-top:4px">{"".join(f"<span>{l}</span>" for l in lengths)}</div>
  </div>
</section>

<section class="band-tight band-brick">
  <div class="wrap">
    <p class="pull" style="max-width:20ch">{pull}</p>
  </div>
</section>

<section class="band">
  <div class="wrap">
    <div class="split">
      <div class="stack">
{abst}
      </div>{aside}
    </div>
  </div>
</section>

<section class="band band-deep">
  <div class="wrap">
    <div class="split">
      <div class="stack-sm">
        <p class="eyebrow eyebrow-brick">What the room leaves with</p>
      </div>
      <div class="stack">
        <ul class="list">
{take}
        </ul>
      </div>
    </div>
  </div>
</section>

<section class="band">
  <div class="wrap stack-lg">
    <div class="stack-sm">
      <p class="eyebrow eyebrow-brick">Also available</p>
      <h2 class="d3">The rest of what I speak about.</h2>
    </div>
    {talk_entries(exclude="/speaking/" + slug)}
  </div>
</section>

{cta_band("Bring it to your city", "Tell me about the room and I'll tell you what I'd do with it.")}
"""
    return page(f"speaking/{slug}.html", f"{title} — {SITE}",
                desc or headline, body, active="speaking")


# ═════════════════════════════════════════════════════════════════════════════
#  PAGES
# ═════════════════════════════════════════════════════════════════════════════

built = []

# ── home ─────────────────────────────────────────────────────────────────────

LEGACY_HASH = """
<script>
/* Old single-page anchors used to live on "/". Send them to their new homes. */
(function () {
  var map = { "#work": "/work-with-me", "#outfitter": "https://techranchaustin.com/programs/ventureoutfitter/",
              "#about": "/about", "#faq": "/faq", "#newsletter": "/campfire" };
  var dest = map[window.location.hash];
  if (dest && window.location.pathname === "/") window.location.replace(dest);
})();
</script>
"""

built.append(page("index.html",
    "Kevin Koym — Don't just start a startup",
    "Kevin Koym helped build Austin's entrepreneurial ecosystem and has carried the method to 42 countries. Keynotes, the U.S. market-entry workshop, and ecosystem programs for the places that want to build one.",
    f"""
<section class="band">
  <div class="wrap">
    <div class="split">
      <div class="stack">
        <h1 class="d1">Don't just start a&nbsp;startup.<br>Start a personal revolution.</h1>

        <p class="lede" style="max-width:44ch">Austin had nothing in 1990. One generation later it is sixth in the world — and it was never the money that did it. I've spent the last decade carrying that method to 42 countries, and I'd like to bring it to yours.</p>

        <div class="btn-row" style="margin-top:6px">
          <a class="btn btn-primary" href="/book">Book Kevin to speak</a>
          <a class="btn btn-secondary" href="https://cv.chat/kkoym">Send a voice note</a>
        </div>

        <p class="body-sm" style="max-width:46ch">If you're putting a room together, start with the first. If you're a founder in the middle of something and you need an answer today, use the second — it comes straight to me.</p>
      </div>

      <div class="stack-sm">
        <image-slot id="kevin-portrait" shape="rect" src="/assets/kevin.jpg" role="img" aria-label="Kevin Koym" class="portrait"></image-slot>
        <p class="eyebrow">Founder &amp; CEO, Tech Ranch Austin</p>
      </div>
    </div>
  </div>
</section>

<section class="band-tight band-deep">
  <div class="wrap">
    <div class="figures">
      <div class="figure"><span class="figure-n">6,500+</span><span class="figure-l">Entrepreneurs guided</span></div>
      <div class="figure"><span class="figure-n">42+</span><span class="figure-l">Countries</span></div>
      <div class="figure"><span class="figure-n">750+</span><span class="figure-l">Solutions deployed</span></div>
    </div>
  </div>
</section>

<section class="band band-brick">
  <div class="wrap">
    <div class="split">
      <div class="stack">
        <p class="pull">Revolt is against.<br>Revolution is for.</p>
      </div>
      <div class="stack">
        <p class="body">There is plenty to be against right now, and being against something is free. It costs you nothing, and by Monday it has changed nothing.</p>
        <p class="body"><strong>Liberation is getting out. Freedom is what you build instead</strong> — and almost everyone stops after the first one.</p>
        <p class="body">The talk is about that difference. What comes after it is the method Austin actually used: culture first, then capital, then change. Always in that order.</p>
      </div>
    </div>
  </div>
</section>

<section class="band">
  <div class="wrap stack-lg">
    <div class="split">
      <div class="stack-sm">
        <p class="eyebrow eyebrow-brick">What we could talk about</p>
        <h2 class="d2">Pick the one that fits your room.</h2>
      </div>
      <p class="body">Two of these are for the whole room — the evening when everyone is in one place. Two are for the founders who come back the next morning wanting to know how. You can have either. Most places end up wanting both.</p>
    </div>

    {talk_entries()}

    <div class="btn-row">
      <a class="btn btn-secondary" href="/speaking">All formats and how booking works</a>
    </div>
  </div>
</section>

<section class="band band-deep">
  <div class="wrap">
    <div class="split-even">
      <div class="stack">
        <p class="eyebrow eyebrow-brick">The signature workshop</p>
        <h2 class="d3">Every founder crossed a valley of death to start the company. Entering a new market means crossing it again.</h2>
        <p class="body">Two and a half hours with the founders in your city — deep tech, machinery, energy, e-commerce, whoever is actually trying to make the crossing. Five lenses for entering a new market, the adoption curve most companies read wrong, and how a $20&nbsp;million beachhead pulls a $4&nbsp;billion market along behind it.</p>
        <div class="btn-row">
          <a class="btn btn-primary" href="/speaking/market-entry">What's inside it</a>
        </div>
      </div>

      <div class="stack">
        <p class="eyebrow">Designed to plug into your network</p>
        <ul class="list">
          <li><strong>You bring a local founder</strong> who has already made the crossing — someone from your own ecosystem who went, and came back with something to say.</li>
          <li><strong>You bring a local attorney</strong> for the legal and practical layer: visas, entity structure, what actually changed this year.</li>
          <li><strong>I bring the method</strong>, the room, and twenty-five years of watching companies get this right and wrong.</li>
        </ul>
        <p class="body-sm">You almost certainly already know both of those people. This is built to put them to work, not to talk over them.</p>
      </div>
    </div>
  </div>
</section>

<section class="band">
  <div class="wrap stack-lg">
    <div class="split">
      <div class="stack-sm">
        <p class="eyebrow eyebrow-brick">What usually happens next</p>
        <h2 class="d2">The talk is the first phase of five.</h2>
      </div>
      <p class="body">Most places that bring me in are not buying an hour. They're trying to build something that outlasts the event. This is the shape it usually takes.</p>
    </div>
{LADDER}
    <div class="btn-row">
      <a class="btn btn-secondary" href="/program">How a place starts</a>
    </div>
  </div>
</section>

<section class="band band-brick">
  <div class="wrap">
    <div class="split-even">
      <div class="stack">
        <p class="eyebrow">After the room empties</p>
        <p class="pull">A small room beats a big list.</p>
        <p class="body">Everyone leaves an event with contacts. Almost nobody leaves with people who would actually show up for them.</p>
      </div>
      <div class="stack">
        <p class="body">A talk that ends with applause and nothing else is a wasted evening. So there is somewhere to go afterwards: <strong>Campfire</strong>, a monthly gathering that is exactly what it sounds like, and the <strong>Venture Outfitter</strong> cohort for the people who want to keep going.</p>
        <div class="btn-row">
          <a class="btn btn-primary" href="/campfire">About the campfire</a>
          <a class="btn btn-secondary" href="https://techranchaustin.com/programs/ventureoutfitter/">Venture Outfitter</a>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="band">
  <div class="wrap">
    <div class="split">
      <div class="stack">
        <p class="eyebrow eyebrow-brick">Who's talking</p>
        <h2 class="d2">I have a lot of scar tissue to donate to your process.</h2>
        <p class="body">Electrical engineering at UT Austin, with honors, in 1990 — into a city that had no jobs for its best engineers. Three and a half years at NeXT with Steve Jobs, then back to Austin anyway, because of how people there treat each other. I wrote the commerce engine that carried Dell's first two billion dollars of online sales, alone, in my living room.</p>
        <p class="body">In 2003 a friend died and none of it made sense any more. So I stopped building products and built a place for founders instead. That was Tech Ranch, and it has been twenty-three years and forty-two countries since.</p>
        <div class="btn-row">
          <a class="btn btn-secondary" href="/about">The longer version</a>
        </div>
      </div>
      <div class="stack-sm">
        <p class="eyebrow">Also</p>
        <ul class="list">
          <li>Built the first internet banking application in the world</li>
          <li>Trading systems for Fidelity, workflow for AT&amp;T</li>
          <li>Consulted on the early design of the Lean Canvas</li>
          <li>Fifth-generation Texan; first cross-border customer in Guadalajara, 1994</li>
        </ul>
      </div>
    </div>
  </div>
</section>

{cta_band("Nobody is going to ask us", "So I'm asking you. What are you trying to build?")}
""", extra=LEGACY_HASH))


# ── /speaking ────────────────────────────────────────────────────────────────

built.append(page("speaking/index.html",
    f"Speaking — {SITE}",
    "Keynotes, the signature U.S. market-entry workshop, and full ecosystem programs. How to book Kevin Koym.",
    f"""
<section class="band">
  <div class="wrap stack">
    <p class="eyebrow eyebrow-brick">Speaking</p>
    <h1 class="d2" style="max-width:20ch">A talk, a workshop, or the thing that comes after both.</h1>
    <p class="lede" style="max-width:48ch">I've spoken in forty-two countries, and the rooms that got the most out of it were the ones that treated the talk as an opening rather than an event.</p>
    <div class="btn-row" style="margin-top:8px">
      <a class="btn btn-primary" href="/book">Start a conversation</a>
    </div>
  </div>
</section>

<section class="band band-deep">
  <div class="wrap stack-lg">
    <div class="stack-sm">
      <p class="eyebrow eyebrow-brick">Formats</p>
      <h2 class="d3">Four ways this usually gets booked.</h2>
    </div>
    <div class="cols-4">
      <div class="stack-sm">
        <p class="d4">Keynote</p>
        <p class="body-sm">Fifteen or twenty minutes, or a longer version for a room that has the time. Best as the opening or closing of a day.</p>
      </div>
      <div class="stack-sm">
        <p class="d4">Workshop</p>
        <p class="body-sm">Two to two and a half hours with your founders, run as a conversation. The signature format.</p>
      </div>
      <div class="stack-sm">
        <p class="d4">Talk&nbsp;+ workshop</p>
        <p class="body-sm">The evening moves the room; the next morning puts tools in their hands. The most common booking, and the one I'd suggest.</p>
      </div>
      <div class="stack-sm">
        <p class="d4">Full program</p>
        <p class="body-sm">Where the workshop is one phase of something longer, ending with your companies on the ground in Austin.</p>
      </div>
    </div>
  </div>
</section>

<section class="band">
  <div class="wrap stack-lg">
    <div class="split">
      <div class="stack-sm">
        <p class="eyebrow eyebrow-brick">The talks</p>
        <h2 class="d2">Pick the one that fits your room.</h2>
      </div>
      <p class="body">Every one of these has been given to real audiences and rewritten after. They adapt to the room — tell me who's in yours and I'll tell you which one I'd bring.</p>
    </div>
    {talk_entries()}
  </div>
</section>

<section class="band band-deep">
  <div class="wrap">
    <div class="split-even">
      <div class="stack">
        <p class="eyebrow eyebrow-brick">What I need from you</p>
        <h2 class="d3">Two people, and a room where they can interrupt me.</h2>
        <p class="body">A keynote needs a stage and an audience. The workshop needs two people you probably already know — someone from your own ecosystem who has made the crossing, and a lawyer who can answer the visa and entity questions when they come up.</p>
        <p class="body">Beyond that: travel from Austin, and enough notice to build the trip around it.</p>
      </div>
      <div class="stack">
        <p class="eyebrow">How booking works</p>
        <ul class="list">
          <li>Send the form — it takes about two minutes and asks for the things I'd otherwise email you about.</li>
          <li>You'll hear back within a few days.</li>
          <li>We'll talk about what you're actually trying to achieve before anyone talks about a fee.</li>
        </ul>
        <div class="btn-row">
          <a class="btn btn-primary" href="/book">Book Kevin to speak</a>
        </div>
      </div>
    </div>
  </div>
</section>

{cta_band("Not sure which one fits", "Tell me about the room and I'll tell you what I'd do with it.")}
""", active="speaking"))


# ── talk pages ───────────────────────────────────────────────────────────────

built.append(talk_page(
    "personal-revolution",
    "Don't Just Start a Startup, Launch a Personal Revolution",
    "Keynote",
    "In 1960 a president asked a generation to give years of their lives to a place they had never seen. A hundred and forty thousand said yes. Nobody is going to ask us — so we have to ask each other.",
    ["15 or 20 minutes", "Long-form version available", "Opening or closing keynote"],
    [
        "It starts at two in the morning on the steps of the Michigan Union, three weeks before an election, with a senator who had no prepared remarks and a crowd of students who would not go to bed. What he asked them founded the Peace Corps. My father was one of the people who said yes.",
        "That question is not coming again. Meanwhile every arrangement people built their careers inside of is coming apart at once — which is frightening, and is also the largest opening any of us will see, because when the arrangements come apart the question of who gets to build is open again.",
        "So the talk turns on a word. Revolt is easy and free and changes nothing. Revolution, in its older sense, meant a turning back — a body coming all the way around to where it was always meant to be. Most of us were knocked out of that orbit by a salary.",
        "It ends where Austin started, and with an ask: that the room build the bridge between here and there, in both directions, starting that week.",
    ],
    [
        "The difference between being against something and being for something — and why only one of them survives to Monday morning.",
        "Why culture precedes capital, with the thirty-year Austin case as evidence rather than inspiration.",
        "The three things an entrepreneur becomes when the business stops being the point: pioneer, revolutionary, guardian — and a demand that they choose one.",
        "A concrete next step, because a room that leaves moved and unorganized has been wasted.",
    ],
    "Revolt is against.<br>Revolution is for.",
    aside_title="Best for",
    aside_items=[
        "Festival and conference main stages",
        "Ecosystem gatherings where the audience is mixed — founders, officials, students",
        "Opening a program you want people to commit to",
        "Rooms outside the United States, which is where most of these have been given",
    ],
))

built.append(talk_page(
    "market-entry",
    "U.S. Market Entry: Five Lenses for Crossing Borders",
    "Signature workshop",
    "How companies actually enter the United States, why Texas and Austin specifically, and what it takes to survive the crossing.",
    ["2–2.5 hours", "Roughly 15 companies", "Run as a conversation"],
    [
        "This runs as a conversation, not a lecture. I bring the structure — five lenses, worked examples, the numbers — and the room decides where we go deep. The questions founders ask when they are seriously considering the move are usually better than anything I had planned to say.",
        "The spine of it is a warning. Every founder in the room crossed a valley of death to start their company. Entering a new market means crossing it again, by definition — and this time with culture shock, unfamiliar norms and unpredictable policy on top. Founders forget this, and it is the single most expensive thing they forget.",
        "The rest is practical. The United States is not one market, it is at least fifty, and Texas alone has 254 counties with their own tax postures. Where you land matters. Who you sell to first matters more.",
    ],
    [
        "The five lenses: riding a disruption, reading cultural difference, the niche hypothesis, customer readiness, and entry modes.",
        "The technology adoption curve, which is the one idea I tell every room to take if they take nothing else — and the 65% principle that comes out of it.",
        "How a $20 million beachhead pulls a $200 million market, which pulls a $4 billion one. The counterintuitive part is hunting for a segment small enough to sound unimpressive.",
        "The channel partner shortcut: find the company already selling to the customers you want, instead of building the segment from scratch.",
        "Practical, unglamorous advice — including why a major conference should not be your first trip.",
    ],
    "The second crossing is harder than the first.",
    aside_title="What you bring",
    aside_items=[
        "A local founder who has already made the crossing, to open the session",
        "A local attorney for the legal layer — visas, entity structure, what changed this year",
        "Fifteen or so companies who are genuinely considering it, not merely curious",
        "A room where people can interrupt me",
    ],
))

built.append(talk_page(
    "austin-advantage",
    "Why Austin Is Overtaking Silicon Valley",
    "Talk",
    "What international founders get wrong about the United States, and the three things you need before you land.",
    ["30–45 minutes", "For founders considering the U.S.", "Pairs well with the workshop"],
    [
        "In Silicon Valley a water technology founder and a social media founder somehow end up at each other's throats despite not competing. The first question is what's your valuation. In Austin the first question is what are you building, and the honest answer is that this is not a personality difference — it is a culture that was deliberately built and is deliberately maintained.",
        "Austin was settled by hippie musicians. The norm they left behind is you play your thing, I'll play mine, and I'll help you carry your amplifier. Nobody organized that and nobody funded it. Twenty-five years later it is a global city, and every visitor expects the answer to be money. It was never money. The money came because of the culture, and it has never once gone the other way.",
        "The second half is the uncomfortable part: most international founders fail in the U.S. before they arrive. They treat it as one market. They lead with the product instead of the relationship. They undersell themselves in a market that reads confident vision as competence. And they arrive alone.",
    ],
    [
        "An honest comparison of Austin and Silicon Valley — cost, access, culture, and what each one actually rewards.",
        "The three things you need before you land: mindset, relationships, and ecosystem fluency.",
        "Why you should build the bridge before you need to cross it, and what that looks like eighteen months out.",
        "Ecosystem vocabulary that turns introductions into opportunities — angels, seed funds, accelerators, venture studios, and the government grants most founders never find.",
    ],
    "Culture first. Capital follows. Change comes.",
    aside_title="Best for",
    aside_items=[
        "Accelerator and incubator cohorts",
        "Trade missions and chamber of commerce audiences",
        "University entrepreneurship programs",
        "Any room where most people are considering the U.S. and nobody has been",
    ],
))

built.append(talk_page(
    "age-of-disruption",
    "Creating a Powerful Future Together in an Age of Disruption",
    "Talk",
    "Care, connection, creation — and why the places that have already lived through the worst of it understand this fastest.",
    ["~30 minutes", "Works as an opening or a closing", "Adapts to the host city"],
    [
        "Civilisation did not begin with fire or the wheel. It began the first time one human being cared for another. Everything since — stone, steel, silicon — has been an extension of our capacity to do that at scale, and the tools have never been more capable than they are now.",
        "Which is the argument: the future belongs to whoever can care more deeply, connect more broadly, and create more boldly. Not to whoever has the most capital, and not to whoever is loudest about disruption.",
        "This one was built first for Sarajevo, a city that knows what it is to rebuild from hardship and turn conflict into design. It works anywhere that has been underestimated, and it works especially well in rooms that are tired of being told disruption is an opportunity by people who have not lived through any.",
    ],
    [
        "Three forces — care, connection, creation — and what each one actually requires of a founder.",
        "Why collaboration beats competition on the evidence, not on sentiment: connection builds trust, and trust accelerates opportunity.",
        "A worked example from the pandemic, when founders across four countries built better solutions together than any of them could have alone.",
        "The three things everyone in the room already carries: scar tissue, relationships, and imagination.",
    ],
    "We grow stronger through the storms.",
    aside_title="Best for",
    aside_items=[
        "Cities and regions rebuilding, or reinventing",
        "Conferences with a social-impact or resilience theme",
        "Mixed audiences of founders, institutions and civil society",
        "Closing a day that has been heavy on tactics",
    ],
))


# ── /program ─────────────────────────────────────────────────────────────────

built.append(page("program/index.html",
    f"The program — {SITE}",
    "The five-phase Venture Engagement Model: from first conversations to companies landing in the United States.",
    f"""
<section class="band">
  <div class="wrap stack">
    <p class="eyebrow eyebrow-brick">The program</p>
    <h1 class="d2" style="max-width:22ch">Most places aren't looking for a speaker. They're looking for a method.</h1>
    <p class="lede" style="max-width:48ch">The ones that get the most out of this are trying to build something that outlasts the event. When that's true, the workshop is one phase of five.</p>
  </div>
</section>

<section class="band band-deep">
  <div class="wrap stack-lg">
    <div class="stack-sm">
      <p class="eyebrow eyebrow-brick">The shape of it</p>
      <h2 class="d3">Venture Engagement Model</h2>
    </div>
{LADDER}
    <p class="body-sm">Phases run at your pace. Some places do two and stop; some run the whole thing across a year. The only phase that never gets skipped is the first, because it is where we work out whether the rest is worth doing.</p>
  </div>
</section>

<section class="band">
  <div class="wrap">
    <div class="split-even">
      <div class="stack">
        <p class="eyebrow eyebrow-brick">How a place usually starts</p>
        <h2 class="d3">A talk, then a workshop, then a cohort.</h2>
        <p class="body">The keynote is where a room decides this is possible. The workshop is where the fifteen companies who meant it find out what it costs. The cohort is what happens to the ones still standing three months later.</p>
        <p class="body">You do not have to commit to all of it, and I would rather you didn't at first. Book the talk. See what the room does with it.</p>
      </div>
      <div class="stack">
        <p class="eyebrow">Who this is for</p>
        <ul class="list">
          <li>Economic development agencies with a mandate and no method</li>
          <li>Chambers of commerce and trade bodies whose members want the U.S. market</li>
          <li>Universities and accelerators with founders who are ready and unprepared</li>
          <li>Any city that has decided it wants to be more entrepreneurial and is not sure what that means in practice</li>
        </ul>
      </div>
    </div>
  </div>
</section>

<section class="band band-brick">
  <div class="wrap">
    <div class="split">
      <div class="stack">
        <p class="pull">All the world's problems have already been solved.</p>
      </div>
      <div class="stack">
        <p class="body">It is just a matter of connecting the entrepreneur with the solution to the market with the problem. That is the entire thesis, and everything above is the mechanism for doing it between two places instead of inside one.</p>
        <p class="body">Austin proved a place with nothing can become something in a generation. What I do not know yet is how well it works <strong>between</strong> places. That is what I am trying to find out, and it is why I would rather work with a city than speak at one.</p>
      </div>
    </div>
  </div>
</section>

{cta_band("Start where it makes sense", "Tell me what your city is trying to become.")}
""", active="program"))


# ── /book ────────────────────────────────────────────────────────────────────

BOOK_SCRIPT = """
<script>
(function () {
  var form = document.getElementById('book-form');
  if (!form) return;
  var status = document.getElementById('book-status');
  var submit = document.getElementById('book-submit');

  form.addEventListener('submit', async function (e) {
    e.preventDefault();
    status.textContent = '';
    status.className = '';
    submit.disabled = true;
    var original = submit.textContent;
    submit.textContent = 'Sending…';

    var data = {};
    new FormData(form).forEach(function (v, k) { data[k] = v; });

    try {
      var res = await fetch('/api/book', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      var out = await res.json().catch(function () { return {}; });

      if (res.ok) {
        form.hidden = true;
        status.className = 'alert alert-ok';
        status.textContent = "Thank you — that's with us. You'll hear back within a few days. If it's urgent, email admin@techranchaustin.com directly.";
        status.focus();
      } else {
        status.className = 'alert';
        status.textContent = (out && out.error) || 'Something went wrong sending that. Please email admin@techranchaustin.com instead — it reaches the same place.';
      }
    } catch (err) {
      status.className = 'alert';
      status.textContent = 'That could not be sent — you may be offline. Please email admin@techranchaustin.com instead.';
    } finally {
      submit.disabled = false;
      submit.textContent = original;
    }
  });
})();
</script>
"""

built.append(page("book/index.html",
    f"Book Kevin to speak — {SITE}",
    "Tell Kevin Koym about your event — format, city, audience and timing — and start the conversation.",
    """
<section class="band">
  <div class="wrap stack">
    <p class="eyebrow eyebrow-brick">Booking</p>
    <h1 class="d2" style="max-width:20ch">Tell me about the room.</h1>
    <p class="lede" style="max-width:46ch">This takes about two minutes and asks the things I'd otherwise have to email you about. The more of it you fill in, the more useful my first reply is.</p>
  </div>
</section>

<section class="band-tight" style="padding-top:0">
  <div class="wrap">
    <div class="split">
      <div>
        <p id="book-status" tabindex="-1"></p>
        <form id="book-form" class="form" novalidate>

          <div class="field-row">
            <div class="field">
              <label for="name">Your name</label>
              <input class="input" id="name" name="name" type="text" autocomplete="name" required>
            </div>
            <div class="field">
              <label for="email">Email</label>
              <input class="input" id="email" name="email" type="email" autocomplete="email" required>
            </div>
          </div>

          <div class="field-row">
            <div class="field">
              <label for="organization">Organization</label>
              <input class="input" id="organization" name="organization" type="text" autocomplete="organization">
            </div>
            <div class="field">
              <label for="role">Your role</label>
              <input class="input" id="role" name="role" type="text" autocomplete="organization-title">
            </div>
          </div>

          <div class="field">
            <label for="event">Event</label>
            <input class="input" id="event" name="event" type="text" placeholder="Name of the conference, program or gathering">
          </div>

          <div class="field-row">
            <div class="field">
              <label for="location">City and country</label>
              <input class="input" id="location" name="location" type="text" required>
            </div>
            <div class="field">
              <label for="dates">Date or window</label>
              <input class="input" id="dates" name="dates" type="text" placeholder="A date, a month, or 'not fixed yet'">
            </div>
          </div>

          <div class="field">
            <label for="format">What you're after</label>
            <select class="input" id="format" name="format" required>
              <option value="">Choose one</option>
              <option>Keynote</option>
              <option>Workshop</option>
              <option>Keynote + workshop</option>
              <option>Full ecosystem program</option>
              <option>Not sure yet — let's talk</option>
            </select>
          </div>

          <div class="field-row">
            <div class="field">
              <label for="audience_size">Audience size</label>
              <input class="input" id="audience_size" name="audience_size" type="text" placeholder="Roughly">
            </div>
            <div class="field">
              <label for="audience_type">Who's in the room</label>
              <input class="input" id="audience_type" name="audience_type" type="text" placeholder="Founders, students, officials, corporates, mixed">
            </div>
          </div>

          <div class="field">
            <label for="budget">Budget range</label>
            <select class="input" id="budget" name="budget">
              <option value="">Choose one</option>
              <option>Not sure — tell me what's typical</option>
              <option>Under $5,000</option>
              <option>$5,000 – $15,000</option>
              <option>$15,000 – $50,000</option>
              <option>Over $50,000</option>
              <option>We have no budget but read on</option>
            </select>
            <span class="hint">Asked so the first reply is useful rather than a round of guessing. It is not a filter.</span>
          </div>

          <div class="field">
            <label for="travel">Travel and accommodation</label>
            <select class="input" id="travel" name="travel">
              <option value="">Choose one</option>
              <option>Covered</option>
              <option>Partly covered</option>
              <option>Not covered</option>
              <option>Not sure yet</option>
            </select>
          </div>

          <div class="field">
            <label for="hoping">What are you hoping happens in the room?</label>
            <textarea class="input" id="hoping" name="hoping" rows="5" placeholder="The thing you actually want out of this. This is the part I read first."></textarea>
          </div>

          <div class="hp" aria-hidden="true">
            <label for="company_website">Leave this blank</label>
            <input id="company_website" name="company_website" type="text" tabindex="-1" autocomplete="off">
          </div>

          <div class="btn-row">
            <button class="btn btn-primary" id="book-submit" type="submit">Send it</button>
          </div>
        </form>
      </div>

      <div class="stack">
        <p class="eyebrow">What happens next</p>
        <ul class="list">
          <li>You'll hear back within a few days.</li>
          <li>We talk about what you're trying to achieve before anyone talks about a fee.</li>
          <li>If a talk isn't the right instrument, I'll say so. Sometimes the workshop on its own does more.</li>
        </ul>
        <hr class="rule">
        <p class="eyebrow">If you're a founder, not an organizer</p>
        <p class="body-sm">Don't use this form. Send a voice note instead — it comes straight to me and I answer them personally.</p>
        <div class="btn-row">
          <a class="btn btn-secondary" href="https://cv.chat/kkoym">Send a voice note</a>
        </div>
      </div>
    </div>
  </div>
</section>
""", extra=BOOK_SCRIPT))


# ── /about ───────────────────────────────────────────────────────────────────

built.append(page("about/index.html",
    f"About — {SITE}",
    "Kevin Koym: NeXT, Dell, the first internet banking application in the world — and then twenty-three years building Tech Ranch.",
    f"""
<section class="band">
  <div class="wrap">
    <div class="split">
      <div class="stack">
        <p class="eyebrow eyebrow-brick">About</p>
        <h1 class="d2" style="max-width:20ch">I have a lot of scar tissue to donate to your process.</h1>
        <p class="lede" style="max-width:44ch">Thirty-four years an entrepreneur, twenty-three of them building a place for other people to be one.</p>
      </div>
      <div class="stack-sm">
        <image-slot id="kevin-about" shape="rect" src="/assets/kevin.jpg" role="img" aria-label="Kevin Koym" class="portrait"></image-slot>
        <p class="eyebrow">Austin, Texas</p>
      </div>
    </div>
  </div>
</section>

<section class="band band-deep">
  <div class="wrap">
    <div class="split">
      <div class="stack-sm">
        <p class="eyebrow eyebrow-brick">The arc</p>
      </div>
      <div class="stack">
        <p class="body">I graduated in electrical engineering from the University of Texas at Austin in 1990, with honors, into a city that had no jobs for its best engineers. That is not an exaggeration — Austin in 1990 was a college town with good music and no reason for anyone to take it seriously.</p>
        <p class="body">So I went to Silicon Valley and spent three and a half years at NeXT, Steve Jobs' company, learning what technology could do to the world when someone meant it. Then I came back to Austin anyway, because of how people there treat each other.</p>
        <p class="body">What followed was the building years. A trading system for Fidelity. Workflow for AT&amp;T. The first internet banking application in the world. And the commerce engine that carried Dell's first two billion dollars of online sales, which I wrote alone, in my living room. In 1994, at twenty-four, I sold software to a bank in Guadalajara — an accidental cross-border sale that turned out to be the shape of my whole career.</p>
        <p class="body">In 2003 my friend Danielle died. She was twenty-four, with a daughter a year and a half old, and by every measure any of us used then she was winning. Afterwards none of the things I had built made sense to me, and it did not make sense to build one more.</p>
        <p class="body">So I stopped, and I built a place for founders instead. That was Tech Ranch. It has been twenty-three years, six and a half thousand entrepreneurs, and forty-two countries since.</p>
        <p class="body">It has cost me. Twice I came close enough to bankruptcy to see the bottom of it — I never declared, either time, but I want to be precise: I have sat down on a Thursday night with thirty thousand dollars due Friday morning and no idea on this earth how I was going to meet it. What got me up was not my network. My network did not know. It was one friend who found out, and came, and said what I was doing was too important to stop.</p>
      </div>
    </div>
  </div>
</section>

<section class="band band-brick">
  <div class="wrap">
    <div class="split">
      <div class="stack">
        <p class="pull">Networks are wide and they are cold. Fires are small and they are warm.</p>
      </div>
      <div class="stack">
        <p class="body">That is not a metaphor I reached for. It is the actual difference between a list of people who know your name and the two or three who would show up. Everything I have built since 2003 has been an attempt to manufacture more of the second kind.</p>
      </div>
    </div>
  </div>
</section>

<section class="band">
  <div class="wrap stack-lg">
    <div class="split">
      <div class="stack-sm">
        <p class="eyebrow eyebrow-brick">What I believe</p>
        <h2 class="d3">Five things, held stubbornly.</h2>
      </div>
      <p class="body">These are not values on a wall. They are the reasons I turn work down.</p>
    </div>
    <div class="cols-3">
      <div class="stack-sm">
        <p class="d4">Bridges over business cards</p>
        <p class="body-sm">A connection you can't act on is not a connection. The work is moving the entrepreneur, not the contact detail.</p>
      </div>
      <div class="stack-sm">
        <p class="d4">The answer already exists</p>
        <p class="body-sm">All the world's problems have already been solved somewhere. The job is connecting the solution to the market that has the problem.</p>
      </div>
      <div class="stack-sm">
        <p class="d4">Trust before transaction</p>
        <p class="body-sm">In Austin the first question is what are you building, not what's your valuation. That order is the whole advantage.</p>
      </div>
      <div class="stack-sm">
        <p class="d4">Entrepreneurship is not an individual sport</p>
        <p class="body-sm">I tried to do it alone. One ranger, one riot. It was the most expensive wrong idea I have held.</p>
      </div>
      <div class="stack-sm">
        <p class="d4">I see it; the Ranch builds it</p>
        <p class="body-sm">I am not an expert at your business. I am an expert at this process.</p>
      </div>
    </div>
  </div>
</section>

<section class="band band-deep">
  <div class="wrap">
    <div class="split">
      <div class="stack-sm">
        <p class="eyebrow eyebrow-brick">Facts, for a program</p>
      </div>
      <div class="stack">
        <ul class="list">
          <li>Founder and CEO, Tech Ranch Austin — 6,500+ entrepreneurs, 42+ countries, 750+ solutions deployed</li>
          <li>BSEE with honors, University of Texas at Austin, 1990</li>
          <li>Three and a half years at NeXT under Steve Jobs</li>
          <li>Built the first internet banking application in the world</li>
          <li>Built the e-commerce engine behind Dell's first $2 billion in online sales</li>
          <li>Consulted on the early design of the Lean Canvas</li>
          <li>Fifth-generation Texan; has lived in Boston, Chicago, Guadalajara, the Bay Area, Phoenix, Dallas, San Antonio and Santiago de Chile</li>
        </ul>
      </div>
    </div>
  </div>
</section>

{cta_band("Enough about me", "What are you trying to build?")}
""", active="about"))


# ── /campfire ────────────────────────────────────────────────────────────────

built.append(page("campfire/index.html",
    f"Campfire — {SITE}",
    "A monthly gathering for founders. Second Wednesday of the month.",
    """
<section class="band band-brick">
  <div class="wrap">
    <div class="split">
      <div class="stack">
        <p class="eyebrow">Campfire</p>
        <p class="pull">A small room beats a big list.</p>
      </div>
      <div class="stack">
        <p class="body">Everyone leaves an event with contacts. Almost nobody leaves with people who would actually show up for them. Campfire is the attempt to manufacture the second kind, once a month, on purpose.</p>
        <p class="body">It is not a panel and it is not a pitch night. People bring what they are stuck on and the room works on it.</p>
      </div>
    </div>
  </div>
</section>

<section class="band">
  <div class="wrap">
    <div class="split">
      <div class="stack">
        <p class="eyebrow eyebrow-brick">The next one</p>
        <h2 class="d2" style="max-width:16ch">Second Wednesday, every month.</h2>
        <p class="body">Dates, details and registration all live on the Tech Ranch events calendar.</p>
        <div class="btn-row">
          <a class="btn btn-primary" href="https://luma.com/techranch">See upcoming campfires</a>
        </div>
      </div>
      <div class="stack">
        <p class="eyebrow">Practical things</p>
        <ul class="list">
          <li>Once a month, second Wednesday</li>
          <li>Free</li>
          <li>Questions about a campfire go to <a href="mailto:admin@techranchaustin.com">admin@techranchaustin.com</a></li>
          <li>If you want to keep going afterwards, that\'s what the <a href="https://techranchaustin.com/programs/ventureoutfitter/">Venture Outfitter cohort</a> is</li>
        </ul>
      </div>
    </div>
  </div>
</section>

<section class="band band-deep">
  <div class="wrap">
    <div class="split-even">
      <div class="stack">
        <p class="eyebrow eyebrow-brick">What it\'s for</p>
        <h2 class="d3">The room after the room.</h2>
        <p class="body">If you heard me speak somewhere and thought there should be a next step — this is the next step. It costs nothing and it does not turn into a sales call.</p>
      </div>
      <div class="stack">
        <div class="btn-row">
          <a class="btn btn-primary" href="https://luma.com/techranch">See upcoming campfires</a>
          <a class="btn btn-secondary" href="https://techranchaustin.com/programs/ventureoutfitter/">Venture Outfitter</a>
        </div>
      </div>
    </div>
  </div>
</section>
""", active="campfire"))


# ── /work-with-me ────────────────────────────────────────────────────────────

built.append(page("work-with-me/index.html",
    f"Work with me — {SITE}",
    "Async voice coaching, the Venture Outfitter cohort, and strategic advisory for organizations.",
    """
<section class="band">
  <div class="wrap stack">
    <p class="eyebrow eyebrow-brick">For founders</p>
    <h1 class="d2" style="max-width:22ch">Tell me where you're trying to grow. I'll tell you what I see — and who you need.</h1>
    <p class="lede" style="max-width:46ch">No calendars. No forms. Just voice, the moment the decision is hot.</p>
    <div class="btn-row" style="margin-top:8px">
      <a class="btn btn-primary" href="https://cv.chat/kkoym">Send a voice note</a>
    </div>
  </div>
</section>

<section class="band band-deep">
  <div class="wrap">
    <div class="split-even">
      <div class="stack">
        <p class="eyebrow eyebrow-brick">A Tuesday, two ways</p>
        <h2 class="d3">The decision doesn't wait for your calendar to have a gap in it.</h2>
      </div>
      <div class="stack">
        <p class="body"><strong>The usual way.</strong> Something breaks on Tuesday morning. You email for time. The first slot is next week. By then you have already made the decision, badly, and the meeting becomes a post-mortem.</p>
        <p class="body"><strong>This way.</strong> Something breaks on Tuesday morning. You send me a voice note while it is still hot — no scheduling, no context-setting document. I answer within about twelve hours, having actually thought about it.</p>
      </div>
    </div>
  </div>
</section>

<section class="band">
  <div class="wrap stack-lg">
    <div class="stack-sm">
      <p class="eyebrow eyebrow-brick">Three ways in</p>
      <h2 class="d2">Pick the one that matches what you need.</h2>
    </div>

    <div class="entries">
      <a class="entry" href="https://cv.chat/kkoym">
        <div>
          <h3 class="entry-title">Breakthrough</h3>
          <div class="entry-meta"><span>One to one</span><span>Async voice</span></div>
        </div>
        <p class="entry-desc">Direct access to me by voice note, answered personally, usually within twelve hours. For founders in the middle of a decision that matters.</p>
        <span class="entry-go">Start →</span>
      </a>

      <a class="entry" href="https://techranchaustin.com/programs/ventureoutfitter/">
        <div>
          <h3 class="entry-title">Venture Outfitter</h3>
          <div class="entry-meta"><span>Cohort + community</span><span>$99/mo · $79 founding</span></div>
        </div>
        <p class="entry-desc">The program for founders who want the method rather than a single answer — structure, a cohort going through the same thing, and the community that outlasts it.</p>
        <span class="entry-go">Join →</span>
      </a>

      <a class="entry" href="/book">
        <div>
          <h3 class="entry-title">Strategic advisory</h3>
          <div class="entry-meta"><span>Organizations</span><span>Ecosystem building</span></div>
        </div>
        <p class="entry-desc">For agencies, universities and companies building an entrepreneurial ecosystem rather than a single venture. Usually starts with a talk or a workshop.</p>
        <span class="entry-go">Enquire →</span>
      </a>
    </div>
  </div>
</section>

<section class="band band-deep">
  <div class="wrap">
    <div class="split-even">
      <div class="stack">
        <p class="eyebrow eyebrow-brick">Is this for you?</p>
        <h2 class="d3">An honest test, so neither of us wastes the other's time.</h2>
      </div>
      <div class="stack">
        <p class="d4">This works if you</p>
        <ul class="list">
          <li>Would rather talk than fill in a form</li>
          <li>Are after a disruptive result, not a tidy one</li>
          <li>Can act on an answer in the week you get it</li>
          <li>Are building something that crosses a border, a sector, or a comfort zone</li>
        </ul>
        <p class="d4" style="margin-top:10px">This doesn't work if you</p>
        <ul class="list">
          <li>Want a standing weekly Zoom</li>
          <li>Need a curriculum with modules and a completion certificate</li>
          <li>Are looking for someone to validate a decision you've already made</li>
        </ul>
      </div>
    </div>
  </div>
</section>

<section class="band">
  <div class="wrap">
    <div class="split">
      <div class="stack-sm">
        <p class="eyebrow eyebrow-brick">How the one-to-one works</p>
        <h2 class="d3">Three steps, no scheduling.</h2>
      </div>
      <div class="stack">
        <ul class="list">
          <li><strong>Send a voice note.</strong> Through Carbon Voice, in whatever state your thinking is in. Unpolished is fine and usually more useful.</li>
          <li><strong>I reply within about twelve hours.</strong> By voice, having thought about it properly rather than reacting live.</li>
          <li><strong>It becomes a conversation.</strong> Most of the value shows up in the third or fourth exchange, when the real problem surfaces.</li>
        </ul>
        <div class="btn-row">
          <a class="btn btn-primary" href="https://cv.chat/kkoym">Send a voice note</a>
          <a class="btn btn-secondary" href="/faq">Questions first</a>
        </div>
      </div>
    </div>
  </div>
</section>
""", active="work"))


# ── /faq ─────────────────────────────────────────────────────────────────────

FAQS = [
    ("Is it really you replying, or a team?",
     "Me. Every voice note is answered by me personally. It is the reason there is a limit on how many of these I take at once."),
    ("How quickly do you reply?",
     "Usually within twelve hours, often faster. If I'm travelling or on stage somewhere it can be longer, and I'll say so."),
    ("What is Carbon Voice?",
     "The app the voice notes run through. You record, I listen and reply by voice. There is nothing to install if you don't want to — it works in a browser."),
    ("Can we just do a Zoom?",
     "Generally no, and not to be difficult. Live calls get scheduled for whenever both calendars are free, which is rarely when the decision is actually being made. Async voice gets you an answer in the window where it still changes something."),
    ("What does the Venture Outfitter cost?",
     "$99 a month, or $79 for founding members. It is the cohort and community program, distinct from one-to-one access."),
    ("What do you charge to speak?",
     "It depends on the format, the travel, and what else we're building around it — a keynote and a full ecosystem program are not the same conversation. Tell me about the event and I'll be straightforward with you quickly."),
    ("Do you travel?",
     "Yes, and most of this work happens outside the United States. Forty-two countries so far. Travel and accommodation are normally covered by the host."),
    ("How much notice do you need?",
     "More is better, but I have done things on three weeks' notice. Ask."),
    ("Can you speak in Spanish?",
     "I can open a room in Spanish and I do, but I deliver in English. My Spanish was learned across tables with Mexican friends and it shows."),
    ("What do you need from us for the workshop?",
     "A room where people can interrupt me, roughly fifteen companies who are seriously considering the U.S. market, a local founder who has already made the crossing, and a local attorney for the legal segment. You almost certainly have the last two already."),
    ("We're a small organization with a small budget. Is it worth asking?",
     "Yes. Ask. Some of the best work I've done started with an email that opened by apologizing for the budget."),
    ("What happens after the event?",
     "That's the part most people don't plan and it's the part that matters. There's a monthly campfire anyone from your room can join, and a cohort program for the ones who want to keep going. If you want something bigger built in your city, that's the program."),
]

faq_html = "\n".join(f"""      <div class="stack-sm">
        <p class="d4">{q}</p>
        <p class="body-sm">{a}</p>
      </div>""" for q, a in FAQS)

built.append(page("faq/index.html",
    f"FAQ — {SITE}",
    "Common questions about booking Kevin Koym to speak, the workshop, and working with him one to one.",
    f"""
<section class="band">
  <div class="wrap stack">
    <p class="eyebrow eyebrow-brick">FAQ</p>
    <h1 class="d2" style="max-width:18ch">Questions people actually ask.</h1>
  </div>
</section>

<section class="band-tight" style="padding-top:0">
  <div class="wrap">
    <div class="cols-2">
{faq_html}
    </div>
  </div>
</section>

{cta_band("Still wondering", "Ask me directly — it's faster than guessing.",
          primary=("Book Kevin to speak", "/book"))}
""", active=None))


# ── /next — the URL Kevin says from stage ────────────────────────────────────

built.append(page("next/index.html",
    f"What's next — {SITE}",
    "If you just heard Kevin speak: three things you can do about it.",
    """
<section class="band">
  <div class="wrap stack">
    <h1 class="d2" style="max-width:18ch">You just heard the talk. Here's the bridge.</h1>
    <p class="lede" style="max-width:42ch">Three things, in order of how much they ask of you. Pick one before you leave the room.</p>
  </div>
</section>

<section class="band-tight" style="padding-top:0">
  <div class="wrap">
    <div class="entries">
      <a class="entry" href="/campfire">
        <div>
          <h3 class="entry-title">Come to the next campfire</h3>
          <div class="entry-meta"><span>Free</span><span>Monthly</span></div>
        </div>
        <p class="entry-desc">A monthly gathering of founders. Bring what you're stuck on. Dates and registration on the Tech Ranch calendar.</p>
        <span class="entry-go">Dates →</span>
      </a>

      <a class="entry" href="https://cv.chat/kkoym">
        <div>
          <h3 class="entry-title">Send me a voice note</h3>
          <div class="entry-meta"><span>Direct</span><span>Answered personally</span></div>
        </div>
        <p class="entry-desc">If something in the talk hit a decision you're in the middle of — say it out loud and send it. I answer these myself.</p>
        <span class="entry-go">Start →</span>
      </a>

      <a class="entry" href="/book">
        <div>
          <h3 class="entry-title">Bring this to your city</h3>
          <div class="entry-meta"><span>Organizers</span><span>Talk · workshop · program</span></div>
        </div>
        <p class="entry-desc">If you run a program, an agency, a chamber or a university and you want the room you were just in to happen where you are.</p>
        <span class="entry-go">Enquire →</span>
      </a>
    </div>
  </div>
</section>
""", active=None))


# ── report ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    for p in built:
        print("wrote", p)
    print(f"\n{len(built)} pages")
