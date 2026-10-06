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
    sendGuide(d, row);
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


/* ------------------------------------------------------------------------
 * CRM on top of the Leads tab. Run once: reload the sheet, then the menu
 * "🏝️ CRM → Set up the CRM". Safe to run again (it only repairs).
 * The website's 11 columns stay exactly where they are; the CRM columns sit
 * to the right of them, so new leads keep landing in the right place.
 * ---------------------------------------------------------------------- */
var CRM = ["Grade", "Country", "Status", "Next step", "Follow-up", "Last contact", "Notes"];
// Country from the phone's dialling code (longest match first)
var CODES = {"1": "🇺🇸 US / Canada", "7": "🇷🇺 Russia", "20": "🇪🇬 Egypt", "27": "🇿🇦 South Africa", "30": "🇬🇷 Greece",
  "31": "🇳🇱 Netherlands", "32": "🇧🇪 Belgium", "33": "🇫🇷 France", "34": "🇪🇸 Spain", "36": "🇭🇺 Hungary", "39": "🇮🇹 Italy",
  "40": "🇷🇴 Romania", "41": "🇨🇭 Switzerland", "43": "🇦🇹 Austria", "44": "🇬🇧 UK", "45": "🇩🇰 Denmark", "46": "🇸🇪 Sweden",
  "47": "🇳🇴 Norway", "48": "🇵🇱 Poland", "49": "🇩🇪 Germany", "51": "🇵🇪 Peru", "52": "🇲🇽 Mexico", "54": "🇦🇷 Argentina",
  "55": "🇧🇷 Brazil", "56": "🇨🇱 Chile", "57": "🇨🇴 Colombia", "60": "🇲🇾 Malaysia", "61": "🇦🇺 Australia", "62": "🇮🇩 Indonesia",
  "63": "🇵🇭 Philippines", "64": "🇳🇿 New Zealand", "65": "🇸🇬 Singapore", "66": "🇹🇭 Thailand", "81": "🇯🇵 Japan",
  "82": "🇰🇷 South Korea", "84": "🇻🇳 Vietnam", "86": "🇨🇳 China", "90": "🇹🇷 Turkey", "91": "🇮🇳 India", "92": "🇵🇰 Pakistan",
  "93": "🇦🇫 Afghanistan", "94": "🇱🇰 Sri Lanka", "95": "🇲🇲 Myanmar", "98": "🇮🇷 Iran", "212": "🇲🇦 Morocco", "234": "🇳🇬 Nigeria",
  "254": "🇰🇪 Kenya", "351": "🇵🇹 Portugal", "352": "🇱🇺 Luxembourg", "353": "🇮🇪 Ireland", "354": "🇮🇸 Iceland", "355": "🇦🇱 Albania",
  "356": "🇲🇹 Malta", "357": "🇨🇾 Cyprus", "358": "🇫🇮 Finland", "359": "🇧🇬 Bulgaria", "370": "🇱🇹 Lithuania", "371": "🇱🇻 Latvia",
  "372": "🇪🇪 Estonia", "377": "🇲🇨 Monaco", "380": "🇺🇦 Ukraine", "381": "🇷🇸 Serbia", "385": "🇭🇷 Croatia", "386": "🇸🇮 Slovenia",
  "420": "🇨🇿 Czechia", "421": "🇸🇰 Slovakia", "673": "🇧🇳 Brunei", "852": "🇭🇰 Hong Kong", "855": "🇰🇭 Cambodia", "856": "🇱🇦 Laos",
  "880": "🇧🇩 Bangladesh", "886": "🇹🇼 Taiwan", "965": "🇰🇼 Kuwait", "966": "🇸🇦 Saudi Arabia", "968": "🇴🇲 Oman",
  "971": "🇦🇪 UAE", "972": "🇮🇱 Israel", "973": "🇧🇭 Bahrain", "974": "🇶🇦 Qatar", "977": "🇳🇵 Nepal"};
var STATUSES = ["New", "Contacted", "Qualified", "Call booked", "Viewing", "Offer", "Won", "Lost", "Not a fit"];

function onOpen() {
  try { SpreadsheetApp.getUi(); } catch (err) { return; }   // only when the script lives in the sheet
  SpreadsheetApp.getUi().createMenu("🏝️ CRM")
    .addItem("Set up the CRM", "setupCrm")
    .addItem("Send a test lead", "testLead")
    .addToUi();
}

