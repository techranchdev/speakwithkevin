/**
 * POST /api/book
 *
 * Receives the booking enquiry (and the campfire signup, which sets
 * kind: "campfire") and:
 *
 *   1. emails it to BOOKING_INBOX via Resend
 *   2. creates a Contact and an associated Deal in HubSpot, the deal carrying
 *      the full enquiry in its description, plus a Note where the plan allows
 *
 * The email goes first and HubSpot is best-effort. If HubSpot is down, the
 * token has expired, or a property name is wrong, the enquiry still reaches
 * the inbox and the failure is written to the function logs. A CRM outage
 * must never cost a lead.
 *
 * No dependencies on purpose — this repo has no build step, and adding one
 * for two HTTP calls would mean adding an install step to a site that
 * currently just serves files. Both APIs are called with plain fetch, which
 * is built into the Node runtime Vercel uses.
 *
 * Environment variables (Vercel → Settings → Environment Variables):
 *   RESEND_API_KEY       required for email. From resend.com/api-keys
 *   BOOKING_INBOX        optional. Defaults to admin@techranchaustin.com
 *   BOOKING_FROM         optional. Must be a verified Resend sender.
 *   HUBSPOT_TOKEN        optional. Private app access token. Without it the
 *                        HubSpot step is skipped silently and email still works.
 *   HUBSPOT_PIPELINE     optional. Pipeline name or id. Blank picks the one
 *                        containing the named stage.
 *   HUBSPOT_DEAL_STAGE   optional. Stage name or id. Defaults to "New Prospect"
 *   HUBSPOT_OWNER_EMAIL  optional. Defaults to sales@techranchaustin.com
 *   HUBSPOT_DEAL_TYPE    optional. Defaults to "Kevin Gig Booking"
 *
 * The plain-text email body is deliberately formatted as "Label: value"
 * lines, one per line, so an automation reading it into Notion has an easy
 * time parsing it. Don't prettify it without checking that first.
 */

const INBOX = process.env.BOOKING_INBOX || "admin@techranchaustin.com";
const FROM = process.env.BOOKING_FROM || "Speak With Kevin <bookings@techranchaustin.com>";

const HS = "https://api.hubapi.com";
const HS_PIPELINE = process.env.HUBSPOT_PIPELINE || "";
const HS_STAGE = process.env.HUBSPOT_DEAL_STAGE || "New Prospect";
const HS_OWNER_EMAIL = process.env.HUBSPOT_OWNER_EMAIL || "sales@techranchaustin.com";
const HS_DEAL_TYPE = process.env.HUBSPOT_DEAL_TYPE || "Kevin Gig Booking";

// HubSpot-defined association type ids. Stable, but if any of these are ever
// wrong the record is still created — only the link is missing, and that's
// logged rather than thrown.
const ASSOC = { DEAL_TO_CONTACT: 3, NOTE_TO_CONTACT: 202, NOTE_TO_DEAL: 214 };

// Field order is the order they appear in the email and the note.
const BOOKING_FIELDS = [
  ["name", "Name"],
  ["email", "Email"],
  ["organisation", "Organization"],
  ["role", "Role"],
  ["event", "Event"],
  ["location", "Location"],
  ["dates", "Dates"],
  ["format", "Format"],
  ["audience_size", "Audience size"],
  ["audience_type", "Audience type"],
  ["budget", "Budget"],
  ["travel", "Travel covered"],
  ["hoping", "Hoping for"],
];

const CAMPFIRE_FIELDS = [
  ["name", "Name"],
  ["email", "Email"],
  ["building", "Building"],
];

const clean = (v) =>
  typeof v === "string" ? v.replace(/\s+/g, " ").trim().slice(0, 4000) : "";

const isEmail = (v) => /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v);

const escapeHtml = (v) =>
  String(v).replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])
  );

/** "Paloma Kuri" -> { firstname: "Paloma", lastname: "Kuri" } */
function splitName(full) {
  const parts = full.split(" ").filter(Boolean);
  if (parts.length < 2) return { firstname: full, lastname: "" };
  return { firstname: parts[0], lastname: parts.slice(1).join(" ") };
}

