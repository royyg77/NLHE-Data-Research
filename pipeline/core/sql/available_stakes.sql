-- available_stakes.sql
-- Distinct stakes (bb_size) that actually appear in the hand data, using the
-- same ROUND(cl.amt_bb::numeric, 2) expression the studies filter on so the
-- values line up exactly with what --stake accepts.
SELECT DISTINCT
    ROUND(cl.amt_bb::numeric, 2) AS bb_size
FROM cash_hand_summary chs
JOIN cash_limit cl
    ON chs.id_limit = cl.id_limit
ORDER BY bb_size;

