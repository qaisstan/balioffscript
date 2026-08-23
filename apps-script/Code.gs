/**
 * Bali Off Script — lead form receiver.
 *
 * Deployed as a web app, this only ever APPENDS a row. It has no doGet and it
 * returns nothing readable, so the public /exec URL sitting in the page source
 * cannot be used to read anyone's submission. Worst case someone posts junk
 * rows, which the honeypot and timing checks below already filter.
 *
 * Setup lives in README.md.
 */

// Where the "New lead" alert goes. Leave "" to switch alerts off.
var NOTIFY = "hello@qaisstanikzai.com";

var HEADERS = ["Received", "Name", "Phone", "Budget", "Timeline", "Source", "Page"];


function doPost(e) {
  try {
    var d = JSON.parse((e && e.postData && e.postData.contents) || "{}");

    // Honeypot: the field is invisible to people and irresistible to bots.
    if (d.hp) return ok();

    // Nobody reads and answers four questions in under two seconds.
    if (typeof d.ms === "number" && d.ms < 2000) return ok();

    var name = clean(d.name, 80);
    var phone = clean(d.phone, 40);
    if (!name || !phone) return ok();

    var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Leads") ||
                SpreadsheetApp.getActiveSpreadsheet().insertSheet("Leads");

    if (sheet.getLastRow() === 0) {
      sheet.appendRow(HEADERS);
      sheet.getRange(1, 1, 1, HEADERS.length).setFontWeight("bold");
      sheet.setFrozenRows(1);
    }

    var row = [
      new Date(),
      name,
      phone,
      clean(d.budget, 40),
      clean(d.timeline, 40),
      clean(d.ref, 200),
      clean(d.page, 200)
    ];
    sheet.appendRow(row);

    notify(row);
    return ok();

  } catch (err) {
    // Swallow the detail. An error body would tell a prober how this works.
    console.error(err);
    return ok();
  }
}


/**
 * Trim, cap, and defuse spreadsheet formula injection.
 *
 * A value starting with = + - @ or a control character is executed as a live
 * formula when the sheet opens. Prefixing an apostrophe forces Sheets to treat
 * it as text, so a submitted "=IMPORTXML(...)" stays a harmless string.
 */
function clean(v, max) {
  if (v === null || v === undefined) return "";
  var s = String(v).replace(/[\x00-\x1f\x7f]/g, " ").trim().slice(0, max || 100);
  return /^[=+\-@]/.test(s) ? "'" + s : s;
}


function notify(row) {
  if (!NOTIFY) return;
  try {
    MailApp.sendEmail({
      to: NOTIFY,
      subject: "New lead: " + row[1] + " — " + row[3],
      body: [
        "Name:      " + row[1],
        "Phone:     " + row[2],
        "Budget:    " + row[3],
        "Timeline:  " + row[4],
        "",
        "Came from: " + (row[5] || "direct"),
        "",
        SpreadsheetApp.getActiveSpreadsheet().getUrl()
      ].join("\n")
    });
  } catch (err) {
    console.error(err);   // never let a mail failure lose the row
  }
}


function ok() {
  return ContentService
    .createTextOutput(JSON.stringify({ ok: true }))
    .setMimeType(ContentService.MimeType.JSON);
}


/** Run once from the editor to confirm the sheet and the email alert work. */
function testLead() {
  doPost({ postData: { contents: JSON.stringify({
    name: "Test Person",
    phone: "+61 400000000",
    budget: "$300k to $500k",
    timeline: "Within 3 months",
    ms: 9000,
    ref: "manual test",
    page: "https://balioffscript.com/opportunities/"
  }) } });
}
