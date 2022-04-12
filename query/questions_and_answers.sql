SELECT qs.QuestionID, QuestionTitle, QuestionText, count(*) CountAnswers,
# GROUP_CONCAT(ans.AnswerID) AnswerIDs,
GROUP_CONCAT(ans.AnswerContentClean) Answers
FROM sap.questions qs
JOIN answers ans on qs.QuestionID = ans.QuestionID
GROUP BY qs.QuestionID;