// Changing a lead's Status stamps today's date in "Last contact".
function onEdit(e) {
  var r = e && e.range;
  if (!r || r.getSheet().getName() !== "Leads" || r.getRow() < 2) return;
  var col = HEADERS.length + 3;                       // Status column
  if (r.getColumn() === col && r.getNumColumns() === 1) {
    r.getSheet().getRange(r.getRow(), HEADERS.length + 6).setValue(new Date());
  }
}

function setupCrm() {
  var ss = SpreadsheetApp.openById(SHEET_ID);
  var sh = ss.getSheetByName("Leads") || ss.insertSheet("Leads");
  var n = HEADERS.length, last = n + CRM.length, rows = Math.max(sh.getMaxRows(), 1000);
  if (sh.getMaxRows() < rows) sh.insertRowsAfter(sh.getMaxRows(), rows - sh.getMaxRows());
  if (sh.getMaxColumns() < last) sh.insertColumnsAfter(sh.getMaxColumns(), last - sh.getMaxColumns());
  if (sh.getRange(1, n + 2).getValue() === "Status") sh.insertColumnAfter(n + 1);   // first CRM version: make room for Country, data moves along
  if (sh.getMaxColumns() < last) sh.insertColumnsAfter(sh.getMaxColumns(), last - sh.getMaxColumns());
  sh.getRange(1, 1, 1, n).setValues([HEADERS]);
  sh.getRange(1, n + 3, 1, CRM.length - 2).setValues([CRM.slice(2)]);

  // Country from the phone number, via a hidden lookup tab
  var codes = ss.getSheetByName("Codes") || ss.insertSheet("Codes");
  codes.clear();
  var list = Object.keys(CODES).map(function (k) { return [k, CODES[k]]; });
  codes.getRange(1, 1, list.length, 1).setNumberFormat("@");
  codes.getRange(1, 1, list.length, 2).setValues(list);
  codes.hideSheet();
  var d = 'REGEXREPLACE(C2:C&"","[^0-9]","")';
  var look = function (k) { return 'VLOOKUP(LEFT(' + d + ',' + k + '),Codes!A:B,2,FALSE)'; };
  sh.getRange(1, n + 2).setFormula('={"Country";ARRAYFORMULA(IF(A2:A="",,IFERROR(' + look(3) + ',IFERROR(' + look(2) + ',IFERROR(' + look(1) + ',"🌐 ?")))))}');

  // Grade (same rule as the Studio): Hot = $250k+ and buying within 3 months
  var big = '((D2:D="$250k to $500k")+(D2:D="$500k and above"))';
  var fast = '((LOWER(E2:E)="ready now")+(LOWER(E2:E)="within 3 months"))';
  var mid = '(LOWER(E2:E)="3 to 6 months")';
  sh.getRange(1, n + 1).setFormula('={"Grade";ARRAYFORMULA(IF(A2:A="",,IF(' + big + '*' + fast + ',"🔥 Hot",IF(' + big +
    '+(D2:D="$100k to $250k")*(' + fast + '+' + mid + '),"Warm","Nurture"))))}');

  // Status dropdown, dates, phone as text
  sh.getRange(2, n + 2, rows - 1, 1).clearDataValidations();
  sh.getRange(2, n + 3, rows - 1, 1).setDataValidation(SpreadsheetApp.newDataValidation()
    .requireValueInList(STATUSES, true).setAllowInvalid(false).build());
  [n + 5, n + 6].forEach(function (c) {
    sh.getRange(2, c, rows - 1, 1).setNumberFormat("d mmm yyyy")
      .setDataValidation(SpreadsheetApp.newDataValidation().requireDate().setAllowInvalid(false).build());
  });
  sh.getRange(2, 1, rows - 1, 1).setNumberFormat("d mmm, HH:mm");
  sh.getRange(2, 3, rows - 1, 1).setNumberFormat("@");

  styleLeads(sh, n, last, rows);
  stylePipeline(ss, n);
  ss.setActiveSheet(sh);
  try {                                   // works from the sheet's menu and from the editor's Run button
    SpreadsheetApp.getUi().alert("CRM ready.");
  } catch (err) {
    console.log("CRM ready");
  }
}

// Brand colours from balioffscript.com
var C = { ink: "#16191d", paper: "#fdfdfc", paper2: "#f4f3f0", slate: "#4c545e", accent: "#2f4858",
          seal: "#8a2c26", verify: "#1d5240", rule: "#e8e6e1", gold: "#b07a12" };