async function hubspot(path, body, token, method = "POST") {
  const res = await fetch(HS + path, {
    method,
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  const text = await res.text().catch(() => "");
  let json = null;
  try {
    json = text ? JSON.parse(text) : null;
  } catch {
    /* non-JSON error body; keep the raw text for the log */
  }
  return { ok: res.ok, status: res.status, json, text };
}

/**
 * Create or find the contact. HubSpot answers a duplicate create with 409 and
 * puts the existing record's id in the error message, which is the documented
 * way to do create-or-get in one round trip. Batch upsert is not used here:
 * it doesn't support partial upserts when the idProperty is email, so it can't
 * create a contact that doesn't exist yet.
 */
async function upsertContact(token, { email, name, organisation, role }) {
  const { firstname, lastname } = splitName(name);
  const properties = { email };
  if (firstname) properties.firstname = firstname;
  if (lastname) properties.lastname = lastname;
  if (organisation) properties.company = organisation;
  if (role) properties.jobtitle = role;

  const created = await hubspot("/crm/v3/objects/contacts", { properties }, token);
  if (created.ok && created.json && created.json.id) return created.json.id;

  if (created.status === 409) {
    // "Contact already exists. Existing ID: 123456789"
    const match = (created.json && created.json.message ? created.json.message : created.text).match(/\d{4,}/);
    if (match) return match[0];
  }

  throw new Error(`contact create failed (${created.status}): ${created.text.slice(0, 400)}`);
}

/**
 * Pipelines and stages are addressed by internal id, but ids are invisible in
 * the HubSpot UI and differ per portal — so the config names them in plain
 * English and this resolves them. Matching is case-insensitive and accepts
 * either the label ("New Prospect") or the raw id, so both styles work.
 *
 * If HUBSPOT_PIPELINE is blank, the pipeline containing the named stage wins;
 * failing that, the first pipeline. If the lookup itself fails, the configured
 * values are passed through unchanged and HubSpot gets the final say.
 */
async function resolvePipeline(token) {
  const res = await hubspot("/crm/v3/pipelines/deals", null, token, "GET");
  if (!res.ok || !res.json || !Array.isArray(res.json.results)) {
    console.error(`HubSpot pipeline lookup failed (${res.status}): ${res.text.slice(0, 200)}`);
    return { pipeline: HS_PIPELINE || undefined, stage: HS_STAGE, resolved: false };
  }

  const pipelines = res.json.results;
  const eq = (a, b) => String(a).trim().toLowerCase() === String(b).trim().toLowerCase();
  const findStage = (pl) =>
    (pl.stages || []).find((st) => eq(st.label, HS_STAGE) || eq(st.id, HS_STAGE));

  let pipeline = HS_PIPELINE
    ? pipelines.find((pl) => eq(pl.label, HS_PIPELINE) || eq(pl.id, HS_PIPELINE))
    : pipelines.find((pl) => findStage(pl));

  if (!pipeline) pipeline = pipelines[0];
  if (!pipeline) return { pipeline: undefined, stage: HS_STAGE, resolved: false };

  const stage = findStage(pipeline);
  if (!stage) {
    console.error(
      `HubSpot stage "${HS_STAGE}" not found in pipeline "${pipeline.label}". ` +
        `Available: ${(pipeline.stages || []).map((st) => st.label).join(", ")}`
    );
    // Fall back to the pipeline's first stage rather than failing the create.
    const first = (pipeline.stages || [])[0];
    return {
      pipeline: pipeline.id,
      stage: first ? first.id : undefined,
      label: `${pipeline.label} / ${first ? first.label : "?"} (fallback)`,
      resolved: false,
    };
  }

  return {
    pipeline: pipeline.id,
    stage: stage.id,
    label: `${pipeline.label} / ${stage.label}`,
    resolved: true,
  };
}

/**
 * Deals are owned by a user id, not an email, so the address has to be
 * resolved first. Needs the crm.objects.owners.read scope; without it this
 * returns null and the deal is simply created unowned.
 */
async function findOwnerId(token, email) {
  if (!email) return null;
  const res = await hubspot(
    `/crm/v3/owners?email=${encodeURIComponent(email)}&limit=1`,
    null,
    token,
    "GET"
  );
  if (res.ok && res.json && Array.isArray(res.json.results) && res.json.results.length) {
    return res.json.results[0].id;
  }
  console.error(`HubSpot owner lookup failed for ${email} (${res.status}): ${res.text.slice(0, 200)}`);
  return null;
}

async function createDeal(token, contactId, { name, organisation, format }, fullText, ownerId, pl) {
  const who = organisation || name;
  const what = format && format !== "Not sure yet — let's talk" ? format : "Speaking enquiry";

  // The whole enquiry goes on the deal itself. Notes are nicer in the HubSpot
  // timeline, but they need a scope that isn't available on every plan — so
  // nothing important is allowed to depend on them.
  const description = fullText;

  // Core properties always succeed. Owner and deal type are added on top and
  // can be rejected — dealtype is an enumeration, so "Kevin Gig Booking" has
  // to exist as an option in HubSpot before it will be accepted.
  const core = {
    dealname: `${who} — ${what}`,
    ...(pl.pipeline ? { pipeline: pl.pipeline } : {}),
    ...(pl.stage ? { dealstage: pl.stage } : {}),
    // amount deliberately left unset — the form collects a band, not a figure
    ...(description ? { description } : {}),
  };

  const extras = {};
  if (ownerId) extras.hubspot_owner_id = ownerId;
  if (HS_DEAL_TYPE) extras.dealtype = HS_DEAL_TYPE;

  const body = {
    properties: { ...core, ...extras },
    associations: [
      {
        to: { id: contactId },
        types: [
          {
            associationCategory: "HUBSPOT_DEFINED",
            associationTypeId: ASSOC.DEAL_TO_CONTACT,
          },
        ],
      },
    ],
  };

  let res = await hubspot("/crm/v3/objects/deals", body, token);

  // A rejected owner or deal type must not cost us the deal. Retry with the
  // core properties only, and log what was dropped so it can be fixed.
  if (!res.ok && Object.keys(extras).length) {
    console.error(
      `HubSpot deal rejected with owner/type (${res.status}): ${res.text.slice(0, 300)} — retrying without them`
    );
    body.properties = core;
    res = await hubspot("/crm/v3/objects/deals", body, token);
  }

  if (!res.ok || !res.json || !res.json.id) {
    throw new Error(`deal create failed (${res.status}): ${res.text.slice(0, 400)}`);
  }
  return res.json.id;
}

async function createNote(token, contactId, dealId, text) {
  const body = {
    properties: {
      hs_timestamp: new Date().toISOString(),
      hs_note_body: text.replace(/\n/g, "<br>"),
    },
    associations: [
      {
        to: { id: contactId },
        types: [
          { associationCategory: "HUBSPOT_DEFINED", associationTypeId: ASSOC.NOTE_TO_CONTACT },
        ],
      },
      {
        to: { id: dealId },
        types: [
          { associationCategory: "HUBSPOT_DEFINED", associationTypeId: ASSOC.NOTE_TO_DEAL },
        ],
      },
    ],
  };
  const res = await hubspot("/crm/v3/objects/notes", body, token);
  if (!res.ok) {
    throw new Error(`note create failed (${res.status}): ${res.text.slice(0, 400)}`);
  }
}

// CommonJS on purpose: there is no package.json in this repo, so the Vercel
// Node runtime treats .js as CommonJS. `export default` would fail at runtime.
module.exports = async function handler(req, res) {
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    return res.status(405).json({ error: "Method not allowed." });
  }

  let body = req.body;
  if (typeof body === "string") {
    try {
      body = JSON.parse(body);
    } catch {
      return res.status(400).json({ error: "Could not read that submission." });
    }
  }
  if (!body || typeof body !== "object") {
    return res.status(400).json({ error: "Could not read that submission." });
  }

  // Honeypot. Bots fill hidden fields; people don't. Answer 200 so the bot
  // believes it succeeded and doesn't retry with a different shape.
  if (clean(body.company_website)) {
    return res.status(200).json({ ok: true });
  }

  const isCampfire = body.kind === "campfire";
  const fields = isCampfire ? CAMPFIRE_FIELDS : BOOKING_FIELDS;

  const name = clean(body.name);
  const email = clean(body.email);

  if (!name) return res.status(400).json({ error: "Please include your name." });
  if (!isEmail(email))
    return res.status(400).json({ error: "That email address doesn't look right." });
  if (!isCampfire && !clean(body.location))
    return res.status(400).json({ error: "Please include the city and country." });

  const rows = fields
    .map(([key, label]) => [label, clean(body[key])])
    .filter(([, value]) => value);

  const subject = isCampfire
    ? `Campfire signup: ${name}`
    : `Speaking enquiry: ${name}${clean(body.organisation) ? " — " + clean(body.organisation) : ""}`;

  // Plain text: one "Label: value" per line, nothing else. Parser-friendly.
  const text = rows.map(([label, value]) => `${label}: ${value}`).join("\n");

  const html =
    `<table cellpadding="6" style="font-family:system-ui,sans-serif;font-size:14px;border-collapse:collapse">` +
    rows
      .map(
        ([label, value]) =>
          `<tr><td style="vertical-align:top;color:#666;white-space:nowrap">${escapeHtml(
            label
          )}</td><td style="vertical-align:top"><strong>${escapeHtml(value)}</strong></td></tr>`
      )
      .join("") +
    `</table>`;

  // ── 1. Email, via Resend ───────────────────────────────────────────────
  const key = process.env.RESEND_API_KEY;
  if (!key) {
    // Don't lose the enquiry silently — it's in the function logs at least.
    console.error("RESEND_API_KEY is not set. Enquiry received but not emailed:\n" + text);
    return res
      .status(500)
      .json({ error: "We couldn't send that just now. Please email admin@techranchaustin.com." });
  }

  try {
    const resend = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${key}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        from: FROM,
        to: [INBOX],
        reply_to: email,
        subject,
        text,
        html,
      }),
    });

    if (!resend.ok) {
      const detail = await resend.text().catch(() => "");
      console.error("Resend rejected the send:", resend.status, detail);
      console.error("Enquiry that failed to send:\n" + text);
      return res
        .status(502)
        .json({ error: "We couldn't send that just now. Please email admin@techranchaustin.com." });
    }
  } catch (err) {
    console.error("Send failed:", err);
    console.error("Enquiry that failed to send:\n" + text);
    return res
      .status(502)
      .json({ error: "We couldn't send that just now. Please email admin@techranchaustin.com." });
  }

  // ── 2. HubSpot, best-effort ────────────────────────────────────────────
  // Campfire signups are not deals, so they only reach the inbox.
  const hsToken = process.env.HUBSPOT_TOKEN;
  if (hsToken && !isCampfire) {
    try {
      const contactId = await upsertContact(hsToken, {
        email,
        name,
        organisation: clean(body.organisation),
        role: clean(body.role),
      });

      const [ownerId, pl] = await Promise.all([
        findOwnerId(hsToken, HS_OWNER_EMAIL),
        resolvePipeline(hsToken),
      ]);

      const dealId = await createDeal(
        hsToken,
        contactId,
        { name, organisation: clean(body.organisation), format: clean(body.format) },
        text,
        ownerId,
        pl
      );

      try {
        await createNote(hsToken, contactId, dealId, text);
      } catch (noteErr) {
        // The deal exists and is associated; only the detail note is missing.
        // Expected on plans without a notes scope. The deal already carries
        // the full enquiry in its description, so nothing is lost.
        console.error("HubSpot note skipped (deal", dealId, "has the detail):", noteErr.message);
      }

      // Say exactly what landed, so "is the owner/type/stage right?" is
      // answerable from the logs without opening HubSpot.
      console.log(
        `HubSpot: deal ${dealId} for ${email} — contact=${contactId} ` +
          `stage=${pl.label || pl.stage || "(default)"} ` +
          `owner=${ownerId ? `${HS_OWNER_EMAIL} (${ownerId})` : "NOT SET"} ` +
          `type=${HS_DEAL_TYPE || "(none)"}`
      );
    } catch (err) {
      // Deliberately swallowed. The email already went out, so the enquiry is
      // safe; this is a CRM problem to fix, not a reason to fail the visitor.
      console.error("HubSpot step failed:", err.message);
      console.error("Enquiry that did not reach HubSpot:\n" + text);
    }
  }

  return res.status(200).json({ ok: true });
};
