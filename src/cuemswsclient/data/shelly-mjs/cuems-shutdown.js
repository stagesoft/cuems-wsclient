// cuems-shutdown.js -- Shelly Pro 1 (Gen 2) mJS script.
//
// Installs into the Shelly's Scripts tab via the device web UI. Edit
// BRIDGE and TOKEN below for your deployment, then click "Save" and
// "Start". The script then sleeps until the wired flip-switch on SW
// input 0 transitions to OFF, at which point it asks the controller's
// power bridge to do an orderly cluster shutdown. The bridge arms a
// hardware safety timer on this Shelly which opens the relay (cuts
// mains) after the configured number of seconds -- even if the bridge
// itself disappears mid-shutdown, the Shelly will still cut power.
//
// SPDX-FileCopyrightText: 2026 Stagelab Coop SCCL
// SPDX-License-Identifier: GPL-3.0-or-later

let BRIDGE = "http://192.168.6.1:8478";   // controller bond0 IP (NOT .local)
let TOKEN  = "REPLACE-ME";                 // matches power-bridge.conf shared_token
let inflight = false;                      // simple debounce guard

Shelly.addStatusHandler(function (ev) {
  if (ev.component !== "input:0") return;
  if (ev.delta.state === undefined) return;
  if (ev.delta.state !== false) return;    // only react on flip -> OFF
  if (inflight) return;
  inflight = true;
  // Fail-safe: if the HTTP callback never fires (Shelly internal hang),
  // clear the lock after 10 s so future flips aren't permanently blocked.
  Timer.set(10000, false, function () { inflight = false; });

  Shelly.call("HTTP.POST", {
    url: BRIDGE + "/shutdown",
    body: "{}",
    headers: {"X-Auth-Token": TOKEN, "Content-Type": "application/json"}
  }, function (r, err_code, err_msg) {
    inflight = false;
    if (err_code !== 0) {
      print("[cuems] bridge unreachable: " + err_msg);
      return;
    }
    if (r.code === 200) {
      // Bridge accepted. It will arm Switch.Set toggle_after, which
      // opens our relay when ready. We do nothing more here.
      print("[cuems] shutdown accepted");
      return;
    }
    if (r.code === 409) { print("[cuems] shutdown refused (project running or in progress): " + r.body); return; }
    if (r.code === 401) { print("[cuems] bad token"); return; }
    if (r.code === 503) { print("[cuems] engine state unknown -- try again later"); return; }
    if (r.code === 502) { print("[cuems] bridge could not reach engine/Shelly: " + r.body); return; }
    print("[cuems] unexpected response " + r.code + ": " + r.body);
  });
});

print("[cuems] cuems-shutdown.js armed -- flip SW0 OFF to initiate orderly shutdown");
