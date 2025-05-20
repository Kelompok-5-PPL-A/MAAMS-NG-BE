import http from 'k6/http';
import { sleep, check } from 'k6';

export let options = {
  stages: [
    { duration: '30s', target: 50 },
    { duration: '1m', target: 200 },
    { duration: '1m', target: 300 },
    { duration: '1m', target: 400 },
    { duration: '1m', target: 500 },
    { duration: '1m', target: 100 },
    { duration: '30s', target: 0 },
  ],
};

const BASE_URL = 'http://127.0.0.1:8000';
const HEADERS = {
  'Content-Type': 'application/json',
  Accept: 'application/json',
};

let counter = 1;

export default function () {
  const title = `StressTest-${counter++}`;

  // 1. Submit question
  const submitPayload = JSON.stringify({
    mode: "PRIBADI",
    question: "Load testing simulation question",
    tags: ["tag1", "tag2"],
    title: title,
  });

  const submitRes = http.post(`${BASE_URL}/question/submit/`, submitPayload, { headers: HEADERS });
  const isSubmitSuccess = check(submitRes, {
    "Success: Submit Analysis - 201": (r) => r.status === 201,
  });

  if (!isSubmitSuccess) {
    console.log(`❌ Gagal submit saat VU ${__VU} | iteration ${__ITER} | status: ${submitRes.status}`);
    sleep(1);
    return;
  }

  const questionId = submitRes.json('id');
  sleep(1);

  // 2. Get submitted question
  const getRes = http.get(`${BASE_URL}/question/${questionId}/`);
  const isGetSuccess = check(getRes, {
    "Success: Get Analysis - 200": (r) => r.status === 200,
  });

  if (!isGetSuccess) {
    console.log(`❌ Gagal GET saat VU ${__VU} | iteration ${__ITER} | status: ${getRes.status}`);
  }

  sleep(1);

  // 3. Submit cause
  const causePayload = JSON.stringify({
    question_id: questionId,
    cause: "Sample cause for testing",
    row: 1,
    column: 1,
    mode: "PRIBADI",
  });

  const causeRes = http.post(`${BASE_URL}/cause/`, causePayload, { headers: HEADERS });
  const isCauseSuccess = check(causeRes, {
    "Success: Submit Cause - 201": (r) => r.status === 201,
  });

  if (!isCauseSuccess) {
    console.log(`❌ Gagal submit cause saat VU ${__VU} | iteration ${__ITER} | status: ${causeRes.status}`);
  }

  sleep(1);
}
