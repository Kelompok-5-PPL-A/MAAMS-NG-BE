import http from 'k6/http';
import { sleep, check } from 'k6';

export let options = {
  stages: [
    { duration: '30s', target: 50 },
    { duration: '1m', target: 300 },
    { duration: '2m', target: 1000 }, // Stress peak
    { duration: '1m', target: 200 },
    { duration: '30s', target: 0 },
  ],
};

const BASE_URL = 'http://127.0.0.1:8000';
const headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
};

let counter = 1;

export default function () {
  const randomTitle = `Test ${counter++}`;
  
  const submitPayload = JSON.stringify({
    mode: "PRIBADI",
    question: "Load testing simulation question",
    tags: ["tag1", "tag2"],
    title: randomTitle,
  });

  const submitRes = http.post(`${BASE_URL}/question/submit/`, submitPayload, { headers });

  const submitOk = check(submitRes, {
    "Submit Analysis - Status is 201": (r) => r.status === 201,
  });

  if (!submitOk) {
    sleep(1);
    return; // Skip further steps if submit failed
  }

  const questionId = submitRes.json('id');
  sleep(1);

  const getRes = http.get(`${BASE_URL}/question/${questionId}/`);

  const getOk = check(getRes, {
    "Get Analysis - Status is 200": (r) => r.status === 200,
  });

  if (!getOk) {
    sleep(1);
    return;
  }

  const causePayload = JSON.stringify({
    question_id: questionId,
    cause: "Sample cause for testing",
    row: 1,
    column: 1,
    mode: "PRIBADI",
  });

  const causeRes = http.post(`${BASE_URL}/cause/`, causePayload, { headers });

  check(causeRes, {
    "Submit Cause - Status is 201": (r) => r.status === 201,
  });

  sleep(1);
}
