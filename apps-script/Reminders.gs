/**
 * Bali meeting reminders (Kai, 18 Oct 2026). Its own Apps Script project in hello@qaisstanikzai.com.
 *
 * Every 10 minutes it looks at the calendar and emails the people booked on a Bali call:
 *   - about 24 hours before: "Tomorrow: your Bali property call"
 *   - about 1 hour before:   "See you in an hour"
 * Only Bali meetings (Calendly bookings, Coco's Calendly, or "Bali" in the title or description).
 * Nothing after the call (Kai, 18 Oct: skip that part).
 *
 * Email safety (Kai's rules): at most 15 a day, at least 60 seconds apart, the address's domain must accept
 * email (MX check), every send logged, never the same reminder twice.
 *
 * Setup, once: paste this file, choose setupReminders in the menu, press Run, Allow.
 * Test: run sendTestToMe, it sends both reminders to hello@qaisstanikzai.com only.
 */
var REM = {
  CAL: 'hello@qaisstanikzai.com',
  FROM_NAME: 'Kai',
  MAX_DAY: 15,
  PER_RUN: 4,                      // 4 sends x 61 s stays inside Apps Script's 6-minute run limit
  OWN: /(@qaisstanikzai\.com|kai\.stan\.coco@gmail\.com|@group\.calendar\.google\.com|@resource\.calendar\.google\.com)$/i,
  WINDOWS: { '24h': [22 * 60, 24 * 60 + 5], '1h': [40, 65] }   // minutes before the start
};

function setupReminders() {
  ScriptApp.getProjectTriggers().forEach(function (t) {
    if (t.getHandlerFunction() === 'sendReminders') ScriptApp.deleteTrigger(t);
  });
  ScriptApp.newTrigger('sendReminders').timeBased().everyMinutes(10).create();
  sendReminders();
  Logger.log('Reminders are on: every 10 minutes.');
}

function stopReminders() {
  ScriptApp.getProjectTriggers().forEach(function (t) {
    if (t.getHandlerFunction() === 'sendReminders') ScriptApp.deleteTrigger(t);
  });
  Logger.log('Reminders are off.');
}

function sendReminders() {
  var lock = LockService.getScriptLock();
  if (!lock.tryLock(5000)) return;
  try {
    var props = PropertiesService.getScriptProperties();
    cleanOld_(props);
    var cal = CalendarApp.getCalendarById(REM.CAL) || CalendarApp.getDefaultCalendar();
    var now = new Date();
    var events = cal.getEvents(now, new Date(now.getTime() + 25 * 3600 * 1000));
    var sent = 0;
    for (var i = 0; i < events.length && sent < REM.PER_RUN; i++) {
      var ev = events[i];
      if (!isBali_(ev) || ev.isAllDayEvent()) continue;
      var mins = (ev.getStartTime().getTime() - now.getTime()) / 60000;
      var kind = null;
      for (var k in REM.WINDOWS) {
        if (mins >= REM.WINDOWS[k][0] && mins <= REM.WINDOWS[k][1]) kind = k;
      }
      if (!kind) continue;
      var guests = ev.getGuestList().filter(function (g) {
        return !REM.OWN.test(g.getEmail()) && g.getGuestStatus() !== CalendarApp.GuestStatus.NO;
      });
      for (var j = 0; j < guests.length && sent < REM.PER_RUN; j++) {
        var to = guests[j].getEmail().toLowerCase();
        var key = 'rem|' + ev.getId() + '|' + ev.getStartTime().getTime() + '|' + kind + '|' + to;
        if (props.getProperty(key)) continue;
        if (dayCount_(props) >= REM.MAX_DAY) { log_(props, 'daily limit reached, not sent: ' + kind + ' ' + to); return; }
        var mx = mxOk_(to);
        if (mx === null) continue;                       // DNS didn't answer: try again next run
        if (!mx) { props.setProperty(key, 'bad-mx ' + now.toISOString()); log_(props, 'no mail server, skipped: ' + to); continue; }
        if (sent > 0) Utilities.sleep(61000);            // at least 60 seconds between emails
        var mail = build_(kind, ev, guests[j]);
        MailApp.sendEmail({ to: to, subject: mail.subject, body: mail.body, name: REM.FROM_NAME });
        props.setProperty(key, now.toISOString());
        bumpDay_(props);
        log_(props, 'sent ' + kind + ' to ' + to + ' for ' + ev.getTitle());
        sent++;
      }
    }
  } finally {
    lock.releaseLock();
  }
}

function isBali_(ev) {
  var text = (ev.getTitle() + ' ' + (ev.getDescription() || '')).toLowerCase();
  return text.indexOf('bali') >= 0;
}

