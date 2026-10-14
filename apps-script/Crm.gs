/**
 * Kai's CRM (14 Oct 2026). Lives in the same Apps Script project as the lead form (Code.gs).
 *
 * Open it through a SECOND web app deployment set to "Execute as: Me" and "Who has access: Only myself".
 * Google asks for Kai's login; crmPage() also refuses anyone who is not OWNER, so the public lead-form
 * deployment can never show it. No secrets live in this file (the repo is public).
 *
 * Tabs in the sheet: Meetings (people Kai has met, his own or Coco's), Messages (ready WhatsApp texts),
 * Analytics (a snapshot the Studio on the Mac pushes every hour). Website leads stay in "Leads".
 */
var OWNER = "hello@qaisstanikzai.com";
var M_HEAD = ["Id", "Name", "Phone", "Source", "Meeting date", "Status", "Next follow-up", "Last contact", "Notes", "Added", "Next type"];
var MSG_HEAD = ["Id", "Title", "Text", "Kind"];
var DAY = 864e5;
// Kai, 14 Oct 2026: two touches a week, alternating. A "Vibe" (a Bali b-roll, I'm here, good energy) and a real
// "Follow-up" (their plans). Vibe, then the follow-up 3 days later, then the next vibe 4 days after that.

function crmPage() {
  if (String(Session.getActiveUser().getEmail() || "").toLowerCase() !== OWNER) return null;
  return HtmlService.createHtmlOutputFromFile("CrmPage")
    .setTitle("Bali CRM")
    .addMetaTag("viewport", "width=device-width, initial-scale=1, maximum-scale=1");
}

function guard_() {
  if (String(Session.getActiveUser().getEmail() || "").toLowerCase() !== OWNER) throw new Error("Not allowed");
}

function tab_(name, head) {
  var ss = SpreadsheetApp.openById(SHEET_ID);
  var sh = ss.getSheetByName(name);
  if (!sh) {
    sh = ss.insertSheet(name);
    sh.getRange(1, 1, 1, head.length).setValues([head]).setFontWeight("bold");
    sh.setFrozenRows(1);
  }
  return sh;
}

function day_(d) { return Utilities.formatDate(d, "Asia/Makassar", "yyyy-MM-dd"); }

function rows_(sh, head) {
  var v = sh.getDataRange().getValues();
  v.shift();
  return v.filter(function (r) { return r[0] !== ""; }).map(function (r) {
    var o = {};
    head.forEach(function (h, i) { o[h] = r[i] instanceof Date ? day_(r[i]) : r[i]; });
    return o;
  });
}

function seedMessages_(sh) {
  if (sh.getLastRow() > 1) return;
  var m = [
    ["v1", "Morning view", "Morning from Bali {name} 🌴 Had to share this one with you.", "Vibe"],
    ["v2", "Beach day", "Hey {name}! Spent the afternoon at the beach today, sending you a little piece of it.", "Vibe"],
    ["v3", "Sunset", "The sunset here tonight was something else {name}. Sending you a quick video.", "Vibe"],
    ["f1", "Check in", "Hi {name}, how are things going? Anything new with your Bali plans?", "Follow-up"],
    ["f2", "Something that fits", "Hey {name}, I came across something that could fit what you told me. Want me to send you the details?", "Follow-up"],
    ["f3", "Quick call", "Hi {name}, would a quick call this week help? Happy to go through any questions about Bali.", "Follow-up"]
  ];
  sh.getRange(2, 1, m.length, 4).setValues(m);
}

