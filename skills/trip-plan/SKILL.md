---
name: trip-plan
description: "Turns pasted or filed booking confirmations into one itinerary page in date order, plus a list of what is still unbooked. Use when the person asks for their itinerary, or hands over flight, hotel, car, train or tour confirmations."
---

# trip-plan

Use this when the person says "make my itinerary" or hands over confirmations: airline, hotel, car, train, tour. Bookings in, one itinerary page out, plus the list of what is still unbooked.

## Never

- Book, change, cancel or pay for anything. This skill reads and writes a page, nothing else.
- Email, post or upload the page. Save it and say where it is; the person sends it.
- Invent a time, a reference or a price. A blank cell says "not in the confirmation".

## Steps

1. **Collect everything.** Every confirmation pasted in the chat and every file the person points to. For PDF, Word or email files use the `markitdown` skill. Read each one whole.
2. **Ask only what is missing.** Who is traveling, the trip dates if no booking shows them, and where the page should be saved. Draft with `[fill in]` for anything else and flag it.
3. **Build the table** by `confirmations.md`: one row per event, sorted by date and time, with date, time, place, what, reference, paid or not.
4. **Run the unbooked check** from `confirmations.md`: a night with no hotel, a leg with no transport, a day with no plan. This list goes in the checklist on the page and in your reply.
5. **Render the page** from `template.html`. Copy it, then fill it in:
   - One `<section class="day">` per date, with `data-date` (ISO) and `data-title`. Each table row becomes an item with its time, a bold title, and one or two sentences.
   - Put the reference and "paid" or "to pay" in each item. Use the `book` tag for anything still unbooked and the `price` tag for a stated amount.
   - Put the unbooked list in the checklist panel, one checkbox each.
   - Set the countdown to the first arrival and the last departure, in the destination's time zone (see below).
   - Use the `neutral-modern` theme unless the person asks for another. The theme is one attribute on the `<html>` tag. Keep it plain; legibility on a phone beats decoration.
6. **Privacy pass** (below), before the page is saved.
7. **Save the page** beside the confirmations as `itinerary.html` (or `itinerary-<place>.html` if there is more than one trip). Say where it landed in one line.
8. **Reply** in three short parts: the dates the page covers, what is still unbooked, and anything you could not read.

## The time check

A flight's departure date is the day the traveler leaves, not the day they land. A long or overnight flight often lands the next calendar day, marked "+1". Before writing the arrival time into the countdown, add the flight time to the departure and check the date against the destination's time zone. Write the countdown with the destination's UTC offset, not the traveler's home offset. If a confirmation gives only local times, keep them local in the table and say so.

## Privacy pass

- **Hotel or named rental:** the property name and neighborhood are fine. Leave out room and unit numbers.
- **Someone's private home:** never write the address, building name or exact neighborhood, even if the person typed it. Write "the address I sent you". Do it everywhere the place appears, including route descriptions, not just one card.
- **Never put on the page:** passport or ID numbers, card numbers, loyalty or login details, or phone numbers of people who did not ask to be listed. The reference column holds the booking reference only.
- If the page might be screenshotted, shared or hosted at a guessable address, assume it will be.

## Before you hand it over

- Dates and time zones match the confirmations, row by row.
- Every table row shows on the page; every unbooked gap is listed.
- No address, ID or payment detail beyond what the privacy pass allows.
- No emoji, no em dashes, and the page opens with no network (no web fonts, no outside scripts).
- Checkboxes cross out their label when checked, and the day tabs still scroll with the page.
- Open the file once and read it as the traveler would on a phone.

## When plans change

Edit the one row or day that changed. Do not regenerate the page; the person may have edited other parts. Re-run the unbooked check after every change.

Adapted from AdeDeepFishing/trip-itinerary-page (MIT).
