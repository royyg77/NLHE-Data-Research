/*
 * 01_pool_overview.sql 
 * 
 * Purpose: Define the analyzed pool for v1 and provide context for the main strategy analysis.
 * 
 * Output: bb_size, pf_action, number_hands, pct_hands_see_flop, avg_players_to_flop, pct_flop_hu, pct_flop_mw
 * 
 * Notes: 
 * - Only includes stake levels with at least 10,000 total hands. 
 * - pct_flop_hu and pct_flop_mw are conditional on a flop being seen. 
 * - Percent columns are returned as proprotions from 0 to 1.
 *  
 */


WITH base_hands AS (
    SELECT
        chs.id_hand,
        ROUND(cl.amt_bb::numeric, 2) AS bb_size,
        COALESCE(chs.cnt_players_f, 0) AS cnt_players_f,
        CHAR_LENGTH(chs.str_aggressors_p::text) AS aggressor_len
    FROM cash_hand_summary chs
    JOIN cash_limit cl
        ON chs.id_limit = cl.id_limit
),
eligible_stakes AS (
    SELECT
        bb_size
    FROM base_hands
    GROUP BY
        bb_size
    HAVING COUNT(*) >= 10000
),
hand_pool AS (
    SELECT
        id_hand,
        bb_size,
        cnt_players_f,
        'All' AS pf_action
    FROM base_hands

    UNION ALL

    SELECT
        id_hand,
        bb_size,
        cnt_players_f,
        CASE
            WHEN aggressor_len = 2 THEN 'SRP'
            WHEN aggressor_len = 3 THEN '3BP'
            WHEN aggressor_len >= 4 THEN '4BP+'
        END AS pf_action
    FROM base_hands
    WHERE aggressor_len >= 2
)
SELECT
    hp.bb_size,
    hp.pf_action,
    COUNT(*) AS number_hands,
    ROUND(
        AVG(CASE WHEN hp.cnt_players_f > 0 THEN 1.0 ELSE 0.0 END),
        4
    ) AS pct_hands_see_flop,
    ROUND(
        AVG(CASE WHEN hp.cnt_players_f > 0 THEN hp.cnt_players_f::numeric END),
        2
    ) AS avg_players_to_flop,
    ROUND(
        SUM(CASE WHEN hp.cnt_players_f = 2 THEN 1 ELSE 0 END)::numeric
        / NULLIF(SUM(CASE WHEN hp.cnt_players_f > 0 THEN 1 ELSE 0 END), 0),
        4
    ) AS pct_flop_hu,
    ROUND(
        SUM(CASE WHEN hp.cnt_players_f > 2 THEN 1 ELSE 0 END)::numeric
        / NULLIF(SUM(CASE WHEN hp.cnt_players_f > 0 THEN 1 ELSE 0 END), 0),
        4
    ) AS pct_flop_mw
FROM hand_pool hp
JOIN eligible_stakes es
    ON hp.bb_size = es.bb_size
GROUP BY
    hp.bb_size,
    hp.pf_action
ORDER BY
    hp.bb_size,
    CASE hp.pf_action
        WHEN 'All' THEN 1
        WHEN 'SRP' THEN 2
        WHEN '3BP' THEN 3
        WHEN '4BP+' THEN 4
        ELSE 5
    END;

