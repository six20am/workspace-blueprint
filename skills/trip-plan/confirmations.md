# Reading confirmations into one table

## What counts as a confirmation

Airline, hotel or rental, car, train or bus, tour or ticket. Each may be a pasted email, a PDF, a screenshot or a note. Read the whole thing; the useful line is often at the bottom (check-out time, pickup desk, baggage rule).

## The table

One row per event, sorted by date, then time. A flight with a connection is one row per leg. A hotel is one row for check-in and one for check-out. A rental car is one row for pickup and one for return.

| Date | Time | Place | What | Reference | Paid or not |
|---|---|---|---|---|---|

- **Date:** the date at that place, written `YYYY-MM-DD`.
- **Time:** local time at that place, 24 hour. Blank if not stated. Note the zone if it differs from the rest of the trip.
- **Place:** airport code and city, hotel name and city, station, rental desk. Name only; follow the privacy pass in `SKILL.md`.
- **What:** flight number and route, "check in", "check out", "pick up car", "train 1 of 2", the tour name.
- **Reference:** the booking or confirmation code exactly as printed. Blank if none.
- **Paid or not:** one of `paid`, `pay at arrival`, `deposit only`, `not stated`. Use `paid` only when the confirmation says paid, charged or payment received. "Booked" alone is `not stated`.

## Where each kind hides its facts

- **Airline:** each leg's departure and arrival times are local to each airport; look for "+1". The reference is the record locator, usually six characters. The fare paid shows near the total.
- **Hotel:** check-in and check-out are dates; the time is usually "from 15:00" and "until 11:00". Count nights from the two dates. Payment is often "pay at the property".
- **Car:** pickup and return are two rows, often at different times than expected. Note the desk or lot. A deposit hold is `deposit only`.
- **Train or bus:** seat and coach go in What. Times are local to each station.
- **Tour or ticket:** the start time, meeting point and any arrive-early instruction go in What. A ticket with no time says "any time that day".

## Conflicts and gaps in the paperwork

- Two confirmations that disagree (a hotel date that does not match the flight): keep both rows and flag the conflict above the table. Do not pick one.
- A confirmation with no date: ask the person once. If unanswered, leave it out of the table and list it under "could not place".
- A cancelled booking: leave it in the table marked "cancelled" so the gap shows in the check below.

## The "still unbooked" check

Run this after the table is built. List every gap with its date, in order.

1. **A night with no hotel.** For each night from the first arrival to the night before the last departure, some stay must cover it: check-in on or before that date, check-out after it. A night spent on an overnight flight or train, or at a place the person says is arranged (family, friends), is covered. Anything else is unbooked.
2. **A leg with no transport.** Between each two consecutive places in the table, something must carry the traveler: a flight, a train, a car pickup and return, or a ride the person says is arranged. Check both ends too: a way from home to the first place and back from the last. A rental car picked up but never returned is a gap.
3. **A day with no plan.** Any date between arrival and departure with no row at all, apart from check-in, check-out and travel. List it as "open day". An open day is information, not an error; say it that way.

Write each gap as one line: `2026-05-14: no hotel (check-out at Harbor Inn on the 13th, next check-in on the 15th)`. Never suggest a specific booking and never make one.

## After the table

Count the rows, the nights and the gaps, and say all three in your reply, so a missed confirmation shows up as a number that is too low.
