import http from 'k6/http';
import { sleep, check } from 'k6';

export let options = {
  stages: [
    { duration: '30s', target: 10 },  // Naik ke 10 user dalam 30 detik
    { duration: '1m', target: 50 },   // Naik ke 50 user dalam 1 menit
    { duration: '2m', target: 100 },  // Peak load di 100 user selama 2 menit
    { duration: '1m', target: 50 },   // Turun ke 50 user selama 1 menit
    { duration: '30s', target: 0 },   // Turun ke 0 user
  ],
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
  
  let submitRes = http.post(`${BASE_URL}/question/submit/`, JSON.stringify({
    title: randomTitle,
    question: "Load testing simulation question",
    mode: "PRIBADI"
  }), { 
    headers: { 
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    } 
  });

  console.log(`Question submission response: ${submitRes.status} - ${submitRes.body}`);

  check(submitRes, {
    "Submit Analysis - Status is 201": (r) => r.status === 201,
  });

  if (submitRes.status === 201) {
    try {
      let questionId = submitRes.json('id');
      console.log(`Created question with ID: ${questionId}`);
      
      sleep(1);

      let getRes = http.get(`${BASE_URL}/question/${questionId}/`);
      console.log(`Get question response: ${getRes.status} - ${getRes.body}`);
      
      check(getRes, {
        "Get Analysis - Status is 200": (r) => r.status === 200,
      });

      sleep(1);

      const causePayload = {
        question_id: questionId,
        cause: "Sample cause for testing",
        row: 1,
        column: 1,
        mode: "PRIBADI"
      };
      console.log(`Submitting cause with payload: ${JSON.stringify(causePayload)}`);

      let causeRes = http.post(`${BASE_URL}/cause/`, JSON.stringify(causePayload), { 
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        } 
      });

      console.log(`Cause submission response: ${causeRes.status} - ${causeRes.body}`);

      check(causeRes, {
        "Submit Cause - Status is 201": (r) => r.status === 201,
      });
    } catch (e) {
      console.log(`Error processing question: ${e.message}`);
    }
  }

  sleep(1);
}
