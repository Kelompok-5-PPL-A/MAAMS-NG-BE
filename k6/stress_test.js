import http from 'k6/http';
import { sleep, check } from 'k6';

export let options = {
  stages: [
    { duration: '1m', target: 10 },
    { duration: '1m', target: 50 },
    { duration: '1m', target: 100 },
    { duration: '1m', target: 200 },
    { duration: '1m', target: 300 },
    { duration: '1m', target: 500 },
    { duration: '1m', target: 1000 },
    { duration: '30s', target: 0 },
  ],
};

const BASE_URL = 'http://127.0.0.1:8000';

let counter = 1;

// Statistik manual
let successSubmit = 0;
let totalSubmit = 0;

let successGet = 0;
let totalGet = 0;

let successCause = 0;
let totalCause = 0;

export default function () {
  const randomTitle = `Test ${counter++}`;

  // Submit Question
  totalSubmit++;
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

  const isSubmitOK = check(submitRes, {
    "Submit Analysis - Status is 201": (r) => r.status === 201,
  });

  if (isSubmitOK) successSubmit++;

  if (submitRes.status === 201) {
    try {
      const questionId = submitRes.json('id');
      sleep(1);

      // Get Question
      totalGet++;
      const getRes = http.get(`${BASE_URL}/question/${questionId}/`);
      const isGetOK = check(getRes, {
        "Get Analysis - Status is 200": (r) => r.status === 200,
      });
      if (isGetOK) successGet++;

      sleep(1);

      // Submit Cause
      totalCause++;
      const causeRes = http.post(`${BASE_URL}/cause/`, JSON.stringify({
        question_id: questionId,
        cause: "Sample cause for testing",
        row: 1,
        column: 1,
        mode: "PRIBADI"
      }), {
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });

      const isCauseOK = check(causeRes, {
        "Submit Cause - Status is 201": (r) => r.status === 201,
      });
      if (isCauseOK) successCause++;
    } catch (e) {
      console.log(`Error processing question: ${e.message}`);
    }
  }

  // Print summary every 100 iterations per VU
  if (__ITER % 100 === 0 && __ITER !== 0) {
    console.log(`[VU ${__VU} | Iter ${__ITER}] Success Rates:`);
    console.log(`  Submit: ${successSubmit}/${totalSubmit} (${((successSubmit / totalSubmit) * 100).toFixed(2)}%)`);
    console.log(`  Get   : ${successGet}/${totalGet} (${((successGet / totalGet) * 100).toFixed(2)}%)`);
    console.log(`  Cause : ${successCause}/${totalCause} (${((successCause / totalCause) * 100).toFixed(2)}%)`);
  }

  sleep(1);
}
