-- 1. ตรวจจำนวนข้อมูลทั้งหมด

SELECT
    COUNT(*) AS total_rows
FROM payments;


-- 2. ตรวจชื่อ Influencer ที่ว่าง

SELECT
    COUNT(*) AS missing_influencer_names
FROM payments
WHERE influencer_name IS NULL
   OR TRIM(influencer_name) = '';


-- 3. ตรวจ Budget ที่ไม่ถูกต้อง

SELECT
    COUNT(*) AS invalid_budgets
FROM payments
WHERE budget IS NULL
   OR budget <= 0;


-- 4. ตรวจข้อมูลซ้ำ

SELECT
    influencer_name,
    budget,
    post_date,
    payment_round,
    payment_status,
    expense_type,
    COUNT(*) AS duplicate_count
FROM payments
GROUP BY
    influencer_name,
    budget,
    post_date,
    payment_round,
    payment_status,
    expense_type
HAVING COUNT(*) > 1;


-- 5. ตรวจประเภทค่าใช้จ่ายที่ไม่รู้จัก

SELECT
    DISTINCT expense_type
FROM payments
WHERE expense_type NOT IN (
    'influencer_fee',
    'shipping',
    'operations',
    'packaging'
);


-- 6. ตรวจรายการที่ไม่มีวันที่โพสต์

SELECT
    COUNT(*) AS missing_post_dates
FROM payments
WHERE post_date IS NULL;