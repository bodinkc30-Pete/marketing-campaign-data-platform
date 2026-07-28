-- 1. สรุปค่าใช้จ่ายแยกตามประเภท

SELECT
    expense_type,
    COUNT(*) AS expense_count,
    SUM(budget) AS total_budget,
    ROUND(AVG(budget), 2) AS average_budget
FROM payments
GROUP BY expense_type
ORDER BY total_budget DESC;


-- 2. ค่าจ้าง Influencer ต่ำสุด

SELECT
    influencer_name,
    budget,
    post_date,
    payment_round,
    payment_status
FROM payments
WHERE expense_type = 'influencer_fee'
ORDER BY budget ASC
LIMIT 10;


-- 3. ค่าจ้าง Influencer สูงสุด

SELECT
    influencer_name,
    budget,
    post_date,
    payment_round,
    payment_status
FROM payments
WHERE expense_type = 'influencer_fee'
ORDER BY budget DESC
LIMIT 10;