function styleLeads(sh, n, last, rows) {
  var CLIP = SpreadsheetApp.WrapStrategy.CLIP, WRAP = SpreadsheetApp.WrapStrategy.WRAP;
  var all = sh.getRange(1, 1, rows, last);
  sh.setHiddenGridlines(true);
  sh.getBandings().forEach(function (b) { b.remove(); });
  all.setFontFamily("Public Sans").setFontSize(10).setFontColor(C.ink).setVerticalAlignment("middle")
     .setWrapStrategy(CLIP).setBorder(false, false, false, false, false, false);
  all.applyRowBanding(SpreadsheetApp.BandingTheme.LIGHT_GREY, true, false)
     .setHeaderRowColor(C.accent).setFirstRowColor("#ffffff").setSecondRowColor(C.paper2);
  all.setBorder(null, null, null, null, null, true, C.rule, SpreadsheetApp.BorderStyle.SOLID);

  // Header: website fields in slate blue, your CRM fields in green
  var head = sh.getRange(1, 1, 1, last);
  head.setFontColor("#ffffff").setFontWeight("bold").setFontSize(10).setWrapStrategy(WRAP)
      .setVerticalAlignment("middle").setHorizontalAlignment("left");
  sh.getRange(1, 1, 1, n + 2).setBackground(C.accent);
  sh.getRange(1, n + 3, 1, CRM.length - 2).setBackground(C.verify);
  sh.setRowHeight(1, 44);
  sh.setRowHeightsForced(2, rows - 1, 30);

  // Readable at a glance
  sh.getRange(2, 2, rows - 1, 1).setFontWeight("bold");                                   // Name
  sh.getRange(2, 1, rows - 1, 1).setFontColor(C.slate);                                   // Received
  [6, 7].forEach(function (c) { sh.getRange(2, c, rows - 1, 1).setFontColor("#9aa0a6").setFontSize(9); });  // Source, Page
  sh.getRange(1, n + 1, rows, 1).setHorizontalAlignment("center");                        // Grade
  sh.getRange(1, n + 3, rows, 1).setHorizontalAlignment("center");                        // Status
  sh.getRange(1, n + 5, rows, 2).setHorizontalAlignment("center");                        // dates
  sh.getRange(2, 10, rows - 1, 1).setHorizontalAlignment("center");                       // Language

  sh.setFrozenRows(1);
  sh.setFrozenColumns(2);
  var widths = [118, 170, 140, 135, 130, 110, 110, 220, 165, 80, 220, 92, 150, 125, 240, 105, 105, 320];
  widths.forEach(function (w, i) { sh.setColumnWidth(i + 1, w); });
  if (sh.getFilter()) sh.getFilter().remove();
  sh.getRange(1, 1, rows, last).createFilter();

  var L = function (c) { return String.fromCharCode(64 + c); };
  var S = L(n + 3), F = L(n + 5), G = L(n + 1);
  var col = function (c) { return sh.getRange(2, c, rows - 1, 1); };
  var rowAll = sh.getRange(2, 1, rows - 1, last);
  var rule = function (formula, range, bg, fg, bold) {
    var b = SpreadsheetApp.newConditionalFormatRule().whenFormulaSatisfied(formula).setRanges([range]);
    if (bg) b.setBackground(bg);
    if (fg) b.setFontColor(fg);
    if (bold) b.setBold(true);
    return b.build();
  };
  var closed = 'REGEXMATCH($' + S + '2&"","Won|Lost|Not a fit")';
  sh.setConditionalFormatRules([
    // follow-up today or late
    rule('=AND($' + F + '2<>"",$' + F + '2<=TODAY(),NOT(' + closed + '))', col(n + 5), "#fbe3e1", C.seal, true),
    // nobody has contacted them for 24 hours
    rule('=AND($A2<>"",OR($' + S + '2="",$' + S + '2="New"),NOW()-$A2>1)', col(2), "#fff1cc", "#7a5200", true),
    // grade pills
    rule('=$' + G + '2="🔥 Hot"', col(n + 1), C.seal, "#ffffff", true),
    rule('=$' + G + '2="Warm"', col(n + 1), "#f6e7c8", "#7a5200", true),
    rule('=$' + G + '2="Nurture"', col(n + 1), null, "#8a8f96", false),
    // status pills
    rule('=$' + S + '2="Won"', col(n + 3), C.verify, "#ffffff", true),
    rule('=REGEXMATCH($' + S + '2&"","Call booked|Viewing|Offer")', col(n + 3), "#dbe7ee", C.accent, true),
    rule('=REGEXMATCH($' + S + '2&"","Contacted|Qualified")', col(n + 3), "#e8f1ec", C.verify, true),
    rule('=OR($' + S + '2="",$' + S + '2="New")', col(n + 3), null, "#b07a12", true),
    // closed leads fade out
    rule('=REGEXMATCH($' + S + '2&"","Lost|Not a fit")', rowAll, "#f7f7f7", "#a8a8a8", false)
  ]);
}