function firstName_(ev, guest) {
  var t = ev.getTitle() || '';
  var n = t.indexOf(' and ') > 0 ? t.split(' and ')[0] : (guest.getName() || t);
  n = n.replace(/\b(bali|property|call|meeting|with)\b/gi, ' ').replace(/[^a-zA-ZÀ-ɏ' -]/g, ' ').trim().split(/\s+/)[0] || '';
  if (!n || n.toLowerCase() === 'kai' || n.toLowerCase() === 'qais') return 'there';
  return n.charAt(0).toUpperCase() + n.slice(1).toLowerCase();
}

function links_(ev) {
  var d = ev.getDescription() || '';
  var meet = (d.match(/https:\/\/calendly\.com\/events\/[^\s"<]+\/google_meet/) ||
              d.match(/https:\/\/meet\.google\.com\/[a-z0-9-]+/i) ||
              (ev.getLocation() || '').match(/https:\/\/meet\.google\.com\/[a-z0-9-]+/i) || [null])[0];
  var resched = (d.match(/https:\/\/calendly\.com\/reschedulings\/[^\s"<]+/) || [null])[0];
  return { meet: meet, resched: resched };
}

function build_(kind, ev, guest) {
  var name = firstName_(ev, guest), l = links_(ev);
  var join = l.meet ? 'Join here: ' + l.meet : 'Join with the Google Meet link in your calendar invite.';
  if (kind === '24h') {
    return {
      subject: 'Tomorrow: your Bali property call',
      body: 'Hi ' + name + ',\n\n' +
        'Just a reminder that we\'re speaking tomorrow, at the time you booked.\n\n' +
        join + '\n\n' +
        'If you have a listing or an area in mind, send it over before the call and I\'ll look at it first, so we use the hour well.\n\n' +
        (l.resched ? 'Need another time? ' + l.resched : 'Need another time? Just reply to this email.') + '\n\n' +
        'Talk tomorrow,\n' +
        'Kai | Property Advisor\n' +
        'WhatsApp +44 7441 340188\n' +
        'balioffscript.com'
    };
  }
  return {
    subject: 'See you in an hour',
    body: 'Hi ' + name + ',\n\n' +
      'We\'re on in an hour. ' + join + '\n\n' +
      'See you soon,\n' +
      'Kai'
  };
}

function mxOk_(to) {
  var domain = to.split('@')[1];
  var cache = CacheService.getScriptCache(), hit = cache.get('mx|' + domain);
  if (hit) return hit === '1';
  try {
    var r = UrlFetchApp.fetch('https://dns.google/resolve?name=' + encodeURIComponent(domain) + '&type=MX', { muteHttpExceptions: true });
    if (r.getResponseCode() !== 200) return null;
    var ok = (JSON.parse(r.getContentText()).Answer || []).some(function (a) { return a.type === 15; });
    cache.put('mx|' + domain, ok ? '1' : '0', 21600);
    return ok;
  } catch (e) {
    return null;
  }
}

function today_() {
  return Utilities.formatDate(new Date(), 'Asia/Makassar', 'yyyy-MM-dd');
}

function dayCount_(props) {
  return Number(props.getProperty('day|' + today_()) || 0);
}

function bumpDay_(props) {
  props.setProperty('day|' + today_(), String(dayCount_(props) + 1));
}

function log_(props, line) {
  var log = JSON.parse(props.getProperty('log') || '[]');
  log.unshift(Utilities.formatDate(new Date(), 'Asia/Makassar', 'dd MMM HH:mm') + '  ' + line);
  props.setProperty('log', JSON.stringify(log.slice(0, 60)));
  Logger.log(line);
}

function showLog() {
  Logger.log((JSON.parse(PropertiesService.getScriptProperties().getProperty('log') || '[]')).join('\n') || 'Nothing sent yet.');
}

function cleanOld_(props) {
  var all = props.getProperties(), cutoff = Date.now() - 3 * 24 * 3600 * 1000;
  Object.keys(all).forEach(function (k) {
    if (k.indexOf('rem|') === 0 && Number(k.split('|')[2]) < cutoff) props.deleteProperty(k);
    if (k.indexOf('day|') === 0 && k !== 'day|' + today_()) props.deleteProperty(k);
  });
}

/** Sends both reminders to hello@qaisstanikzai.com only, using the next Bali meeting in the calendar. */
function sendTestToMe() {
  var cal = CalendarApp.getCalendarById(REM.CAL) || CalendarApp.getDefaultCalendar();
  var now = new Date();
  var ev = cal.getEvents(now, new Date(now.getTime() + 30 * 24 * 3600 * 1000)).filter(isBali_)[0];
  if (!ev) { Logger.log('No Bali meeting in the next 30 days to test with.'); return; }
  var g = ev.getGuestList().filter(function (x) { return !REM.OWN.test(x.getEmail()); })[0] || ev.getGuestList()[0];
  ['24h', '1h'].forEach(function (kind, i) {
    if (i) Utilities.sleep(61000);
    var m = build_(kind, ev, g);
    MailApp.sendEmail({ to: REM.CAL, subject: '[TEST] ' + m.subject, body: m.body, name: REM.FROM_NAME });
  });
  Logger.log('Two test emails sent to ' + REM.CAL + ' (based on: ' + ev.getTitle() + ')');
}
