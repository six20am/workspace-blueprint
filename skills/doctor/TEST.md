# Test: doctor

## The ask
"Something feels broken. Can you check my tools?"

## The input
A workspace where most tools are present, one program is missing, and two sign-ins are not done.

## Done looks like
The skill runs `python tools/doctor/doctor.py` once, installs only the missing program, reports the three lines in two plain sentences, and lists the two sign-ins without typing any credential.