function stylePipeline(ss, n) {
  var p = ss.getSheetByName("Pipeline") || ss.insertSheet("Pipeline");
  p.clear();
  p.clearConditionalFormatRules();
  p.setHiddenGridlines(true);
  if (p.getMaxColumns() < 8) p.insertColumnsAfter(p.getMaxColumns(), 8 - p.getMaxColumns());
  var L = function (c) { return String.fromCharCode(64 + c); };
  var S = L(n + 3), F = L(n + 5), G = L(n + 1);
  var st = "Leads!" + S + "2:" + S, fu = "Leads!" + F + "2:" + F, gr = "Leads!" + G + "2:" + G;
  var open = 'NOT(REGEXMATCH(' + st + '&"","Won|Lost|Not a fit"))';
  var newCount = 'COUNTIFS(Leads!A2:A,"<>",' + st + ',"")+COUNTIF(' + st + ',"New")';

  p.getRange("A1:H60").setFontFamily("Public Sans").setFontColor(C.ink).setVerticalAlignment("middle");
  p.setColumnWidth(1, 28);
  [2, 3, 4, 5, 6].forEach(function (c) { p.setColumnWidth(c, 170); });
  p.setColumnWidth(7, 28);

  p.getRange("B2").setValue("Bali Off Script · Leads").setFontFamily("Fraunces").setFontSize(22).setFontWeight("bold");
  p.getRange("B3").setValue("Live from the Leads tab. Work the red and yellow first.").setFontColor(C.slate).setFontSize(10);
  p.setRowHeight(2, 44);

  // KPI cards
  var kpis = [["New, last 7 days", '=COUNTIFS(Leads!A2:A,">="&(TODAY()-7))', C.accent],
              ["New, last 30 days", '=COUNTIFS(Leads!A2:A,">="&(TODAY()-30))', C.accent],
              ["🔥 Hot leads", '=COUNTIF(' + gr + ',"🔥 Hot")', C.seal],
              ["Not contacted yet", "=" + newCount, C.gold],
              ["Follow-ups due", '=COUNTIFS(' + fu + ',"<="&TODAY(),' + st + ',"<>Won",' + st + ',"<>Lost",' + st + ',"<>Not a fit")', C.seal]];
  kpis.forEach(function (k, i) {
    var c = 2 + i;
    p.getRange(5, c).setValue(k[0]).setFontSize(9).setFontColor(C.slate).setFontWeight("bold");
    p.getRange(6, c).setFormula(k[1]).setFontSize(28).setFontWeight("bold").setFontColor(k[2]).setHorizontalAlignment("left");
    p.getRange(5, c, 2, 1).setBackground(C.paper2)
      .setBorder(true, true, true, true, false, false, "#ffffff", SpreadsheetApp.BorderStyle.SOLID_THICK);
  });
  p.setRowHeight(5, 30); p.setRowHeight(6, 54);

  // Pipeline by status with bars
  p.getRange("B9").setValue("Pipeline").setFontFamily("Fraunces").setFontSize(15).setFontWeight("bold");
  p.getRange("B10:D10").setValues([["Status", "Leads", ""]]).setFontSize(9).setFontColor(C.slate).setFontWeight("bold");
  STATUSES.forEach(function (s, i) {
    var r = 11 + i;
    p.getRange(r, 2).setValue(s).setFontWeight("bold");
    p.getRange(r, 3).setFormula(s === "New" ? "=" + newCount : '=COUNTIF(' + st + ',"' + s + '")').setHorizontalAlignment("left");
    var color = s === "Won" ? C.verify : (s === "Lost" || s === "Not a fit") ? "#c4c4c4" : s === "New" ? C.gold : C.accent;
    p.getRange(r, 4, 1, 3).merge().setFormula('=SPARKLINE(C' + r + ',{"charttype","bar";"max",MAX($C$11:$C$19)+0.0001;"color1","' + color + '"})');
    p.getRange(r, 2, 1, 5).setBorder(null, null, true, null, null, null, C.rule, SpreadsheetApp.BorderStyle.SOLID);
    p.setRowHeight(r, 28);
  });

  // Today's work
  p.getRange("B22").setValue("Today").setFontFamily("Fraunces").setFontSize(15).setFontWeight("bold");
  p.getRange("B23").setValue("Follow up today").setFontWeight("bold").setFontColor(C.seal);
  p.getRange("C23:F23").merge().setFormula('=IFERROR(TEXTJOIN(", ",TRUE,FILTER(Leads!B2:B,' + fu + '<>"",' + fu + '<=TODAY(),' + open + ')),"Nothing due")').setWrap(true);
  p.getRange("B24").setValue("🔥 Hot, not contacted").setFontWeight("bold").setFontColor(C.seal);
  p.getRange("C24:F24").merge().setFormula('=IFERROR(TEXTJOIN(", ",TRUE,FILTER(Leads!B2:B,' + gr + '="🔥 Hot",(' + st + '="")+(' + st + '="New"))),"None, well done")').setWrap(true);
  p.getRange("B25").setValue("Newest 5").setFontWeight("bold").setFontColor(C.accent);
  p.getRange("C25:F25").merge().setFormula('=IFERROR(TEXTJOIN(", ",TRUE,ARRAY_CONSTRAIN(SORT(FILTER(Leads!B2:B,Leads!A2:A<>""),FILTER(Leads!A2:A,Leads!A2:A<>""),FALSE),5,1)),"")').setWrap(true);
  [23, 24, 25].forEach(function (r) { p.setRowHeight(r, 34); p.getRange(r, 2, 1, 5).setBorder(null, null, true, null, null, null, C.rule, SpreadsheetApp.BorderStyle.SOLID); });

  // Where they're from
  var K = L(n + 2);
  p.getRange("B28").setValue("Where they're from").setFontFamily("Fraunces").setFontSize(15).setFontWeight("bold");
  p.getRange("B29").setFormula('=IFERROR(QUERY(Leads!' + K + '2:' + K + ',"select ' + K + ', count(' + K + ') where ' + K +
    ' is not null group by ' + K + ' order by count(' + K + ') desc limit 10 label count(' + K + ') \'\'",0),"")');
  p.getRange("B29:C38").setFontSize(11);
  p.getRange("C29:C38").setHorizontalAlignment("left").setFontWeight("bold");

  p.setTabColor(C.accent);
  var leads = ss.getSheetByName("Leads");
  if (leads) leads.setTabColor(C.verify);
  ss.setActiveSheet(p);
  ss.moveActiveSheet(1);
}