/** Everything the page needs in one call. */
function crmLoad() {
  guard_();
  var ms = tab_("Meetings", M_HEAD), msg = tab_("Messages", MSG_HEAD);
  seedMessages_(msg);
  var ss = SpreadsheetApp.openById(SHEET_ID);
  var leads = [], lsh = ss.getSheetByName("Leads");
  if (lsh) {
    var v = lsh.getDataRange().getValues();
    var head = v.shift();
    var col = function (n) { return head.indexOf(n); };
    var since = new Date(Date.now() - 120 * 864e5);
    v.forEach(function (r, i) {
      if (!(r[0] instanceof Date) || r[0] < since) return;
      leads.push({ row: i + 2, received: day_(r[0]), name: String(r[col("Name")] || "").replace(/^'/, ""),
                   phone: String(r[col("Phone")] || "").replace(/^'/, ""), type: r[col("Type")], interest: r[col("Interest")],
                   timeline: r[col("Timeline")], budget: r[col("Budget")] });
    });
    leads.reverse();
  }
  var a = ss.getSheetByName("Analytics");
  var analytics = null;
  if (a) { try { analytics = JSON.parse(a.getRange(1, 1).getValue() || "null"); } catch (e) {} }
  return { today: day_(new Date()), meetings: rows_(ms, M_HEAD), messages: rows_(msg, MSG_HEAD), leads: leads, analytics: analytics };
}

function findRow_(sh, id) {
  var ids = sh.getRange(2, 1, Math.max(sh.getLastRow() - 1, 1), 1).getValues();
  for (var i = 0; i < ids.length; i++) if (String(ids[i][0]) === String(id)) return i + 2;
  throw new Error("Not found");
}

function note_(old, text) {
  var stamp = Utilities.formatDate(new Date(), "Asia/Makassar", "d MMM");
  return (stamp + ": " + text + (old ? "\n" + old : "")).slice(0, 45000);
}

function crmAddMeeting(m) {
  guard_();
  var sh = tab_("Meetings", M_HEAD);
  var met = m.date ? new Date(m.date + "T12:00:00+08:00") : new Date();
  var id = "k" + Date.now().toString(36);
  sh.appendRow([id, String(m.name || "").slice(0, 80), "'" + String(m.phone || "").slice(0, 40), m.source === "Coco" ? "Coco" : "Mine",
                met, "Following up", new Date(met.getTime() + 3 * DAY), "", m.note ? note_("", m.note) : "", new Date(), "Vibe"]);
  return crmLoad();
}

function crmUpdate(id, patch) {
  guard_();
  var sh = tab_("Meetings", M_HEAD), r = findRow_(sh, id);
  if (patch.status) sh.getRange(r, 6).setValue(patch.status === "Not interested" ? "Not interested" : "Following up");
  if (patch.next) sh.getRange(r, 7).setValue(new Date(patch.next + "T12:00:00+08:00"));
  if (patch.note) sh.getRange(r, 9).setValue(note_(sh.getRange(r, 9).getValue(), String(patch.note).slice(0, 2000)));
  if (patch.phone) sh.getRange(r, 3).setValue("'" + String(patch.phone).slice(0, 40));
  return crmLoad();
}

/** Kai sent the message that was due: log it, switch Vibe <-> Follow-up and set the next date. */
function crmSent(id, title) {
  guard_();
  var sh = tab_("Meetings", M_HEAD), r = findRow_(sh, id), now = new Date();
  var kind = sh.getRange(r, 11).getValue() === "Follow-up" ? "Follow-up" : "Vibe";
  sh.getRange(r, 7, 1, 2).setValues([[new Date(now.getTime() + (kind === "Vibe" ? 3 : 4) * DAY), now]]);
  sh.getRange(r, 11).setValue(kind === "Vibe" ? "Follow-up" : "Vibe");
  sh.getRange(r, 9).setValue(note_(sh.getRange(r, 9).getValue(), "sent " + kind.toLowerCase() + ": " + (title || "a message")));
  return crmLoad();
}

function crmMoveLead(row) {
  guard_();
  var lsh = SpreadsheetApp.openById(SHEET_ID).getSheetByName("Leads");
  var head = lsh.getRange(1, 1, 1, lsh.getLastColumn()).getValues()[0];
  var r = lsh.getRange(row, 1, 1, head.length).getValues()[0];
  var g = function (n) { return String(r[head.indexOf(n)] || "").replace(/^'/, ""); };
  var bits = [g("Interest"), g("Timeline"), g("Budget")].filter(String).join(", ");
  return crmAddMeeting({ name: g("Name"), phone: g("Phone"), source: "Mine", date: day_(new Date()),
                         note: "from the website" + (bits ? ": " + bits : "") });
}

function crmSaveMessage(m) {
  guard_();
  var sh = tab_("Messages", MSG_HEAD);
  if (m.id) {
    var r = findRow_(sh, m.id);
    sh.getRange(r, 2, 1, 3).setValues([[String(m.title).slice(0, 80), String(m.text).slice(0, 2000), m.kind === "Follow-up" ? "Follow-up" : "Vibe"]]);
  } else {
    sh.appendRow(["m" + Date.now().toString(36), String(m.title).slice(0, 80), String(m.text).slice(0, 2000),
                  m.kind === "Follow-up" ? "Follow-up" : "Vibe"]);
  }
  return crmLoad();
}

function crmDeleteMessage(id) {
  guard_();
  var sh = tab_("Messages", MSG_HEAD);
  sh.deleteRow(findRow_(sh, id));
  return crmLoad();
}

/** Called from doPost with the Studio's key. Keeps the latest snapshot in Analytics!A1. */
function saveAnalytics(d) {
  var key = PropertiesService.getScriptProperties().getProperty("READ_KEY");
  if (!key || key.length < 24 || d.key !== key) return ok();
  var sh = tab_("Analytics", ["snapshot"]);
  sh.getRange(1, 1).setValue(JSON.stringify(d.data || {}).slice(0, 49000));
  return ok();
}
