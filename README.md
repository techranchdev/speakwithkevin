# speakwithkevin

Static site, served by Vercel. No framework, no build step, no dependencies —
Vercel serves the HTML as-is and runs one serverless function.

## Pages

| Route | File |
| --- | --- |
| `/` | `index.html` |
| `/speaking` | `speaking/index.html` |
| `/speaking/personal-revolution` | `speaking/personal-revolution.html` |
| `/speaking/market-entry` | `speaking/market-entry.html` |
| `/speaking/austin-advantage` | `speaking/austin-advantage.html` |
| `/speaking/age-of-disruption` | `speaking/age-of-disruption.html` |
| `/program` | `program/index.html` |
| `/book` | `book/index.html` |
| `/about` | `about/index.html` |
| `/campfire` | `campfire/index.html` |
| `/work-with-me` | `work-with-me/index.html` |
| `/faq` | `faq/index.html` |
| `/next` | `next/index.html` |

Clean URLs come from `vercel.json`, which also holds the redirects, asset
caching and security headers.

## Editing content

**Do not hand-edit the `.html` files.** They are generated. Every page shares
one shell — head, nav, footer — defined once in `tools/build.py`, so a nav
change is a single edit rather than thirteen.

```
python3 tools/build.py
```

That rewrites all thirteen pages in place. Commit the generated HTML along
with the change; Vercel does not run the script.

To add a talk: add an entry to `talk_entries()` and a `talk_page(...)` call.

## Design system

`_ds/orbit/styles.css` is the whole look — color, type, and every component
class. Change the tokens at the top of that file and the entire site follows.

The previous system is still in `_ds/industry-*/` and is no longer referenced.
It can be deleted once you're confident you don't want to roll back.

## The booking form

`/book` posts JSON to `/api/book`, which emails the enquiry via Resend.
`/campfire` has no form — dates and registration live on
[the Tech Ranch Luma calendar](https://luma.com/techranch) — but the endpoint
still accepts `kind: "campfire"` if a signup form ever comes back.

### Required environment variables

Set these in Vercel → Settings → Environment Variables:

| Variable | Required | Notes |
| --- | --- | --- |
| `RESEND_API_KEY` | Yes | From resend.com/api-keys |
| `BOOKING_INBOX` | No | Defaults to `admin@techranchaustin.com` |
| `BOOKING_FROM` | No | Must be a verified Resend sender. Defaults to `bookings@techranchaustin.com` |
| `HUBSPOT_TOKEN` | No | Private app access token. Without it the HubSpot step is skipped and email still works |
| `HUBSPOT_PIPELINE` | No | Defaults to `default` |
| `HUBSPOT_DEAL_STAGE` | No | Defaults to `appointmentscheduled` |
| `HUBSPOT_OWNER_EMAIL` | No | Deal owner. Defaults to `sales@techranchaustin.com` |
| `HUBSPOT_DEAL_TYPE` | No | Defaults to `Kevin Gig Booking` |

### HubSpot

Each booking enquiry creates a Contact (matched on email, so repeat enquiries
attach to the same person) and an associated Deal carrying the full submission
in its `description`. A Note is also attempted, but only as a nicety — the
notes scope isn't offered on every HubSpot plan, so nothing depends on it. The
deal `amount` is deliberately left blank; the form collects a budget band, not
a figure.

Deals are assigned to the owner named by `HUBSPOT_OWNER_EMAIL` and tagged with
the deal type in `HUBSPOT_DEAL_TYPE`. Two prerequisites:

- that email must belong to an actual HubSpot user, and the app needs the
  `crm.objects.owners.read` scope to resolve it to an owner id
- `dealtype` is an enumeration, so the value must already exist as an option
  under Settings → Objects → Deals → Manage properties → Deal Type

If either is missing the deal is still created, just without the owner or
type, and the log line says which was rejected.

The private app needs five scopes: `crm.objects.contacts.read`,
`crm.objects.contacts.write`, `crm.objects.deals.read`,
`crm.objects.deals.write`, `crm.objects.owners.read`. Add
`crm.objects.notes.read` / `.write` too if your plan offers them.

HubSpot runs *after* the email and never blocks it. If the token expires or
a property name is wrong, the enquiry still lands in the inbox and the error
goes to the Vercel function logs. Campfire signups are not deals, so they are
emailed only.

`techranchaustin.com` must be verified as a sending domain in Resend, which
means adding DNS records. Until `RESEND_API_KEY` exists the form fails
politely — it shows an error pointing people at `admin@techranchaustin.com`
and writes the enquiry to the function logs, so nothing is lost.

The plain-text email body is deliberately formatted as `Label: value`, one
per line, so the Notion automation has an easy time parsing it. Don't
prettify it without checking that still works.

## Known open items

- Budget bands on `/book` are placeholders — set them once there's a real
  floor and ceiling.
- `/speaking` has no past-rooms section. It's the single biggest upgrade
  available to that page once Kevin signs off on which events can be named.
- Venture Outfitter pricing appears both here on `/work-with-me` and on the
  Tech Ranch program page. Two places to update when it changes.
