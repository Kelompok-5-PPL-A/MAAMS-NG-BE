import http from 'k6/http';
import { sleep, check } from 'k6';

export let options = {
  stages: [
    { duration: '5m', target: 5 },    // warming up
    { duration: '10m', target: 10 },  // start stable load
    { duration: '20m', target: 15 },  // endurance peak
    { duration: '5m', target: 5 },    // cooldown
    { duration: '2m', target: 0 },    // ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<1000'], // 95% response time harus < 1 detik
    http_req_failed: ['rate<0.01'],    // error rate < 1%
  },
};

const BASE_URL = 'http://127.0.0.1:8000';

function randomString(length) {
  const chars = 'abcdefghijklmnopqrstuvwxyz0123456789';
  let result = '';
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
}

export default function () {
  const randomTitle = `Test ${randomString(5)}`;
  
  // Step 1: Submit pertanyaan
  let submitRes = http.post(`${BASE_URL}/question/submit/`, JSON.stringify({
    mode: "PRIBADI",
    question: "Load testing simulation question",
    tags: ["tag1", "tag2"],
    title: randomTitle
  }), { 
    headers: { 
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    } 
  });

  check(submitRes, {
    "Submit Question - status 201": (r) => r.status === 201,
  });

  sleep(1); // jeda seolah user berpikir

  if (submitRes.status === 201) {
    try {
      let questionId = submitRes.json('id');

      // Step 2: GET pertanyaan detail
      let getRes = http.get(`${BASE_URL}/question/${questionId}/`);

      check(getRes, {
        "Get Question - status 200": (r) => r.status === 200,
      });

      sleep(1);

      // Step 3: Submit cause
      const causePayload = {
        question_id: questionId,
        cause: "Sample cause for testing",
        row: 1,
        column: 1,
        mode: "PRIBADI"
      };

      let causeRes = http.post(`${BASE_URL}/cause/`, JSON.stringify(causePayload), { 
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        } 
      });

      check(causeRes, {
        "Submit Cause - status 201": (r) => r.status === 201,
      });

    } catch (e) {
      // tangani jika parsing JSON gagal
      console.log(`Error: ${e.message}`);
    }
  }

  sleep(1); // delay sebelum VU ulangi siklusnya
}
