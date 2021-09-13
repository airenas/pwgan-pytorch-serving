// test acoustic model with several voice parameters
import http from "k6/http";
import { check, sleep } from "k6";
import { SharedArray } from "k6/data";
import { Counter } from 'k6/metrics';

var counter500 = new Counter('status 5xx');
var counter400 = new Counter('status 4xx');

const testURL = __ENV.URL;

const VOICES = new SharedArray("voc voices", function() { return JSON.parse(open(__ENV.DATA_DIR + '/data.json')).data.voices; });
const DATA = new SharedArray("voc data", function() { return JSON.parse(open(__ENV.DATA_DIR + '/data.json')).data.data; });
const t_len = DATA.length;
const v_len = Math.min(VOICES.length, __ENV.VOICES_NUM);

function getRandomInt(max) {
  return Math.floor(Math.random() * max);
}

export default function (data) {
    var ti = getRandomInt(t_len);
    var vi = getRandomInt(v_len);
    var url = testURL;
    var payload = JSON.stringify({
        data: DATA[ti],
        voice: VOICES[vi],
    });
    var params = {
        headers: {
            'Content-Type': 'application/json',
        },
    };
    let res = http.post(url, payload, params);
    counter500.add(res.status >= 500);
    counter400.add(res.status >= 400 && res.status < 500);
    check(res, {
        "status was 200": (r) => r.status === 200,
        "json ok": (r) => r.json("data") && r.json("data").length > 10000,
        "transaction time OK": (r) => r.timings.duration < 25000
    });
    sleep(0.1);
}
