# Lead form setup

The form at `balioffscript.com/opportunities/` posts to a Google Apps Script
web app, which writes each answer into a Google Sheet you own and emails you.

Free, no submission limit, no third-party service holding your leads.

---

## One-time setup, about five minutes

**1. Make the sheet**

Go to [sheets.new](https://sheets.new). Name it `Bali Off Script — Leads`.
Nothing else to do; the script creates the tab and the headers on first use.

**2. Open the script editor**

In that sheet: **Extensions → Apps Script**.

**3. Paste the code**

Delete whatever is in `Code.gs`, paste the entire contents of the `Code.gs`
next to this file, and save (⌘S).

Check the `NOTIFY` line at the top is the address you want alerts at.
Set it to `""` if you would rather only see the sheet.

**4. Deploy**

- **Deploy → New deployment**
- Click the gear next to "Select type" → **Web app**
- Description: `lead form`
- **Execute as: Me**
- **Who has access: Anyone**  ← this is required, and it is safe (see below)
- **Deploy**

Google will ask you to authorise it. It is your own script, so click through
**Advanced → Go to (project name)** and allow it.

**5. Copy the URL**

You get a URL ending in `/exec`. Copy it. That is the whole thing.

**6. Give it to me**

Paste it in chat and I will wire it into the site and push. Or do it yourself:
put it in `LEAD_ENDPOINT` near the top of `build.py`, run `python3 build.py`,
commit and push.

---

## Testing it

In the Apps Script editor, pick `testLead` from the function dropdown and press
**Run**. A test row should appear in the sheet and an email should arrive.

Delete the test row afterwards.

---

## Why "Anyone" access is safe here

That setting sounds alarming and is worth being clear about.

The URL is visible in your page source. Anyone can find it. What matters is
what it lets them do:

- The script has **no `doGet`**. Opening the URL in a browser does nothing.
- `doPost` **only appends a row**. It never reads the sheet and never returns
  any stored data.
- Every response is the same `{ok:true}` regardless of what happened, so
  probing it tells an attacker nothing.

So the worst case is someone posting junk rows into your sheet. They cannot
read your leads, cannot see who submitted before them, and cannot reach your
Google account.

Three things already reduce the junk case:

| Guard | What it stops |
| --- | --- |
| Honeypot field | Bots that fill in every field they find |
| 2-second timing check | Scripted posts that submit instantly |
| Length caps on every field | Oversized payloads |

**Formula injection** is handled separately and matters more than spam. A value
like `=IMPORTXML(...)` typed into the form would otherwise run as a live formula
the moment you open the sheet, and could pull data out of it. `clean()` prefixes
any value starting with `=`, `+`, `-` or `@` with an apostrophe, so it stays
inert text.

---

## If the form ever breaks

The page degrades on purpose. If the endpoint is missing, unreachable, or
erroring, the form still collects all four answers and then offers a WhatsApp
link with them pre-written.

You lose the sheet row. You do not lose the lead.

---

## Changing the questions

Budget brackets and timeline options are in `build.py`, in
`opportunities_page()`. Edit the lists, rebuild, push. The sheet picks up
whatever text you set, no script change needed.