/* ------------------------------------------------------------------------
 * The free guide by email, automatically, the moment a lead comes in.
 * Only when the person gave an email, and never to an Indonesian number
 * (+62, 0062, or a local 08 number): Kai's rule. Protected against abuse:
 * one guide per address per 7 days, at most 40 a day.
 * ---------------------------------------------------------------------- */
var SITE = "https://balioffscript.com";
var KIT_PDF = SITE + "/kit/k7q4m2/";
var TOPIC_PDF = {
  "The Bali Villa Build Guide": "bali-build-guide.pdf",
  "Owning Property in Bali as a Foreigner": "bali-own-guide.pdf",
  "The Bali Rental Income Guide": "bali-rent-guide.pdf",
  "Where to Buy in Bali: Area by Area": "bali-areas-guide.pdf",
  "Moving to Bali: Visas, Living and Buying": "bali-move-guide.pdf"
};
var MAIL = {
  en: { s: "Your {g}", h: "Hi {n},", a: "Here is your {g}:", b: "Download it here", c: "Are you looking at something specific in Bali, or still exploring? Reply with the area and your budget and I'll tell you what I would check first.", k: "The Bali Buyer's Kit" },
  fr: { s: "Ton guide : {g}", h: "Bonjour {n},", a: "Voici ton guide, {g} :", b: "Le télécharger ici", c: "Tu regardes déjà quelque chose de précis à Bali, ou tu te renseignes encore ? Réponds-moi avec la zone et ton budget, et je te dis ce que je vérifierais en premier.", k: "Le guide de l'acheteur à Bali" },
  de: { s: "Dein Leitfaden: {g}", h: "Hallo {n},", a: "Hier ist dein Leitfaden, {g}:", b: "Hier herunterladen", c: "Schaust du dir schon etwas Bestimmtes auf Bali an, oder informierst du dich noch? Schreib mir die Gegend und dein Budget, dann sage ich dir, was ich zuerst prüfen würde.", k: "Der Bali-Käuferleitfaden" },
  nl: { s: "Je gids: {g}", h: "Hoi {n},", a: "Hier is je gids, {g}:", b: "Hier downloaden", c: "Kijk je al naar iets specifieks op Bali, of oriënteer je je nog? Stuur me het gebied en je budget, dan vertel ik wat ik als eerste zou controleren.", k: "De Bali-kopersgids" },
  sv: { s: "Din guide: {g}", h: "Hej {n},", a: "Här är din guide, {g}:", b: "Ladda ner den här", c: "Tittar du redan på något särskilt på Bali, eller undersöker du fortfarande? Svara med område och budget så säger jag vad jag skulle kontrollera först.", k: "Köparguiden för Bali" },
  no: { s: "Guiden din: {g}", h: "Hei {n},", a: "Her er guiden din, {g}:", b: "Last den ned her", c: "Ser du allerede på noe bestemt på Bali, eller undersøker du fortsatt? Svar med område og budsjett, så sier jeg hva jeg ville sjekket først.", k: "Kjøperguiden for Bali" }
};

