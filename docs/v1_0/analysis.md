# Introduction

This study examines flop continuation-bet strategy in single-raised pots (SRPs) using hand-history data stored in a PokerTracker 4 PostgreSQL database. The focus of version 1 is to analyze how flop c-bet behavior varies by board texture across pooled microstakes (2nl, 5nl, and 10nl) data.

The main strategy question is split into two related components: how often the pool continuation-bets on a given texture, and how the pool distributes its c-bet sizings once it chooses to bet. Board texture is defined using pairedness and suitedness, while the final grouped strategy outputs are segmented by blind level, relative position, and heads-up versus multiway flop context.

# Key Takeaways

- Position is the dominant driver of flop c-bet frequency. Across every stake and texture, IP c-bet frequency exceeds OOP by 10–17 percentage points. Wilson 95% CIs do not overlap between IP and OOP within any high-sample texture — the position effect is statistically clean, not a sampling artifact.

- Texture effects exist but are secondary. Holding position fixed, c-bet frequency varies by 5–10 percentage points across textures, with Unpaired 2Tone the highest-frequency surface and Paired Rainbow / Unpaired Monotone the lowest. The pattern is consistent across stakes.

- Size selection skews small-to-medium, with large sizes making up most of the remainder and overbets used sparingly (4–8%). 10nl shows a directional shift toward larger sizes on common textures relative to 2nl and 5nl.

- Multiway flops concentrate in SRPs. 3-bet and 4-bet+ pots reach the flop heads-up over 80% of the time, making SRPs the natural focus for any population-level multiway analysis.

- Texture frequencies are nearly identical across the 2nl, 5nl, and 10nl pools, but SRP flop-seen rates differ enough that downstream strategy comparisons should account for different preflop range compositions.


# Part 1: Pool Overview

The pool covers 130,050 hands at 2nl, 42,082 at 5nl, 54,340 at 10nl, and 12,953 at 30nl. Stake-level samples are uneven, and 30nl in particular sits close to the 10,000-hand inclusion threshold — its frequencies should be read with more caution than the others. SRPs dominate raised preflop action across all stakes (roughly 80%+), followed by 3BPs, with 4BP+ pots making up a small share.

SRP flop-seen rates are noticeably higher at 10nl and 30nl (~64% and ~60%) than at 2nl and 5nl (~52% and ~51%). Because the downstream c-bet analysis is restricted to SRPs, this is significant as the SRP flops being compared across stakes were not generated from identical preflop calling tendencies. Wider preflop calling at higher stakes can carry through into different range compositions on the flop, independent of any postflop strategy difference.

The most structurally important finding is the HU vs MW split. Multiway flops are concentrated almost entirely in SRPs, while 3-bet and 4-bet+ pots reach the flop heads-up the vast majority of the time (>80% HU in 3BPs, >90% in 4BP+ pots). HU and MW postflop strategy cannot be treated as interchangeable, and SRPs are the natural focus for population c-bet study because they are where multiway flops are practically relevant.

One anomaly worth flagging: 10nl shows the highest multiway flop rate in the sample, higher than both 2nl and 5nl. Whether this reflects a genuine pool tendency or sample composition isn't clear from this data alone, but it makes 10nl a useful pool for future study of exploitative adjustments against multiple callers.

Although 30nl cleared the 10,000-hand inclusion threshold, the resulting flop sample is too thin to support stable per-texture estimates, and is excluded from texture and strategy analysis. The Pool Overview retains all four stakes for context.


# Part 2: Texture Prevalence

Pooled across the 2nl, 5nl, and 10nl SRP sample, board textures fall into a clear hierarchy. Unpaired two-tone boards are the most common at 45.98% (95% CI: 45.59%–46.36%), followed by unpaired rainbow at 31.34% (95% CI: 30.99%–31.70%). Paired rainbow and paired two-tone occur at similar rates, 8.69% (95% CI: 8.48%–8.91%) and 8.49% (95% CI: 8.28%–8.71%) respectively. Unpaired monotone boards account for 5.26% (95% CI: 5.09%–5.43%), and tripped rainbow boards are rare at 0.24% (95% CI: 0.20%–0.28%).

These frequencies are nearly identical across the three stakes (visible in the heatmaps by stake). Texture distribution is a property of the deck and the randomized dealing process, so this is expected — but confirming it is empirically important: it denotes cross-stake strategy comparisons in Part 3 are not distorted by underlying differences in which textures players are facing.

The practical weight of any texture-specific strategy finding in Part 3 depends on both the size of the strategic effect and how often the texture actually occurs. Differences observed on unpaired two-tone or unpaired rainbow boards (which together make up ~77% of flops) carry far more population-level weight than differences observed on tripped boards, where the sample is too thin to support strong claims regardless.


# Part 3: Flop Continuation-bet Strategy in SRP by Texture

Position is the dominant strategic driver. Across every stake and every texture in the analyzable range, IP c-bet frequency exceeds OOP by roughly 10–17 percentage points. On the two most common textures (Unpaired 2Tone and Unpaired Rainbow), IP frequencies sit near 60% while OOP frequencies sit in the mid-40s. The IP-OOP gap is larger and more consistent than the gap between any two textures within a single position — the pool's c-bet decision is shaped more by whether they have position than by the board itself. This pattern holds at all three stakes and is robust to sample-size variation. Wilson 95% CIs are tight on the high-volume cells and never overlap between IP and OOP within a texture.

Texture effects within position are real but modest. Holding position fixed, c-bet frequency moves predictably with texture: highest on Unpaired 2Tone (the most common dynamic surface), and lowest on Paired Rainbow and Unpaired Monotone. Within IP, the spread across textures is roughly 8–10 percentage points; within OOP, closer to 5. The directional pattern is consistent across stakes, but the magnitudes are small relative to the position effect.

Size selection skews small-to-medium with stake-dependent shift toward larger sizes. Across textures and positions, small and medium bets account for roughly 65–80% of all c-bets, with large sizes making up most of the remainder and overbets used sparingly (typically 4–8%). One trend visible across stakes: large% rises at 10nl. On Unpaired 2Tone the IP large share moves from ~21% at 2nl/5nl to ~27% at 10nl, with a parallel shift on Unpaired Rainbow (~17–19% at 2nl/5nl, ~22–25% at 10nl). This suggests a higher proportion of the 10nl pool implements a more aggressive strategy with bigger flop bets, though smaller sample sizes on rarer textures make the trend more directional than definitive.

A note on sample size. Trips Rainbow appears in every stake's results but is excluded from the interpretations above. The wide Wilson CIs on the chart make the unreliability evident — at 5nl, IP and OOP cells contain only 11 and 10 c-bet opportunities respectively, with the OOP cell representing 4 total c-bets. Any percentage shown for these cells should be read as noise.