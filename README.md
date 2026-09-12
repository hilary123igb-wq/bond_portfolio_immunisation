# Bond Portfolio Immunization with Stochastic Yield Forecasting

A $1,000,000 fixed-income portfolio built from four bonds across different maturities and credit ratings, with interest rate risk measured two ways: a deterministic 1% rate shock, and a state-space (Kalman filter) forecast that prices in historical volatility.

## The portfolio

| Bond | Weight | Allocation | Coupon | Maturity | Rating | Modified duration |
|---|---|---|---|---|---|---|
| Belgium 30Y (2054) | 40% | $400,000 | 3.30% | 30 years | AA | 18.62 |
| UK 4Y (2029) | 30% | $300,000 | 0.50% | 4 years | AA | 4.75 |
| International Paper 2048 | 20% | $200,000 | 4.35% s/a | 23 years | BBB | 13.85 |
| Bausch Health 2027 | 10% | $100,000 | 6.13% s/a | 2 years | CC | 1.66 |

Weights are tilted toward the two sovereigns to keep default risk low, with a small high-yield position in Bausch Health for return. The two corporates sit in unrelated sectors (packaging and pharmaceuticals), so sector-wide shocks hit only part of the book.

**Weighted modified duration: 11.81 years**

## Results

**Deterministic method.** A uniform 1% rise in rates implies a portfolio loss of roughly $118,000, concentrated almost entirely in the two long-duration holdings (Belgium alone accounts for about $74,000).

**Stochastic method.** Assuming a flat 1% shift is arbitrary, as it ignores how much rates actually move. Instead, 150 days of yield movements are simulated as a random walk calibrated to the 3.65% ECB benchmark, and a local-level state-space model separates the underlying yield from market noise. Forecasting 12 steps ahead gives a 95% confidence band:

| Metric | Value |
|---|---|
| Current benchmark yield | 2.66% |
| 95% confidence upper bound | 3.14% |
| Implied adverse shift | 0.47% |
| Projected portfolio loss | ~$56,000 |

The probabilistic worst case is well under half the deterministic estimate, which suggests the 1% shock was a conservative assumption rather than a realistic one.

## Immunization

The target liability duration is 10 years against a portfolio duration of 11.81, so the book is over-exposed. Closing the gap means cutting the Belgium 30Y weight and adding to the UK 4Y and Bausch Health positions.

Because the Kalman filter produces a forecast distribution rather than a point estimate, rebalancing can account for duration drift (durations themselves shift as rates move) which makes the match to the liability hold up better over time.

Practical constraints on all of this:

- The corporate bonds are denominated at $2,000 per bond against $1,000 for the sovereigns, and fractional bonds can't be bought.
- Frequent rebalancing incurs brokerage costs.
- A sharp inflation surprise erodes the real value of fixed coupons regardless of duration matching. Inflation-linked bonds would partly address this.

## Running the code

```bash
pip install -r requirements.txt
python bond_portfolio_analysis.py
```

Prints the portfolio table, duration, forecast bounds and projected loss, then opens a chart of the observed yield path with the forecast and its confidence band.

## Repository contents

| File | Purpose |
|---|---|
| `bond_portfolio_analysis.py` | Portfolio duration, yield simulation, Kalman filter forecast, loss calculation |
| `requirements.txt` | Python dependencies |
| `README.md` | This file |

## Method notes and limitations

- The yield path is simulated, not historical. Calibrating to the ECB benchmark makes the level realistic, but the volatility assumption (0.08% daily) is an input rather than something estimated from data. Using real yield history would be the obvious next step.
- `np.random.seed(42)` fixes the simulation, so the numbers above reproduce exactly on any machine.
- Loss is estimated from modified duration alone, a first-order approximation. It overstates losses and understates gains for large rate moves because it ignores convexity.
- Modified durations were computed in Excel assuming settlement and maturity both fall on 1 January, which slightly simplifies accrual.
- Bond prices, ratings and macro figures were sourced in November 2024 and are not live.

