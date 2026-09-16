/**
 * POST /api/book
 *
 * Receives the booking enquiry (and the campfire signup, which sets
 * kind: "campfire") and emails it to BOOKING_INBOX via Resend.
 *
 * No dependencies on purpose — this repo has no build step, and adding one
 * for a single HTTP call would mean adding an install step to a site that
 * currently just serves files. Resend is called with plain fetch, which is
 * built into the Node runtime Vercel uses.
 *
 * Environment variables (Vercel → Settings → Environment Variables):
 *   RESEND_API_KEY   required. From resend.com/api-keys
 *   BOOKING_INBOX    optional. Defaults to admin@techranchaustin.com
 *   BOOKING_FROM     optional. Must be on a domain verified in Resend.
 *                    Defaults to bookings@techranchaustin.com
 *
 * The plain-text body is deliberately formatted as "Label: value" lines,
 * one per line, so an automation reading the email into Notion has an easy
 * time parsing it. Don't prettify it without checking that first.
 */

const INBOX = process.env.BOOKING_INBOX || "admin@techranchaustin.com";
const FROM = process.env.BOOKING_FROM || "Speak With Kevin <bookings@techranchaustin.com>";

// Field order is the order they appear in the email.
const BOOKING_FIELDS = [
  ["name", "Name"],
  ["email", "Email"],
  ["organisation", "Organisation"],
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

    return res.status(200).json({ ok: true });
  } catch (err) {
    console.error("Send failed:", err);
    console.error("Enquiry that failed to send:\n" + text);
    return res
      .status(502)
      .json({ error: "We couldn't send that just now. Please email admin@techranchaustin.com." });
  }
};
