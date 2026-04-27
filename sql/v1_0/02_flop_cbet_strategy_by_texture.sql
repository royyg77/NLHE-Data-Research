/* 02_flop_cbet_strategy_by_texture.sql
 * 
 * Purpose: Build the main v1 strategy summary table for flop continuation-betting in single-raised pots (SRPs) showing how cbet frequency and conditional size selection vary by board texture
 * 
 * Derived Metrics:
 * - cbet_opportunities: number of flop c-bet opportunities
 * - cbets: number of c-bets made, given flop c-bet opportunity
 * - cbet_frequency: cbets / cbet_opportunities
 * - bet_ratio: flop bet size as a proportion of flop pot size
 * - size buckets:
 *   - Small:   > 0 to 0.35 pot
 *   - Medium:  > 0.35 to 0.60 pot
 *   - Large:   > 0.60 to 1.00 pot
 *   - Overbet: > 1.00 pot
 * 
 * Output: bb_size, player_bucket, relative_position, pairedness, suitedness, cbet_opportunities, cbets, cbet_frequency, small_pct, medium_pct, large_pct, overbet_pct 
 * 
 * Note: size percentages are conditional on a c-bet occurring
 * 
 */


WITH base AS (
    SELECT
        ROUND(cl.amt_bb::numeric, 2) AS bb_size,
        CASE
            WHEN chs.cnt_players_f = 2 THEN 'HU'
            WHEN chs.cnt_players_f > 2 THEN 'MW'
        END AS player_bucket,
        CASE
            WHEN chps.flg_f_has_position = TRUE THEN 'IP'
            ELSE 'OOP'
        END AS relative_position,
        ((chs.card_1 - 1) % 13) AS r1,
        ((chs.card_2 - 1) % 13) AS r2,
        ((chs.card_3 - 1) % 13) AS r3,
        FLOOR((chs.card_1 - 1) / 13.0) AS s1,
        FLOOR((chs.card_2 - 1) / 13.0) AS s2,
        FLOOR((chs.card_3 - 1) / 13.0) AS s3,
        chps.flg_f_cbet,
        CASE
            WHEN chps.flg_f_cbet = TRUE AND chs.amt_pot_f > 0
                THEN ROUND(chps.amt_bet_f::numeric / chs.amt_pot_f, 2)
            ELSE NULL
        END AS bet_ratio
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
)
SELECT
    bb_size,
    player_bucket,
    relative_position,
    CASE
        WHEN r1 = r2 AND r2 = r3 THEN 'Trips'
        WHEN r1 = r2 OR r1 = r3 OR r2 = r3 THEN 'Paired'
        ELSE 'Unpaired'
    END AS pairedness,
    CASE
        WHEN s1 = s2 AND s2 = s3 THEN 'Monotone'
        WHEN s1 <> s2 AND s1 <> s3 AND s2 <> s3 THEN 'Rainbow'
        ELSE '2Tone'
    END AS suitedness,
    COUNT(*) AS cbet_opportunities,
    SUM(CASE WHEN flg_f_cbet = TRUE THEN 1 ELSE 0 END) AS cbets,
    ROUND(
        SUM(CASE WHEN flg_f_cbet = TRUE THEN 1 ELSE 0 END)::numeric / COUNT(*),
        4
    ) AS cbet_frequency,
    ROUND(
        SUM(CASE
            WHEN flg_f_cbet = TRUE AND bet_ratio > 0 AND bet_ratio <= 0.35 THEN 1
            ELSE 0
        END)::numeric
        / NULLIF(SUM(CASE WHEN flg_f_cbet = TRUE THEN 1 ELSE 0 END), 0),
        4
    ) AS small_pct,
    ROUND(
        SUM(CASE
            WHEN flg_f_cbet = TRUE AND bet_ratio > 0.35 AND bet_ratio <= 0.60 THEN 1
            ELSE 0
        END)::numeric
        / NULLIF(SUM(CASE WHEN flg_f_cbet = TRUE THEN 1 ELSE 0 END), 0),
        4
    ) AS medium_pct,
    ROUND(
        SUM(CASE
            WHEN flg_f_cbet = TRUE AND bet_ratio > 0.60 AND bet_ratio <= 1.00 THEN 1
            ELSE 0
        END)::numeric
        / NULLIF(SUM(CASE WHEN flg_f_cbet = TRUE THEN 1 ELSE 0 END), 0),
        4
    ) AS large_pct,
    ROUND(
        SUM(CASE
            WHEN flg_f_cbet = TRUE AND bet_ratio > 1.00 THEN 1
            ELSE 0
        END)::numeric
        / NULLIF(SUM(CASE WHEN flg_f_cbet = TRUE THEN 1 ELSE 0 END), 0),
        4
    ) AS overbet_pct
FROM base
GROUP BY
    bb_size,
    player_bucket,
    relative_position,
    pairedness,
    suitedness 
ORDER BY
    bb_size,
    player_bucket,
    relative_position,
    pairedness,
    suitedness;



