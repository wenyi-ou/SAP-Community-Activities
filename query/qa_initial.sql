SELECT qs.QuestionID, QuestionTitle, QuestionText, 
GROUP_CONCAT(DISTINCT ans.AnswerContentClean ORDER BY ans.AnswerTimeStamp ASC SEPARATOR '-:::-') Answers,
GROUP_CONCAT(DISTINCT qs_cmts.CommentContent ORDER BY qs_cmts.CommentTimeStamp ASC SEPARATOR '-:::-') QuestionComments,
GROUP_CONCAT(DISTINCT ans_cmts.CommentContent ORDER BY ans_cmts.CommentTimeStamp ASC SEPARATOR '-:::-') AnswerComments
FROM sap.questions qs
JOIN answers ans on qs.QuestionID = ans.QuestionID 
LEFT JOIN comments qs_cmts on qs.QuestionID = qs_cmts.ParentQuestionID
LEFT JOIN comments ans_cmts on ans.AnswerID = ans_cmts.ParentAnswerID
GROUP BY qs.QuestionID;