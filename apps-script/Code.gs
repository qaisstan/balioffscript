/**
 * Bali Off Script — lead form receiver.
 *
 * Deployed as a web app. doPost only ever APPENDS a row. doGet returns leads
 * ONLY with the private read key, which lives in this project's Script
 * properties (READ_KEY), never in this file: the repo is public. Without the
 * key the /exec URL in the page source returns nothing readable. Worst case
 * someone posts junk rows, which the honeypot and timing checks filter.
 *
 * Setup and the one-minute update steps live in README.md.
 */

// The spreadsheet to write into, taken from its URL:
// docs.google.com/spreadsheets/d/THIS_PART/edit
// Addressing it by id means this works whether the script is bound to the
// sheet or standalone. getActiveSpreadsheet() returns null when standalone,
// which fails silently and is exactly how leads go missing.
var SHEET_ID = "1JK3pIfbNCpXfZIN3Z55F8c45Ad1jfURdkn11JsYSCb8";

// Where the "New lead" alert goes. Leave "" to switch alerts off.
var NOTIFY = "hello@qaisstanikzai.com";

// The sheet's first seven columns are what the original version wrote. New
// columns go AFTER them so every older row keeps lining up under its header.
var HEADERS = ["Received", "Name", "Phone", "Budget", "Timeline", "Source", "Page", "Email", "Type", "Language", "Interest"];
var TYPES = {form: "Opportunities form", kit: "Guide download", "kit-qualify": "Guide download + budget"};


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
      new Date(),                                                   // 0 Received
      name,                                                         // 1 Name
      phone,                                                        // 2 Phone
      clean(d.budget, 40),                                          // 3 Budget
      clean(d.timeline, 40),                                        // 4 Timeline
      clean(d.ref, 200),                                            // 5 Source
      clean(d.page, 200),                                           // 6 Page
      clean(d.email, 120),                                          // 7 Email
      TYPES[d.type] || clean(d.type, 40) || "Opportunities form",   // 8 Type
      clean(d.lang, 8),                                             // 9 Language
      clean(d.interest, 80)                                         // 10 Interest
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
      subject: (wrote ? "" : "(SHEET FAILED) ") + row[8] + ": " + row[1] +
               (row[10] ? " — " + row[10] : "") + (row[3] ? " — " + row[3] : "") + (row[9] ? " [" + row[9].toUpperCase() + "]" : ""),
      body: [
        "Name:      " + row[1],
        "Phone:     " + row[2],
        "Email:     " + (row[7] || "not given"),
        "Budget:    " + (row[3] || "-"),
        "Timeline:  " + (row[4] || "-"),
        "Looking for: " + (row[10] || "-"),
        "Language:  " + (row[9] || "-"),
        "",
        "Came from: " + (row[5] || "direct"),
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
    sheet.setFrozenRows(1);
  } else if (sheet.getRange(1, HEADERS.length).getValue() !== HEADERS[HEADERS.length - 1]) {
    sheet.getRange(1, 1, 1, HEADERS.length).setValues([HEADERS]);  // add the new column names once
  }
  sheet.getRange(1, 1, 1, HEADERS.length).setFontWeight("bold");
  sheet.appendRow(row);
  return true;
}


/**
 * The Studio (Kai's local app) reads leads with the private key:
 *   GET <exec url>?key=READ_KEY&days=90
 * Without the right key this returns the same empty {ok:true} as everything else.
 */
function doGet(e) {
  var key = PropertiesService.getScriptProperties().getProperty("READ_KEY");
  var p = (e && e.parameter) || {};
  if (!key || key.length < 24 || p.key !== key) return ok();
  var days = Math.min(Math.max(parseInt(p.days, 10) || 90, 1), 730);
  var since = new Date(Date.now() - days * 864e5);
  var sheet = SpreadsheetApp.openById(SHEET_ID).getSheetByName("Leads");
  var values = sheet ? sheet.getDataRange().getValues() : [];
  var head = values.shift() || HEADERS;
  var rows = values.filter(function (r) { return r[0] instanceof Date && r[0] >= since; }).map(function (r) {
    var o = {};
    head.forEach(function (h, i) { o[String(h || ("col" + i)).toLowerCase()] = r[i] instanceof Date ? r[i].toISOString() : r[i]; });
    return o;
  });
  return ContentService.createTextOutput(JSON.stringify({ ok: true, leads: rows }))
    .setMimeType(ContentService.MimeType.JSON);
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
    page: "https://balioffscript.com/opportunities/",
    type: "form", lang: "en", interest: "A finished villa to live in or rent out"
  }) } });
}
