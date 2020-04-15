SELECT
 person_id,
 test.id as test_id,
 test.time as test_time,
 test.result as test_result,
 C1.eval_count,
 C1.test_no_symptoms_count,
 C1.test_symptoms_count,
 CASE 
    WHEN (test.RESULT = "symptoms" AND test_no_symptoms_count = 0) THEN "SYMPTOM" 
    WHEN (test.RESULT = "no-symptoms" AND test_symptoms_count = 0) THEN "NO_SYMPTOM"
    WHEN (test.RESULT = "symptoms" AND test_no_symptoms_count > 0) THEN "TO_SYMPTOM"
    WHEN (test.RESULT = "no-symptoms" AND test_symptoms_count > 0) THEN "TO_NO_SYMPTOM"
 END as user_type
FROM ${TABLE_ID} C
JOIN (
  SELECT
    person_id as person_id1,
    COUNT(*) as eval_count,
    COUNTIF(test.result like "no-symptoms") as test_no_symptoms_count,
    COUNTIF(test.result like "symptoms") as test_symptoms_count,
    MAX(test.time) as latest_test_time
  FROM ${TABLE_ID}
  GROUP BY person_id
) C1
ON C.person_id = C1.person_id1 AND C.test.time = latest_test_time
ORDER BY PERSON_ID,TEST.TIME DESC