/*
 * 03_texture_frequency.sql
 * 
 * Purpose: Measure how often each flop texture occurs within dataset. 
 * 
 * Output cols: bb_size, num_players, pairedness, suitedness, occurrences, total_flops, texture_frequency
 * 
 */

WITH base AS (
    SELECT DISTINCT
        chs.id_hand,
        ROUND(cl.amt_bb::numeric, 2) AS bb_size,
        CASE
            WHEN chs.cnt_players_f = 2 THEN 'HU'
            WHEN chs.cnt_players_f > 2 THEN 'MW'
        END AS num_players,
        CASE
            WHEN ((chs.card_1 - 1) % 13) = ((chs.card_2 - 1) % 13)
             AND ((chs.card_2 - 1) % 13) = ((chs.card_3 - 1) % 13) THEN 'Trips'
            WHEN ((chs.card_1 - 1) % 13) = ((chs.card_2 - 1) % 13)
              OR ((chs.card_1 - 1) % 13) = ((chs.card_3 - 1) % 13)
              OR ((chs.card_2 - 1) % 13) = ((chs.card_3 - 1) % 13) THEN 'Paired'
            ELSE 'Unpaired'
        END AS pairedness,
        CASE
            WHEN FLOOR((chs.card_1 - 1) / 13.0) = FLOOR((chs.card_2 - 1) / 13.0)
             AND FLOOR((chs.card_2 - 1) / 13.0) = FLOOR((chs.card_3 - 1) / 13.0) THEN 'Monotone'
            WHEN FLOOR((chs.card_1 - 1) / 13.0) <> FLOOR((chs.card_2 - 1) / 13.0)
             AND FLOOR((chs.card_1 - 1) / 13.0) <> FLOOR((chs.card_3 - 1) / 13.0)
             AND FLOOR((chs.card_2 - 1) / 13.0) <> FLOOR((chs.card_3 - 1) / 13.0) THEN 'Rainbow'
            ELSE '2Tone'
        END AS suitedness
    FROM cash_hand_summary chs
    JOIN cash_limit cl
        ON chs.id_limit = cl.id_limit
    JOIN cash_hand_player_statistics chps
        ON chs.id_hand = chps.id_hand
    WHERE ROUND(cl.amt_bb::numeric, 2) IN (0.02, 0.05, 0.10)
      AND CHAR_LENGTH(chs.str_aggressors_p::text) = 2
      AND chps.flg_f_cbet_opp = TRUE
      AND chs.card_1 BETWEEN 1 AND 52
      AND chs.card_2 BETWEEN 1 AND 52
      AND chs.card_3 BETWEEN 1 AND 52
      AND chs.cnt_players_f >= 2
),
agg AS (
    SELECT
        bb_size,
        num_players,
        pairedness,
        suitedness,
        COUNT(*) AS occurrences
    FROM base
    GROUP BY
        bb_size,
        num_players,
        pairedness,
        suitedness
)
SELECT
    bb_size,
    num_players,
    pairedness,
    suitedness,
    occurrences,
    SUM(occurrences) OVER (
        PARTITION BY bb_size, num_players
    ) AS total_flops,
    ROUND(
        occurrences::numeric
        / SUM(occurrences) OVER (PARTITION BY bb_size, num_players),
        4
    ) AS texture_frequency
FROM agg
ORDER BY
    bb_size,
    num_players,
    pairedness,
    suitedness;