function isIndonesian(phone) {
  var raw = String(phone || "").replace(/^'/, "").trim();
  var d = raw.replace(/[^0-9]/g, "");
  if (/^\+?\s*62/.test(raw) || /^0062/.test(d) || (raw.charAt(0) !== "+" && /^08/.test(d))) return true;
  // an Indonesian mobile typed under the form's default code, e.g. "+61 0812 3456 7890"
  var nat = raw.replace(/^\+\d{1,3}\s*/, "").replace(/[^0-9]/g, "");
  return /^08[1-9]/.test(nat) && nat.length >= 11;
}

function sendGuide(d, row) {
  try {
    var email = String(row[7] || "").replace(/^'/, "").trim().toLowerCase();
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) return;
    if (isIndonesian(row[2])) return;

    var props = PropertiesService.getScriptProperties();
    var key = "g:" + email, now = Date.now();
    var last = Number(props.getProperty(key) || 0);
    if (now - last < 7 * 864e5) return;                              // one per address per week
    var day = "n:" + Utilities.formatDate(new Date(), "Asia/Makassar", "yyyy-MM-dd");
    var count = Number(props.getProperty(day) || 0);
    if (count >= 40) return;                                         // daily cap

    var lang = MAIL[String(row[9] || "en").toLowerCase()] ? String(row[9]).toLowerCase() : "en";
    var m = MAIL[lang];
    var topic = TOPIC_PDF[String(row[10] || "")];
    var guide = topic ? String(row[10]) : m.k;
    var pdf = topic ? KIT_PDF + topic : KIT_PDF + "bali-buyers-kit-" + lang + ".pdf";
    var name = String(row[1] || "").replace(/^'/, "").split(" ")[0] || "";
    var f = function (t) { return t.replace("{g}", guide).replace("{n}", name); };

    var text = [f(m.h), "", f(m.a), pdf, "", m.c, "", "Kai", "Bali Off Script · balioffscript.com"].join("\n");
    var html = '<div style="font-family:Arial,sans-serif;font-size:15px;line-height:1.55;color:#16191d">' +
      "<p>" + f(m.h) + "</p><p>" + f(m.a) + '</p><p><a href="' + pdf + '" style="display:inline-block;background:#8a2c26;color:#fff;' +
      'padding:12px 18px;border-radius:6px;text-decoration:none;font-weight:bold">' + m.b + "</a></p><p>" + m.c + "</p>" +
      '<p>Kai<br><span style="color:#4c545e">Bali Off Script · <a href="' + SITE + '" style="color:#4c545e">balioffscript.com</a></span></p></div>';

    MailApp.sendEmail({ to: email, subject: f(m.s), body: text, htmlBody: html, name: "Kai | Bali Off Script", replyTo: NOTIFY });
    props.setProperty(key, String(now));
    props.setProperty(day, String(count + 1));
  } catch (err) {
    console.error("guide email failed", err);                       // never let this lose the lead
  }
}
