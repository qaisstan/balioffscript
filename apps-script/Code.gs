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

// The spreadsheet to write into, taken from its URL:
// docs.google.com/spreadsheets/d/THIS_PART/edit
// Addressing it by id means this works whether the script is bound to the
// sheet or standalone. getActiveSpreadsheet() returns null when standalone,
// which fails silently and is exactly how leads go missing.
var SHEET_ID = "1JK3pIfbNCpXfZIN3Z55F8c45Ad1jfURdkn11JsYSCb8";

// Where the "New lead" alert goes. Leave "" to switch alerts off.
var NOTIFY = "hello@qaisstanikzai.com";

var HEADERS = ["Received", "Name", "Phone", "Email", "Budget", "Timeline", "Source", "Page"];


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

    var row = [
      new Date(),
      name,
      phone,
      clean(d.email, 120),
      clean(d.budget, 40),
      clean(d.timeline, 40),
      clean(d.ref, 200),
      clean(d.page, 200)
    ];

    // Write and notify independently. If the sheet is unreachable the email
    // still goes out, so the lead survives a broken spreadsheet.
    var wrote = false;
    try {
      write(row);
      wrote = true;
    } catch (sheetErr) {
      console.error("sheet write failed", sheetErr);
    }

    notify(row, wrote);
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


function notify(row, wrote) {
  if (!NOTIFY) return;
  try {
    MailApp.sendEmail({
      to: NOTIFY,
      subject: (wrote ? "New lead: " : "New lead (SHEET FAILED): ") + row[1] + " — " + row[4],
      body: [
        "Name:      " + row[1],
        "Phone:     " + row[2],
        "Email:     " + (row[3] || "not given"),
        "Budget:    " + row[4],
        "Timeline:  " + row[5],
        "",
        "Came from: " + (row[6] || "direct"),
        "",
        "https://docs.google.com/spreadsheets/d/" + SHEET_ID + "/edit"
      ].join("\n")
    });
  } catch (err) {
    console.error(err);   // never let a mail failure lose the row
  }
}


function write(row) {
  var ss = SpreadsheetApp.openById(SHEET_ID);
  var sheet = ss.getSheetByName("Leads") || ss.insertSheet("Leads");

  if (sheet.getLastRow() === 0) {
    sheet.appendRow(HEADERS);
    sheet.getRange(1, 1, 1, HEADERS.length).setFontWeight("bold");
    sheet.setFrozenRows(1);
  }
  sheet.appendRow(row);
  return true;
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
    email: "test@example.com",
    budget: "$300k to $500k",
    timeline: "Within 3 months",
    ms: 9000,
    ref: "manual test",
    page: "https://balioffscript.com/opportunities/"
  }) } });
}
