# Financial Plan

Charlie's personal financial planner — the web-app successor to a Numbers
spreadsheet kept since 2011. A monthly budget that projects itself forward,
with the tabs that hang off it: savings goals, retirement, tax, investments,
giving, trips and the household the plan is for.

**Live at <https://eagleadams86.github.io/financial-plan/>**

No account. No install. Nothing uploaded. Your figures live in your own
browser and stay there unless you deliberately sign in or send a link.

## Contents

**Using It**
[Start Here](#start-here) ·
[Where Your Data Lives](#where-your-data-lives) ·
[Getting Around](#getting-around) ·
[Preferences](#preferences) ·
[Themes](#themes)

**The Tabs**
[Budget](#budget) ·
[Progress](#progress) ·
[Vacations](#vacations) ·
[Giving](#giving) ·
[Investments](#investments) ·
[Retirement](#retirement) ·
[Household](#household) ·
[Compensation](#compensation) ·
[Tax](#tax)

**Beyond One Browser**
[Backups and Starting Over](#backups-and-starting-over) ·
[Comparing Two Plans](#comparing-two-plans) ·
[Share a Read-Only Link](#share-a-read-only-link) ·
[Cross-Device Sync](#cross-device-sync) ·
[Installing It as an App](#installing-it-as-an-app) ·
[Working Offline](#working-offline)

**Under the Hood**
[Architecture](#architecture) ·
[Tests](#tests) ·
[The Migration Scripts](#the-migration-scripts)

---

## Start Here

**The tabs are not there yet, and that is deliberate.** Nine tabs above a
welcome card would every one of them lead to an empty state explaining that
there is nothing there — so nothing is offered until there is something behind
it, the same rule that shows no net-worth tile for a part you have never
recorded. They appear together the moment a plan exists. (A read-only link is
the exception: its tabs are what the sender chose to send.)

Open the page and press **Start Fresh**. That sets up the current year's
budget with a starter set of rows — all renameable, deletable and
reorderable — and every tab's ＋ Add button does the rest. No import, no
account, nothing to configure first.

Because each person's data stays in their own browser, sharing the plain URL
shares the *app*, never the numbers. (A [share link](#share-a-read-only-link)
is the deliberate exception: it carries the figures you picked inside the
link itself.)

Three things worth knowing on day one:

- **Everything is editable, everywhere.** Click any row or cell to change,
  annotate or delete it.
- **Undo covers this sitting.** ⌘Z / Ctrl+Z, or the ↩ Undo button in the
  header.
- **Back up before you experiment.** The **⇩ Back Up** button writes a JSON
  file you can restore later.

## Where Your Data Lives

**This repo is public and holds code only — never data.** Everything you see
in the app lives in your browser's localStorage.

- **Without signing in, the page calls out to exactly one place**:
  api.twelvedata.com, and only if you have added a price-lookup key, carrying
  a ticker symbol and your own key and nothing else.
- **Read-only share links upload nothing.** The figures ride inside the
  link's own `#fragment`, which browsers never send to a server. Creating one
  and opening one are both entirely local, and opening one leaves whatever
  the reader already had saved untouched.
- **Sync is optional.** "Sign In to Sync" (Google) mirrors your data to a
  private Firestore document in the `financialplan-60c6e` Firebase project.
  Security rules confine every account to its own document, sign-in goes
  through Google Identity Services (so it works on corporate networks that
  block firebaseapp.com), and "Delete all data" empties the synced copy too.
  See [Cross-Device Sync](#cross-device-sync).
- **The import files never get committed.** `financial-plan-data.json` and
  `expected-2026.json` are gitignored from the very first commit; `git
  status` must never show them.
- **Backups and screenshots carry more than money.** Since the Household tab
  arrived they can also hold family members' names and birth months,
  children's included — treat those the way you treat the figures.

Full detail in [privacy.html](privacy.html). The app's footer links to it, beside a
**How it works** link back to this README on GitHub (the repo front page renders it) —
the manual for anything the in-app ⓘ dialogs don't cover.

---

## Budget

The monthly grid, 2011–present — the heart of the app, and the part that was
a spreadsheet longest.

Rows are grouped into **Income, Expenses, Transfers and Accounts**, with
per-month subtotals (a section holding a single row skips its subtotal) and a
year-total column pinned to the right.

### Which Way a Transfer Went

A transfer row's figure is **what the move did to the hub** — the account your
pay lands in — which is the same rule the rest of the grid follows, where a
figure below zero is money that left. So −$500 on a Savings row takes $500 out
of the hub and puts it into Savings, and +$500 brings it back the other way.

Which is why a transfer row reads best **named for the other account rather
than for a direction**. One row carries money out in one month and back in the
next, so "To Savings" is right only half the time and "From Savings" is wrong
the other half; the section heading has already said these are transfers, and
the sign says which of the two a given month was. The starter budget and the
sample plan both name their transfer rows exactly as the account is named, and
an **i** on the Transfers heading says so on every plan — the one thing about a
transfer row you cannot work out by looking at it. The exception is a sweep,
which only ever runs one way, so `Sweep to emergency` keeps its direction.

### Year or Month

The Budget has two lenses on the same figures, and a **Year / Month** switch at
the left of the strip along the top picks between them. Whichever you leave it
on is where it opens next time, on every device you sync to.

**Year** is the grid: twelve columns of rows, the shape the spreadsheet had, and
the one for planning a whole year on a wide screen.

**Month** is one month laid out as a page — the shape for a phone, and for
fixing a single row without pinching into a thirteen-column table. It opens on
the current month and steps back and forward with the ‹ › arrows, across a year
end as easily as within one; a **This month** button appears once you have
wandered off it, and the strip itself lists every month the plan holds — this
month underscored wherever it has got to, and every month still to come
underlined with dots, the same mark a year that hasn't begun wears. It draws:

- **The headline figures** — money in (the income rows plus what the accounts
  themselves earned), money out, what was left over, what you only moved, and
  what every account closed the month holding, with how far that moved since the
  month before. **Left over is the one that goes green or red**, since it is the
  only one of the five with a direction of its own: a month that went backwards
  is the thing you most want to spot on the page.
- **Each section as a list, biggest first**, with a bar for each row's share of
  its section and, underneath, where the figure came from: something that
  happened, an estimate of yours, or the rule that worked it out, named. A row
  pointing the other way from its section is a **refund** — cash back, a
  reimbursement — and says it reduced the section rather than making it up;
  money out is what the month really cost you, net of those. Click any line to
  open the same editor the grid opens — notes, split months, revert and the
  balance reconciliation all included. **A row with nothing recorded in that
  month drops off the list**, whatever the reason it's empty — a quarterly bill
  in a month it doesn't fall in, a row you've marked as
  [stopped](#a-row-that-stopped), or one that simply had nothing in it. A line
  at the foot of the section says how many went and offers them back, and the
  choice sticks: press it once and every month keeps showing them until you
  press it again, which is how you fill a month in without tapping row by row.
  Two things stay: **anything with something in it** — a figure, a note, or the
  amounts a split month is made of, a stated $0.00 included, since that's a
  claim you made — and **a bill this month says is due** that you haven't
  recorded yet, because an empty row is the whole point of a reminder. That
  last is the one blank row you'll see, and its line reads "due the 20th" or
  "autopay, the 1st" rather than "nothing recorded", so it says why it's there.
  A month you haven't started keeps all its rows — if nothing anywhere in it has
  anything in it, that list is the thing you came for. Once the month has
  begun, a whole section can collapse to its heading, its total and the show
  line: $0.00 moved is worth printing, three rows saying "nothing recorded"
  under it are not.
- **Anything due**, when there is anything: a card of the hand-paid bills that
  are close or already late, and of any you are still waiting on. On the month
  you're actually in it also gathers **anything still unpaid from earlier
  months** — each line named for the month the money should have left, so
  opening it records the payment there. Only the current month does that: a bill
  nobody paid belongs on the page you open, not on one you'd have to go looking
  for. It isn't there at all in a month with nothing to say.
- **The accounts**, each with what it held at the end of the month, how far that
  moved, and what it earned. **＋ Add Account** sits at the foot of that card.
- **The month's notes**, gathered at the foot of the page the way a year's are
  gathered at the foot of the grid — everything you wrote on that month, on its
  figures, on the amounts a split month is made of, and on the balances you
  stated. Click one to open the cell it came from. A **row's own note** carries
  no month, so it stays on the year's list rather than being repeated under all
  twelve. A month you wrote nothing on draws no card at all.
- **A bar per month of the year**, so the month you are reading has somewhere to
  sit. Above the zero line — which is drawn heavier than the rest of the grid,
  since it is the line that means something here — a month added to your money
  and the bar is green; below it the month cost you some and the bar is red.
  Months still to come are outlined with a dash, the month you are reading is
  the one filled solid, and clicking any bar opens that month and takes you back
  to the top of the page to see it.

Every figure and every heading on the page carries its own **i**, and each opens
a window about that one thing rather than about the page.

**You can act on the month from here, not only read it** — which matters because
this is the phone lens. The actions sit where the thing they act on is, rather
than in a strip of buttons at the top:

- **＋ Add an Income Row / an Expense Row / a Transfer Row** at the foot of each
  section, and the editor opens on that section already — you added from
  Expenses, so it doesn't ask again.
- **＋ Add Account** at the foot of the Accounts card.
- **✓ Mark ⟨month⟩ entered** on the month's own status line, right after the
  sentence that says the month is still to come. Once it is entered that
  sentence changes and the button becomes **↩ Re-open ⟨month⟩** in the same
  place, so the way back is where the way forward was.

Each of those two appears on **exactly the month it acts on** and nowhere else:
months are entered in order, so the next un-entered one offers "Mark entered",
the last entered one offers "Re-open", and a month further ahead offers neither
— October cannot be entered before September. The rest of the grid's buttons
stay on the grid, because they act on the whole year: freezing it, building the
next one, the CSV, and deleting it are not things to be offered while you are
reading one month.

Nothing is worked out twice — every figure on the month page comes out of the
same engine the grid draws from, so the two lenses cannot disagree about a
month.

**No transfer counts against what was left over**, wherever you moved the money
to. Expenses means gone and transfers means moved, and filing a row under one or
the other is how you say which — so paying into your own retirement account is
not a loss just because that account is kept on a different tab. The Moved tile
shows exactly what the Transfers card totals, sign and all, and its own line
says how much of that stayed inside accounts the budget tracks: that part leaves
your closing total untouched, and the rest is why the closing total can fall in
a month you came out ahead. The other side of the rule: a transfer to something
that genuinely **stops being yours** belongs under Expenses, which is what that
section is for.

Picking a month moves the Year lens to that month's year, and opening the Month
lens over a year you are not already inside lands you in it — so switching
lenses shows you the same place differently rather than losing it.

A year kept as a **yearly summary** has no months in it, so the Month lens sends
you back to Year for those.

### How a Row Projects Itself

Each row has a **type** (which section it lives in), a **projection rule**,
and a **behaviour** — ordinary money, a transfer with another account, or a
pass-through that never touches the main account.

The rules: repeat last month · repeat rising a set % a year · cycle · average
so far · average of last year · same month last year · interest · per-check ×
paychecks · overflow sweep.

**A number you type into a month always beats the rule**, and moves the same
way.

**Both averages say which months they're over**, because neither is quite what
its name suggests. *Average of the months so far* falls back to **last year's**
average while this year has no months of its own — which is every month of a
year you've built ahead. *Average of last year* counts only the months actually
recorded in it, so on a plan entered through August it's an average of eight
months, not twelve. Hover a row's name to see which.

**Same month last year rounds to the nearest whole dollar** — the spreadsheet
wrapped that lookback in `ROUND()`, and on a bill nobody is pretending to know
to the penny it reads as what it is: an estimate. It is the only rule that
rounds, so on a row where the cents *are* the figure it reads instead as a
number that is 28 cents wrong. Tick **Keep the cents** in the row's settings and
that row copies last year's figure exactly; every other same-month row goes on
rounding. Either way the row's tooltip says which one it is doing. A half-dollar
rounds **away from zero on both sides** — a −$100.50 bill to −$101, the same way
a $100.50 refund goes to $101 — rather than the browser's own tie-break, which
sent the two in opposite directions and always gave the expense the smaller
figure.

**A rising row** is "repeat the last month" with a clock on it: the figure
steps up by the percentage you give it once each **calendar year**, never
monthly — a renewal letter, not compound interest. Inside a year it simply
repeats, so typing the real new rent when it lands takes over exactly as it
does everywhere else, and the row grows from *that* from then on. No percentage
typed means no rise; it repeats rather than inventing a figure.

### Due Dates

Most expenses have a day attached, and plenty of them only fall in some months.
A row can say so, and once it has, the Month page can remind you about it and
get out of your way in the months it isn't due.

Open a row and tick **It has a due date**:

- **How it gets paid** — by hand, or on autopay. **Only a hand-paid bill is ever
  warned about.** An autopay one just says when it goes out; that's a note about
  your arrangement, and the app has no way to check that the payment actually
  went through.
- **Day of the month** — leave it empty when the day moves about, and the row
  simply says it's due this month rather than counting down to a date you never
  gave it. **31 means the last day**, whatever the month is, so a February bill
  lands on the 28th rather than on a date that doesn't exist.
- **Months it falls in** — Jan, Apr, Jul and Oct for a quarterly water bill; two
  boxes for taxes twice a year; one for an annual renewal. Tick them all (or
  none) for a monthly bill.

**Ticking the months also tells the projection rule where it may go.** A *repeat
the last month* row only fills the months you ticked, so it's safe on a bill
that isn't monthly; and a **cycle keeps the beat you stated** rather than
counting from the last month you happened to type something into — which used to
mean one bill paid late moved every future estimate along with it. A figure you
type is never affected: it wins wherever you put it.

That's the one place a due date touches a computed figure. A row with no ticked
months behaves exactly as it always has.

All of that is behind the **ⓘ** beside *It has a due date* in the row editor.
What the app then *does* with a due date — the warnings, and what the Month page
gathers up — is behind the one on the **Due and Waiting** card, where you are
reading the result rather than setting it up. Each points at the other.

**A warning starts a set number of days before the date** — seven unless you
change it in [Preferences](#preferences) — and appears as a small pill on the
row and in a **Due and Waiting** card at the top of the month. It stops the
moment the month's figure is recorded as *something that happened* rather than
an estimate, which is also what marking the whole month as entered does to every
row at once. There is no separate "paid" tick, because an actual figure already
means exactly that.

**Nothing here is ever a colour on its own.** The pill carries a mark and words —
*Due in 3 days*, *Due today*, *12 days late* — and the colour only agrees with
them.

#### When the Money Actually Leaves

A bill due on the 3rd is one you settle a week earlier — which is in the
**previous month**. Nothing in the figures can tell that apart from paying on the
day: either way it's one payment a month. So the row has to say, and **The money
leaves** is where you say it.

Pick *the month before* and the whole row shifts: the reminder lands on the page
you're actually on, the estimate goes in the month the money really leaves, a
figure recorded there counts as having paid it, and the row can drop off the
months in between. Without it, somebody who always pays early reads as **late
every single month, for ever** — which is the fastest way to teach yourself to
ignore a warning.

The warning still counts down to the *due* date, so "a week before the 3rd"
starts on the 27th of the month before.

#### Bills Due at the Start of a Month

A bill due on the 1st is one you pay **in the month before it**, so the card
looks into the beginning of next month as well as the month you're reading.
Standing on 25 August with a week's warning set, the August page tells you the
1 September insurance is due in seven days — which is the point at which you can
still do something about it.

A line about next month says so, shows *next month's* figure, and opening it
records the payment there, where the money will actually go. Only a deadline
still to come reaches back like that: one that's already late belongs on its own
month's page, which is a click away.

#### Rows That Aren't Due This Month

A row whose schedule excludes the month you're reading **drops off the list**,
with a quiet line at the foot of the section saying how many went and offering
them back. Your choice sticks until you change it.

It only ever drops a row that has **genuinely nothing recorded**. A figure, a
note, or split amounts all keep it on the page, whatever the schedule says — so
a bill that turned up in a month you weren't expecting it never disappears, and
the rows you can see always add up to the total underneath them.

That also means a row set to **repeat the last month** mostly won't drop off: it
fills every month with an estimate, and an estimate is something recorded. The
rows this shortens a month by are the ones that are actually blank in between.

#### A Bill That Hasn't Arrived

The awkward case, and the one this was built around: a quarterly bill the town
hasn't managed to send for three quarters. The money is genuinely owed and
genuinely **not late**, so shouting "overdue" at it is wrong — and quietly
forgetting about it is wrong too.

**Pause reminders until** is the answer. The warnings stop, and the app keeps
counting: the Due and Waiting card names the row, says how many periods have
gone by unpaid, and gives a figure for what they come to. Where a period was
never billed at all it uses **what the bill last came to** and says so, rather
than presenting an estimate as a total. If nothing has ever been recorded for
that row there's no figure to judge it by, and it says that instead of showing
$0.00.

Marking a month as entered **leaves a paused row blank** rather than stamping its
estimate as paid — it tells you how many rows it left alone — because that's the
whole point of having said you're still waiting.

### A Row That Stopped

Some rows are only true for part of the plan. You change credit cards and stop
redeeming cash back; a subscription ends; a bill you paid for eight months goes
away. Left alone such a row keeps estimating itself forward, sits on every Month
page with nothing to say, and gets copied into next year for you to delete by
hand.

Open the row and set **Stopped using it** to the last month it had money in it
— the same field, and the same words, an account uses when you close it. From
the month after:

- **it estimates nothing.** A "repeat the last month" row stops repeating rather
  than carrying its final figure across the rest of the year.
- **it drops off the Month page** — not because it stopped, but because it's
  now empty, which is [what that page hides](#year-or-month). It's still there
  behind the **show** line at the foot of the section, and it says when it
  stopped.
- **it is never reminded about again**, and stops counting up unpaid periods.
- **it is left out when you build next year**, and it is taken out of any year
  you have already built ahead — unless that year holds the month it stopped in,
  or holds a figure you typed there, in which case it stays.

**A figure you type into a later month still stands.** A charge that turned up
after you thought you were done is a fact, and it keeps the row on that month's
page. Nothing in the year you were using it moves, either: the row and every
dollar it recorded stay exactly where they happened, and the grid's row label
says "stopped Apr 2026" so a row whose figures end halfway across doesn't read
as an oversight. Clear the field and the row is simply in use again.

### Overflow Sweeps and Caps

An **overflow sweep row** watches one account and moves whatever it would end
the month holding above a threshold into another account. The threshold is
either a **goal's target, read live** — edit the goal and every future month
moves with it — or a plain dollar amount.

- A goal that adds up **several accounts is measured across all of them**. An
  emergency fund living in cash plus two checking accounts is over its target
  when those balances together are. The transfer still leaves the one watched
  account, which must be among the ones the goal counts.
- It is worked out **at the end of the month, after the accounts' interest**,
  so the measured pot lands exactly on the threshold. A month that ends under
  it stays blank — nothing to sweep is not a $0 transfer.
- A row can also **cap its destination**: fill it only up to a goal's target,
  or an amount. This is how several rows sweep from one account the way real
  transfers are made — the first row fills mid-term until it reaches its
  goal, and the row below it takes whatever overflow is left to long-term,
  worked out in row order. (A cap goal spanning several accounts is full when
  they together reach its target, and it must count the account the row
  fills.)
- An account that dips under its cap **refills before anything flows past
  it**, and a full one keeps its own interest — a cap stops money going in,
  it never sweeps money out.
- Rows can **chain**: one row watching the account another fills, resolved in
  dependency order within the same month. Two rows sweeping into each other's
  accounts is a loop with no answer, so both stay blank and the cell editor
  says which row to repoint.

### Accounts

**Accounts are a list you own** — add as many as you like, each with its own
name, growth rate, and a choice of which account that interest is paid into.
Open one by clicking its name at the left of the grid, or with **⚙ Account
settings** in any of its balance cells — the same button "⚙ Row settings" is
on a budget row.

- **They start where your data starts.** An account is tracked from the first
  month you put a figure in; earlier months stay blank rather than zero, and
  typing into one of them moves the start back.
- **One account is the main account** — everything ordinary lands there, and
  transfers and pass-throughs are both described against it. Open an account
  to nominate a different one if your banking moves; only one can hold it, so
  ticking the box moves it.
- **Each account says what its rate produces** — interest, or growth. Interest
  is money the account earned and counts as income. Growth is an investment
  rising on paper: it moves the balance and counts as income nowhere, because
  you cannot spend it until you sell. Both compound the same way; the setting
  only decides whether the figure is treated as pay. Every account starts on
  interest, so nothing changes until you say otherwise.
- **Interest starts where it grows.** A new account pays its interest into
  itself, which is what an account holding money does; its dividends default to
  the main account instead, since a brokerage usually sweeps those somewhere
  spendable. Both are a dropdown, and either can be pointed anywhere.
  **Growth has nowhere to go** and the dropdown is replaced by a line saying
  so: moving a paper gain into an account you can spend from would be selling,
  and a percentage does not say you sold anything.
- **An account you stop using can be closed**, from the month it last held
  anything, so it drops out of Total instead of carrying its final balance
  forward for ever. If other accounts were paying their interest or dividends
  into it, those earnings stay in the account that made them from the closing
  month on — and closing it says so, because money that quietly changed where
  it compounds is exactly what a plan is read to catch.
- **Two accounts with exactly the same name are the same account** under
  different labels. Years of history imported under drifting names fold into
  one row, carrying every balance with them. It refuses if both hold a figure
  in the same month, since that would mean losing one.
- **Owner, if you've named a household.** Each account can say whose it is —
  see [Household](#household).

### Interest and Dividends

**Interest & Dividends** is a line of its own at the foot of Income: what
every account earned that month, added together, with the two halves named on
hover.

In the **live** year it is worked out from each account's rates rather than
typed, so you correct it on the account rather than in the grid. The Income
total counts it — it is money in, and money in vs money out and the savings
rate had always counted it while the grid itself showed it nowhere.

A **Dividends** row that earns on last month's balances reads December's from
the year before, so January is never blank in a year built ahead (until
2026-09-01 it was — the row only looked inside its own year, and a projected
year lost a twelfth of its dividend income).

In a **past year it is stated**, the way the balances there are. Nothing is
computed in a finished year — a rate an account carries today says nothing
about what it paid in 2021 — so click the month on the account's row and type
what it really earned. That figure counts as income for the year and leaves
the balance beside it alone, which already holds the money. You can state what
a month earned without stating what it held; hovering the blank cell reads it
back.

Marking a live year as history writes its earnings down at the same time as
its balances, so freezing a year never costs it the interest it made.

A year whose accounts earn nothing — or a past year you haven't typed any
figures into — shows no such row at all.

A row that earns interest **names the accounts it earns on**, and any income
row can be **marked as pay** so the giving percentages count it.

### Growth

An account set to **grow** rather than pay interest reports its growth **on the
account itself**, and nowhere else. Hover or tap a balance and it reads
"Growth $88.40 · not income" under the figure; the account's year-total column
gives the year's. There is no Growth row in either lens — growth is a flow, and
a flow among the account balances reads as an account, which is what it is not.

It is in none of the figures that count income: not Interest & Dividends, not
Money In, not the savings rate. So once an account is set to grow, those
figures fall by however much of them was really appreciation — which is the
honest number, and the reason to set it.

The consequence worth knowing is that **Money In less Money Out no longer
explains the change in your closing total**, and it should not: the balances
climbed by more than any money that arrived. The difference is on the account
that grew, which is the account whose balance moved.

**Stating a balance does not restate that month's growth.** The month you pin
keeps the figure the rate implied; every month after it chains from your number,
so their growth follows.

But the app will **offer** you the figure. Type a balance that differs from the
one the plan expected and a button appears saying what the month must have done
for that balance to be right — **"Say This Month Grew $1,279.42"**, or *Fell*
where the market went the other way. It is exact rather than a guess: every
other figure in the month is already accounted for, so the difference has one
candidate left. Take it and the reconciliation line changes to *"Matches the
plan exactly"*, because you have just explained the whole gap.

It only ever offers. The app will not decide on its own that a difference was
the market — it might have been a payment you never recorded, and there is no
way to tell from here. So the button waits to be pressed, it never fills a
Growth box you have already written in, and it appears only on an account set
to grow, where the residual really does have one candidate. On a savings or
current account the reconciliation line still just states the gap and stops.

A past year states its growth the same way it states its interest — click the
month on the account's row — and freezing a live year writes it down with the
balances. Converting a year to a **summary** is the one place it is not
carried across: a summary holds flows and balances, and growth is neither. No
money is lost (the balance rows already hold every dollar of it), only the
line saying how much of the year's climb was appreciation, and the confirm
says so before it happens.

### Reading a Year

The current year is live. Months you've entered are actuals; everything after
them is an estimate that recomputes the way the spreadsheet's formulas did —
**the account balances included** — so the current month reads as the estimate
it is until you mark it entered, rather than looking like money already
counted.

**Every figure says what it's made of**, subtotals and year totals too:

| Style | Meaning |
| --- | --- |
| Plain | What happened |
| *Italic* | A projection |
| Dashed | A total spanning both |

The year-total column adds a row's months up — **except an account, where it
shows the balance the year closed on**, since twelve monthly balances added
together would be the same money counted twelve times. Hovering one gives
that year's interest and dividends, which is what the account actually made
you; the CSV export carries the same figure.

### Editing a Month

Click any cell to edit it. Beyond typing a figure:

- **Split a month into several amounts**, each actual or estimated on its own,
  totalled on save. A row paid per check opens that way already — one line per
  payday with the amount filled in — so correcting a single cheque (a bonus, a
  missed shift) is one box to type in rather than a lump sum to break apart
  first. Hovering a split month reads its amounts one per line with the total
  labelled last, in the grid's own tooltip, which follows the pointer so it
  never goes missing after a scroll or an edit. **On a phone**, where there is
  no pointer to follow, tapping a line that opens nothing — a subtotal, a total,
  the interest line — puts the same tooltip up above it and leaves it there
  until you tap somewhere else. A line that opens an editor doesn't show one:
  the editor it opens says all of it. Nothing in the app explains itself by hover
  alone — where a column or a figure has something to say, it says it through the
  info dot beside it, the tooltip, or in words on the page.
- **A balance cell reconciles as you type.** Say what an account really holds
  and it tells you how far that is from what the plan expected, or confirms
  the two agree.
- **Hovering a balance explains it.** What the account earned that month — its
  interest, its dividend, and the account either was paid into when that isn't
  itself — which is what explains a balance moving with no budget row behind
  it. It reads from **both ends**: the account that earned the money names
  where it went, and the account it landed in names who sent it ("Paid in
  $102.01 from Brokerage", one line per account that swept something in), so a
  hub balance jumping is answerable from the cell you're already looking at. A
  month that earned and received nothing stays quiet rather than printing
  $0.00, and a figure you typed over the computed one says so.
- **The cell editor says the same in words** — the rate, what it earned, and
  what the other accounts paid in this month — and lets you override the
  interest or add a dividend. Correct either and the balance recomputes around
  it, in whichever account the money is paid into, for that month and every
  month after. In a **past year** the same two boxes state the earnings
  outright: there is no rate to quote and no balance to recompute, so the
  editor says so, and "Clear this cell" empties the month's balance and its
  earnings together. Nothing is routed to another account there — where
  interest lands is today's arrangement, not 2021's.
- **"✓ Accept the Estimates" agrees with the plan in one press.** Every figure
  in a balance month is greyed, because typing is what states one — so saying
  "yes, that is what the account held" meant copying three numbers back into the
  boxes that were already showing them, where a mistyped digit looks exactly
  like a real correction. The button writes them in for you: the balance becomes
  a stated one, and the month holds it even when an earlier month changes. A box
  you have already typed in is left alone — it fills the blanks, it never
  overwrites a correction sitting in front of it — and a month that earned
  nothing states nothing, since a stated $0.00 is a claim of its own. "↺ Back to
  Auto Estimate" is the way back. The **paycheck count** offers the same button,
  for the same reason: it is a placeholder too.

### A Note With No Figure

Sometimes what you want to record about a month is that **nothing happened** —
the water bill never arrived, the refund never landed. Write the note and leave
the amount empty.

The month stays **blank**: nothing recorded, still unpaid, still counted as
outstanding, still warned about. The note shows as a dot on the grid, in the
month's notes, and in the cell's tooltip. It's the difference between "the bill
never came" and a **stated $0.00**, which is the opposite claim — the bill came
and it was nothing — and which does mark the month as settled.

A note on a **future** month rides alongside its estimate rather than replacing
it, so annotating next March doesn't empty it. And a note on a **past** blank
month is not a figure for later months to carry: a row that repeats its last
figure, grows it, averages it or bills on a cycle looks past the note to the
last real amount. (Until 2026-09-01 those four rules read a note-only month as
a real $0.00 — April's estimate went to nothing, the average dropped, the
quarterly bill re-phased onto the note month, and every balance after it moved.)

### Notes

**Every note you've written anywhere in a year is gathered into a box of its
own under the budget** — cells, split parts, balances and rows — each one
clickable to jump back to what it was about. The box isn't there at all in a
year you haven't annotated. Notes are grouped by month and laid out across the
width of the card, so a year's worth reads at a glance instead of running down
one long strip.

### Entered Months and Finished Years

Mark a month **entered** to freeze its estimates into numbers, like
overtyping formulas in Numbers. A figure you typed as an estimate is frozen
too — it becomes an actual like the rest, so a due-dated bill you estimated
by hand stops reading as late once its month is entered (until 2026-09-01 it
kept its estimate marking, read *late* for ever, and was counted among the
outstanding dues). A row marked as still waiting on its bill is left blank
either way.

Once every month of a year is entered you can **mark the whole year as
history**: the balances it computed become the balances it states, and nothing
you typed changes — the grid reads exactly the same the moment after as the
moment before. It also notes the year's end-of-year total, which is the figure
the year-by-year chart draws it at, and which you can correct with **✎
End-of-year figure**.

Nothing is lost either way. **↩ Re-open as live** puts the year back to a
computed one, including any balance you'd stated by hand.

A finished year can also be **converted to a yearly summary** — permanent; the
Progress charts carry on unchanged, each account keeps its end-of-year balance
as a balance row, and whatever the year stated it earned folds into one
"Interest & Dividends" row among the flows — or deleted outright. It holds its account balances
as figures you stated at the time rather than a chain to recompute, and an
account you've since closed stops at its last month instead of following you
into later years.

### Building Next Year

**"Build ⟨next year⟩"** duplicates the live grid the way Charlie used to
duplicate the sheet. Build it as early as you like to see where the plan is
heading.

A year that hasn't arrived shows nothing but projections, and they start from
the year before rather than a blank page:

- "repeat last month" rows open at December
- "average so far" rows at last year's average
- a cycle bill keeps its beat, so an annual renewal still lands in its own
  month
- the paycheck counts repeat last year's pattern — which keeps the year's
  total right if you're paid fortnightly, where assuming two a month would
  lose you a fortnight's pay

Each hands over as soon as you type a real month in.

**Every paycheck count says where it came from.** Hover one and it tells you
whether it's a figure you entered, one taken from the same month a year ago, or
— where there's nothing to go on anywhere — **two a month assumed**, which it
names outright and invites you to correct. An assumption inherited from last
year still reads as an assumption, however many years along, rather than being
laundered into "from last year".

**It keeps tracking the current year as that changes — rows included.** Add a
row to this year, retire one, rename it, change its rule or move it, and next
year is changed to match, so a year you built in advance never quietly
describes a budget you no longer have. Anything you set up in next year alone
is left alone.

**A row you have marked as [stopped](#a-row-that-stopped) doesn't come with
you** — not into a year you build now, and not into one you built earlier,
unless that year holds the month it stopped in or a figure you typed in it.

And it doesn't become the current year — Progress and the rest carry on
reading this one — until 1 January, or until you mark December entered.

---

## Progress

Where the whole plan stands and where it has been, on one tab.

### Savings Goals

Goals add up whichever accounts you tick, so splitting an account is a matter
of ticking the new ones. Each goal counts its accounts up to the target, in
full, or only what another goal hasn't already claimed.

Plus progress, target dates, required monthly saving, and a pace check that
follows whichever goal is next — the soonest deadline you haven't met yet.

**Where the Total Is Heading** goes **dashed the moment it passes the month
you've entered through**, so a month the plan has merely worked out never
reads as one that happened, whether it's next month or a year you've built
ahead.

### Net Worth

A **net worth strip** under the goals adds up everything the plan knows about:
the liquid total, the Investments tab's holdings, the retirement
accounts, the Household tab's property at your stated values, and everything
you owe. The giving fund is deliberately left out — that money is
already given — and a part with nothing recorded shows no tile rather than a
$0.00.

**Which month it is read at is yours to choose**, once the two answers differ.
The month in progress is not settled — every figure in it is the plan's own
estimate until you mark it entered — so Liquid and Total are drawn in *italics*
there, the same mark the grid puts on a figure it worked out. An **As of**
switch offers the **last month you marked entered** instead, whose balances are
what the accounts really ended that month holding. Where the current month is
itself entered there is one answer and no switch.

What you hold and what you own are **today's figures either way**: a holding is
worth its price now, a property what you last said it would fetch, and neither
has a month. So an end-of-August net worth is August's balances beside today's
prices — right the morning after you settle a month and refresh your quotes, and
less so the further back you look. That is why there is no picker over every
month in the plan.

Debt appears in one of two places and comes off the total either way. A debt
**secured on a property** is inside that property's figure, which is the
property's equity; everything else — cards, student loans, a personal loan —
is the **Owed** tile. Nothing is ever counted twice, and the total is the same
number whichever side of the line a debt sits.

If something is held in a currency you have given no rate for, the card says
so and leaves it out, rather than adding it in at face value.

Money that honestly lives in two places is **counted once**: a brokerage
tracked as a budget account *and* as an Investments pane is reconciled by the
pane's ✎ Edit dialog, which lets it name the budget account(s) its holdings
are. The total then subtracts that overlap, keeping the pot at what the
holdings are worth.

**Record** turns the strip into history. Each press states the card's exact
figures as a dated snapshot — a deliberate act, like pinning a balance; the app
never records one on its own — and two or more draw the net-worth-over-time
line, with the parts in the hover.

- **It records whatever you are reading**, and its label says which: today's
  figures on the month in progress, or "Record Aug 2026's Figures" on a settled
  one. A settled month is dated its **last day** — the end of August is recorded
  as the 31st, where it belongs on the line, not as the day you pressed the
  button.
- The table under it lists each snapshot's parts beside its total, in the same
  order as the tiles above; a part a snapshot never stated shows a dash rather
  than a $0.00.
- A second press for the same day restates rather than duplicating.
- Old statements can be typed in by hand to backfill the line.
- Every snapshot is clickable to correct or delete, **Owed included**.

### Savings Rate and Runway

The year's totals in the units the questions are actually asked in:

- **Savings rate** — income minus expenses, over income. Money moved between
  your own accounts never counts as spending, and income is the Budget tab's
  own Income total (the income rows plus what the accounts earned).
- **Runway** — liquid savings against a month of expenses.

Both move as real months land.

### The Long-Run Charts

- **Total liquidity, 2011→now.**
- **Money in vs out, every year** — with the interest your accounts earned
  counted as money in, so the two charts tell the same story. These bars count
  every movement, so a year that swept $16,000 into savings and took $11,000
  back out counts both, which is why "money in" can read well above anything
  you'd call income. A switch on the card, **"Leave out transfers between your
  own accounts"**, takes them off; it's remembered and follows you to the
  phone like the folded boxes do. A row only counts as a transfer if you've
  filed it under Transfers *and* its other side is an account tracked here —
  so a payment you've called an expense still counts as money out however it's
  routed (giving through a fund, a Zelle out of a tracked balance), and a Roth
  IRA contribution filed under Transfers counts too, because that account
  isn't tracked and the money really left.
- **What you actually spent each year** — the expense rows alone, so money
  swept into savings or moved between your own accounts doesn't read as a
  heavy year. Each bar is the year's Expenses total from the Budget tab, with
  a dotted line across the years already recorded to say what's usual, and a
  hover giving the change on the year before.

The oldest years come from bi-weekly sheets whose rows the importer couldn't
tell apart. They're sorted out on load, and any row it reads wrong is one
click to fix. Those years have no Income / Expenses / Transfers split to read,
so their spending bar counts everything the old sheets recorded going out —
and the years imported from the old spreadsheet never recorded which rows were
transfers, so their bars are the same either way. A line under each chart says
so rather than letting them look comparable.

*(These charts lived on a tab called History until August 2026; a tab order
saved before then just drops the dead entry.)*

### Where the Money Goes

The charts above say what a year cost. This says what it was **spent on** —
every expense row in the live year, biggest first, with its share of the year
and what the same row came to last year beside it.

The **change** column is the point. A share of spending on its own only tells
you which row is biggest, and you already know which row is biggest.

- Rows are matched to last year **by the row**, so renaming one keeps its
  history in a single line instead of splitting it in two. Against an old
  yearly summary, which has no rows to point at, they are matched by name.
- **A row that has vanished since last year still gets a line.** Money that
  stopped being spent is as much a finding as money that started.
- **A row that hands back more than it takes is negative** — cash back, a
  parking benefit — and its change is said in those terms: "$961.71 less back"
  means less came back than last year, never "up $961.71", which is a true
  sentence about the year and a false one about the row. The caret always
  points the way the *year* went, because the column has to explain the total
  under it, so less money back points up. A row that crosses zero between the
  two years says which side it was on instead of a percentage.
- Anything that spent nothing in either year is left out — a screenful of
  $0.00 is how a table stops being read.
- The current year includes the months the plan has worked out, so August
  never looks like a cheap year, and those figures are set in the estimate
  style to say so.
- A year with no breakdown to compare against says that in words rather than
  calling every row new.

Counted exactly as the bars above are, so the parts always add to the total.
One colour for every bar with the names on the axis: a key of forty colours is
unreadable for anyone.

---

## Vacations

The year-by-year chart opens the tab and the trips follow it. The trips are
still what the tab is *for* — but they read newest-first, and the newest year is
usually trips that are still only titles, so the page used to open on a row of
boxes with no figures in them. The chart is the only card here that says how
this year compares with the last few, and it gives the tab something to open on.

- **Trip Spending, Year by Year** — under the add bar, once two years have
  trips (the sample plan has two, one settled and one still forming, so the demo opens on it). Each bar adds a year's trips up (paid, minus credits, plus still due),
  with the trips themselves broken out in the hover, a dotted average across
  the finished years, and a dashed edge on a year whose figure can still grow — the current
  year and anything after it, and any past year with money still due, since a December trip
  whose last bill lands in January is not finished whatever the calendar says.
- **Per-trip cost tables**, grouped into one row per year, newest first, and
  reorderable within a year. A new trip starts from the lines most trips need
  — airfare, stay, transport, excursions, food, tips, spa — or from nothing,
  your choice.
- **Each line tracks what's paid, what's credited and what's still due**, with
  a **✓ Paid** button that settles the rest in one click.
- **A holidays & PTO planner**, with from/to dates, under the trips it counts.

---

## Giving

The donations log, each one filed under the year of its date. Date one in any
year, past or future, and that year gets its own table — which appears when it
has something in it and goes when it doesn't.

Each donation carries the **event** it was given through (a walk, a ride, an
appeal) beside the foundation receiving it, and is either done or
**planned**. A planned one reads in italics, stays out of the year's totals,
and is counted up separately as what's still to go.

Under the year tables sits a **donor-advised fund's holdings**, for those who
have one — a Preferences switch, since plenty of people don't. Donations are
tracked either way, and the giving-over-time chart is last.

### Giving as a Share of Income

Every year shows what its giving came to as a share of **gross comp** and of
**take-home pay**, on meters drawn against one shared scale, so the years
compare with each other at a glance. Once a second year has something in it, a
chart appears above them: dollars given as bars, both percentages as lines
over the top.

"Given" counts what left your own accounts — fund deposits and cash gifts. A
grant out of the fund isn't counted twice.

**The take-home tile names the rows it divided by**, because take-home isn't
every income row — it's the ones that are pay. A row counts if it's on the
per-check rule, if you've ticked **This is my pay** in its settings, or, failing
both, if it's *named* like pay ("Salary", "Wages", "Paycheck" — the fallback
that lets an old summary year, whose rows carry no rule at all, still work). So
the tile lists what it counted, and where a row got in on its name alone it says
so and points at the tick that overrides it in either direction.

### Where a Year Is Heading

A year still running that has giving **planned** in it also shows a second row
of tiles under the first, saying the same three things about the year's
projected total: the planned fund deposits and cash gifts added to what's
already gone, and the share that comes to of each kind of income.

The columns line up, so a projection reads straight down from the figure it
projects, and it's marked as an estimate the way everything else in the app is
— italic figures, a dashed meter rail, never a colour. On the chart, that
year's bar is filled and outlined solid to what's been given, and a dashed box
carries on above it to the projected total; the gap between them is the giving
still to come.

It's the missing half of the fraction: take-home pay is already read from the
whole year, projected months included, so measuring eight months of giving
against twelve months of pay read low all year and jumped in December.

A planned *grant* is left out of the projection the same way a made one is —
that money left your account when its deposit did — so the projection can be
smaller than the "more is planned" figure above the table, which counts every
planned row.

### Cloning and Clearing a Year

Each year can be **cloned forward** as next year's plan. The button names the
year it writes into — the first one with nothing in it yet — and every copy
lands **Planned**, dates moved to the new year and their day kept, so an
appeal you give every February stays in February. Nothing you've actually
given can be changed by it, and the year you cloned from is untouched.

A whole year's donations can also be **deleted at once**, card and all; undo
in the header brings them back.

---

## Investments

One pane per place you hold investments — add, rename and reorder them.

### Prices

**Automatic price lookups** are optional (Twelve Data; free key kept on the
device, cached six hours, and every price still editable by hand).

- Shares, ETFs and **mutual funds** are all quoted. A fund strikes one price a
  day after the close, so its figure is the last published NAV rather than a
  live one.
- The free tier allows **800 lookups a day and eight a minute**. Once the
  supplier says it has no price for a holding, that answer is remembered for
  the day rather than spending the allowance on the same question at every
  visit.
- Prices top themselves up automatically when they are more than six hours
  old; **Refresh prices** ignores that and fetches everything on the spot.
- **The six-hour cache syncs**, so a price fetched on the laptop is still
  fresh on the phone rather than being fetched again out of the same daily
  allowance. The key itself stays on each device — which is why you enter it
  once per device but only ever pay for a lookup once.
- **The key box is a password box**: masked, with a **Show** button so you can
  check what you typed. It is masked because it is a credential, and because
  that is what makes your browser's password manager offer to remember it —
  which is how the key reaches your other devices, since the app deliberately
  never carries it there itself. Saved that way it is synced end to end
  encrypted by the password manager, not by this app.
- Open a holding and its **Price box says where that number came from**:
  fetched and when, typed over a fetched one, or never looked up. (The line
  above the tables can only report the oldest fetch across the whole table.)
  The box also shows what the holding is worth and how much of the account it
  is, both keeping up as you type.

### Cost and Gain

A holding can carry its **cost basis** — what you paid, off your statement —
and the tables then show cost and gain, in dollars and percent, per holding
and per pot. Holdings without a basis are honestly left out of the footer's
sum. The same field works on the Retirement tab's holdings, since every
holdings table is one renderer.

### Everything You Hold

A card that rolls every pot still yours — the panes here plus the retirement
accounts — into one by-ticker table, with each holding's share of the whole,
so concentration across pots is finally one number. The giving fund stays out
(that money is already given). A shared Investments link carries the
retirement accounts and your allocation targets, and says so.

- **Targets per ticker** — click a rollup row to set the share it should be. A
  Drift column then shows how far each targeted ticker has wandered, in points
  and in the dollars that would bring it back. Targets don't have to cover
  every row or sum to 100%. **A holding with no price reads "no prices"** in
  that column, and in the Furthest From Target chart's text — a drift is measured
  from what the holding is worth, and without a price the app does not know that
  (until 2026-09-04 it said "on target", a zero measured against nothing).
- **Asset classes in your own words** ("S&P 500", "Bonds") — the app
  deliberately ships no fund taxonomy, the same principle as the tax tables. A
  **By Class** table folds the rollup into those labels, so three funds
  tracking one index read as the single bet they are; anything unlabelled
  gathers honestly under "Not classed yet".
- **Targets per class** — click a class row. This is usually where a
  rebalancing rule actually lives: "90% US stocks" is one target at the class
  level, where saying it per ticker would measure each fund alone against the
  whole.

### The Two Charts

Both sit at the bottom of the tab, after the tables they read from, side by
side on a desktop window and stacked on a narrow one, and each fills the window
on its own with the ⤢ button.

- **Where It's Held** — one bar per ticker, biggest first, cut into bands by
  the account it sits in. The rollup table names the accounts a ticker turns up
  in and has never said how much is in each, so VOO in a brokerage and VOO in a
  401(k) read there as a single number; this is where they come apart. Bands run
  in the same order along every bar, and the palette holds five accounts apart —
  past that the smallest are gathered into one band rather than a sixth colour
  nobody could tell from the fifth.
- **Furthest From Target** — the Drift column put in order: every ticker you
  have set a target for, ranked by the size of the trade that would close the
  gap. Right of the line is money to take out, left of it money to put in, so
  which way a holding has wandered is a position on the chart rather than a
  colour. Once you have set class targets too, a switch ranks by **asset class**
  instead — usually the layer a rebalancing rule actually lives at.

Both appear only once they have something to say: two tickers and two accounts
for the first, two targets for the second. A single bar is a table row wearing a
bigger heading.

### Reconciling Against the Budget

A pane that names budget accounts also reconciles against them: its subtitle
shows the budget's figure for the same pot and how far behind or ahead of the
holdings it is, or that the two are in step.

---

## Retirement

### The Accounts

Retirement accounts each have a type (401(k), Roth IRA, HSA…), an owner, and
their own contribution history — so nothing about Roth IRAs is
special-cased. Contributions are rows you click to edit, one per year and
account.

- **A growth rate per account** (leave it empty to follow Preferences), so a
  bond-heavy rollover and an all-equity Roth don't have to compound alike.
- **The contribution types inside an account** — a real 401(k) holds a
  rollover, a Roth deferral, an employer match and a pre-tax deferral at once,
  each taxed differently, so one account carries them all rather than being
  faked as several. A **Combine** button folds accounts you split that way
  back into one, keeping every balance and treatment, and refuses outright
  rather than half-doing it.
- **Holdings inside each account** — the same ticker/shares/price rows an
  investment pane takes, priced by the same lookup. Once an account lists
  them, its balance follows the holdings instead of a figure you typed.

### The Split, and the Calculators

- **Traditional vs Roth**, with a per-person breakdown once there are two of
  you.
- **A 401(k) limit calculator per earner** — that limit is per person.
- **A Roth IRA income (MAGI) calculator** that counts both incomes when you
  file jointly.
- Both recompute as you change the figures. The thresholds stay figures **you**
  type: they move every year and differ by filing status, and the app ships
  none of them.
- **"Traditional vs Roth at Retirement"** — the same split as the bar at the
  top of the tab, but worked out for the month the pot starts paying, since
  that is the date the mix decides how much of your spending is taxable.
- **"Where the IRAs Land"** — each IRA's balance now, what is still to go in,
  and what it is worth by the month the paying-in stops.

### The Projection

Where the balances are heading, counting **both** the IRA contribution rows
you type and the **401(k) cards' own percentages**, carried forward in today's
money until each of you retires and pro-rated across the year you go. A year
you have typed always wins, in both directions, so a year you deliberately
skipped stays skipped.

- **A dotted rule marks each person's retirement year**, worked out from the
  birth month and retirement age on the [Household](#household) tab — and only
  for somebody who has both, since the alternative is a date you never gave.
- **An optional worse and better return** draws the same plan three ways with
  the range shaded, and says in a line what each does to the year the money
  runs out. Three assumptions you typed, deliberately **not** a range of
  likelihoods, since the app has no distribution behind them.

### The Drawdown

**Past the first of those retirements the line bends and the pot pays out.**

You set what the household spends a year, and the pot covers whatever **other
retirement income** — Social Security, a pension, a partner still working —
doesn't.

- Retire mid-year and that first year only spends the months left in it, so
  the figures on the card beside the chart describe the first **whole** year.
  A withdrawal rate read off a two-month year would be a sixth of the real
  one.
- The drawing years are drawn in a tighter dash, a solid rule marks the year
  the money runs out if it does, and a read-only table shows it year by year.
- The first withdrawal is shown as a share of the pot against a **rate you
  call safe** — 4% is only where the box starts, not a figure this app
  endorses.

**Everything on the tab is in today's money**, which is what makes the return
setting a *real* one (growth after inflation).

**Once you enter brackets on the [Tax](#tax) tab, the withdrawal is grossed up
to cover the tax on it** — a Tax column appears in the year-by-year table, a
fourth tile names what the year owes, and the withdrawal rate says it is
measured on the gross figure. Until then nothing on the tab moves by a cent.

It does not model required minimum distributions, and it says so rather than
pretending.

---

## Tax

The bracket tables **you** type, federal and state. They answer two questions:
what **this year** owes on what you are paid, and what a retirement withdrawal
has to be *before* tax in order to leave you what you planned to spend.

**The answers lead the tab and the tables sit under them** — the tables are a
year's typing you do once and then read back, the answers are what you come
back for. Until you have stored a table there are no answers to lead with, so
the order flips and the tables come first.

That gap was the biggest remaining dishonesty in the drawdown: a pre-tax
401(k) has to pay out more than you spend, and the projection used to draw
exactly what you spend.

- **Nothing ships with the app** — no bracket, no rate, no deduction, not even
  as a placeholder or a realistic-looking example. The app may work tax out;
  it deliberately does not know what the tax is, the same rule the
  contribution limits have always followed. **A year with no table means no
  tax.**
- **Type a table by hand or paste one in.** The paste box reads the layouts
  the published schedules actually use — rate-first, range-first, the
  over/but-not-over form, a bare two-column table, or a single flat rate — and
  tells you what it will store *as you type*. It copes with what a real
  clipboard does to a table: a wide table with a column per filing status
  (yours is picked out), markdown bullets, headings, citation links, and a
  copy that lost its line breaks and arrived as one run-on line.
- **It refuses whole rather than importing half** — bands that don't climb, a
  rate over 100%, a schedule whose top row is missing, two schedules pasted
  together, or a wide table with no column for your status — and it names the
  lines it ignored.
- **A table carries forward.** The newest one at or before a year is what that
  year uses, so one schedule covers a forty-year projection. The "Years You've
  Stored" card says which stretch of years is reading which table, rather than
  leaving you to infer it. Federal and state carry separately.
- **Each Other Retirement Income row carries its own taxable share**, with a
  separate state share once you have a state table. A row nobody has answered
  for is counted as 0% and **said so** — "untaxed" and "nobody has said" are
  different claims.
- **"What ⟨year⟩ Owes"** applies your tables to the whole package on the
  [Compensation](#compensation) tab — salary after the raise, the bonus, equity
  that vested, an employer contribution — and shows the federal and state
  figures, the effective rate and what the next dollar meets. The tab collected
  brackets for a year and used them only for a withdrawal forty years out; this
  is the nearest question, and the app had every part of it already.

  **It is brackets and your deduction, and nothing else** — no credits, no
  itemising, no payroll tax, and no notice of what has already been withheld.
  So it is what the schedule says on that income, never what you still owe in
  April, and the card says so in as many words. Nor is it a household figure
  where two people earn: the app records a second earner as take-home in the
  budget and never as gross, so there is no second package to add. It reads the
  newest year you have recorded comp for rather than the calendar year, because
  a raise letter arrives when it arrives.
- **A calculator** to check an income against your own tables, and a **"What
  the Pot Has to Pay"** card that works the first whole year of retirement
  through line by line. Those figures are read off the same records the
  Retirement chart is drawn from, so the two can never disagree.
- **Your spending target now means what you get to spend** — after tax. That
  is a change in what the figure means, and both tabs say so out loud.

It will not do required minimum distributions, a Roth-versus-traditional
withdrawal order, the Social Security provisional-income formula, itemising,
capital gains, NIIT or IRMAA. Each is a figure with a year attached that would
be quietly wrong within twelve months while looking authoritative.

---

## Household

Who the plan is for: a partner, your children.

**A new plan starts with one adult called "Me"** — a placeholder to type your own
name over, so the tab opens on a household of one rather than on an empty screen
asking you to declare that you exist. It has no birth month: every age,
retirement year and 18th birthday here is worked out from that field, so a
guessed one would print a wrong date as though the app had worked it out. Fill it
in and the rest follows. Restoring a backup never adds anyone — only a plan
created from nothing gets the default.

A new plan also starts with **two accounts, Cash and Savings, both in that person's
name** — the two the starter budget actually moves money through. Investments and
Other bank used to be there too and appeared nowhere else on a fresh plan, so they
read as two empty rows of furniture; **+ Add Account** is how you get them, or
anything else, back.

Each person has a role, an optional birth month and — for an adult — a
retirement age (halves allowed, for anyone waiting until exactly 59½),
**which month of that year it lands in** (their birthday, or the January
before or after it, since "retires at 55" is several different dates), and a
**plan-to age**: how far the retirement projection runs for them, a planning
horizon rather than a guess at a lifespan.

Their age, retirement year and the month a child turns 18 are all **worked out
rather than stored**, so none of it goes stale.

### What Naming People Unlocks

- **Every account can say whose it is** — theirs, yours, **Joint**, or not
  said — and the budget grid grows a subtotal per person just above Total.
  Every account lands in exactly one of those rows (the unassigned gather
  under "Unassigned"), so **the subtotals always add up to Total**.
- **Accounts can be added and edited right here** — the Who Owns What list is
  the same editor the budget grid's account rows open.
- **A savings goal can say which child it is for**, which files it under them
  here and suggests their 18th birthday as its target date — a starting point
  you type straight over.

Nothing on this tab changes a single figure the budget computes. Owner is a
way of reading the plan, not an input to it.

### Property

The household's **property** — a home, a car, a boat — at what you say it
would sell for, minus whatever is still owed on it.

Equity, not a balance: nothing flows through a house, so the budget engine
never sees these rows, and the [Progress](#progress) tab's net worth is where
the figure lands.

### What You Owe

Every debt the household carries, secured on something or not.

This used to be a single number typed onto a property row, retyped by hand or
left to rot while every other figure in the app kept itself true — and a loan
not attached to a house or a car had nowhere to live at all.

Give a debt a **balance, the month it was true, a rate and a payment** and the
app does the rest:

- **What is owed today**, worked out by paying the debt down month by month
  from the statement you quoted — interest first, the rest off the principal.
  That projected figure is the one net worth counts, so it stops going stale
  the moment you look away. It is set in the estimate style, and hovering says
  what you actually stated and when.
- **The month it ends**, and what the remaining payments cost in interest.
- **A debt secured on a property** comes off that property's equity; anything
  else stands on its own. Either way it comes off your net worth once.

It says what it is missing rather than filling it in. No payment typed means
nothing is projected — the balance stands exactly as you typed it. And if the
payment is smaller than the first month's interest the debt genuinely grows,
so the card says so in words instead of drawing a line climbing away: that is
a fact about the loan and it should not look like a fault in the app.

**Nothing here reaches the budget grid.** The payment leaving your account is
already a row there, and counting the debt as well would take the money out
twice.

*(A plan written before this arrives keeps its figures exactly: whatever was
owed on a property becomes a debt secured on it, and the net worth is
identical to the cent. No rate, payment or date is invented for it.)*

### Other Currencies

`Currency` in Preferences was only ever a label — it changed the symbol in
front of every figure and nothing else — so a household with a flat in one
country and a brokerage in another could not be written down at all.

A **property, a debt and an investment pane** can each say which currency they
are in, converted by a rate you state here.

- **You state the rate; the app never looks one up.** Same rule as the tax
  tables and the contribution limits, for the same reason: a rate fetched today
  is wrong tomorrow, and one baked into the app is wrong for ever while looking
  authoritative. Say when you read it and the card can tell you how old the
  answer is.
- **Each card reads in its own money** — the figure on the statement in front
  of you — and only the totals convert, saying which currency they are in.
- **Something with no rate yet is left out and named**, never counted at face
  value. A foreign flat added in at whatever number happens to be typed is the
  one answer worse than saying the total cannot be worked out yet.
- **The budget grid stays in one currency**, and always will. Its balances
  chain month to month through transfers and interest, so a rate you edited
  would silently rewrite years of history every time you touched it.
  Retirement accounts carry no currency either — a 401(k) is a creature of one
  country's tax code.

---

## Compensation

Where comp stands, and how it got there.

- **Raises over time** — the raise in dollars, and how the salary actually
  moved since last year, which differ whenever something lands mid-year.
- **A year takes the raise either way round**: type the percentage and the
  salary it comes to fills itself in, or type the new salary and the
  percentage does — whichever your letter happened to give you.
- **Bonuses by year** — one figure per year, editable from the comp year or
  from the bonus table, whichever you happen to have open. Shown both in
  dollars and as a percentage of **the salary that year opened on**, which is
  the pay it was earned against and the figure a payroll system quotes. Typed
  either way round.
- **Equity that vested, and what your employer put in.** Both optional. For
  anyone paid partly in shares, salary and bonus are most of a package rather
  than all of it — and this figure is not decoration: it is the denominator the
  [Giving](#giving) tab measures every percentage against, so a third of your
  income missing meant a giving share that read a third too generous. A column
  appears only once there is something to put in it, and a plan that has never
  tracked either is unchanged to the cent.
- **A total-comp line above the salary line**, once either is recorded. It is
  what a raise on the salary alone can hide going the other way.

---

## Getting Around

### The Header

| Button | What it does |
| --- | --- |
| **⌕ Find** (⌘K / Ctrl+K) | One search box over all of it |
| **↩ Undo** (⌘Z / Ctrl+Z) | Walk back through this sitting's changes |
| **⚙ Preferences** | Settings that apply across the whole app |
| **⇩ Back Up** | Export, restore, or start again |
| **↗ Share** | Create a read-only link |
| **☁️ Sign In to Sync** | Optional Google sign-in |

Each button wears a glyph in front of its word. They are plain text
characters rather than an icon font or emoji, so nothing extra is fetched for
a header that paints before anything else runs, and each takes the theme's own
text colour — no meaning ever rides on hue alone. A screen reader is told to
skip them; the word beside each one is the whole label.

### Find

Two characters minimum, and it searches everything: every year's rows and
notes (split-part notes and balance notes included), donations, trips and
their line items, goals, people, property, and holdings by ticker.

A budget hit opens straight into its cell's editor; everything else lands you
on the right tab. **Enter opens the first result** — the same as clicking it
(added 2026-09-04; until then Enter did nothing, and you had to reach for the
mouse). **The keyboard lands somewhere you can see**: after a result, if the
focus would otherwise have fallen to nowhere — the way it does after a ⌘K
pressed from the middle of nothing — it goes to the tab you landed on, so the
next Tab press carries on from there; a budget hit's editor keeps its own
focus, and a Find button you clicked gets it back as before. The same rule in
every app in the family (Flow Metrics set it on 2026-09-04). When results are
capped it says how many more there were rather than trimming silently.

### Undo

Every change banks the state it replaced, up to twenty deep, and ⌘Z / Ctrl+Z
(or the ↩ Undo button, which appears once there is something to undo) walks
straight back through them, one honest step at a time.

- **The ring lives in memory for this sitting only** — a reload starts fresh.
- **It clears when another device's changes arrive**, since undoing past
  somebody else's work would overwrite it — and stays clear until you change
  something (until 2026-09-01 the first tab click after a sync offered an undo
  of nothing).
- **There is no redo, on purpose**: linear and predictable beats a two-state
  seesaw.
- **Because there is no redo, the button asks before it acts.** It sits among
  the other header buttons and a mis-click would cost you an edit you'd have
  to retype. ⌘Z / Ctrl+Z goes straight back without asking — a modifier chord
  isn't pressed by accident, and it's the way to walk back several steps at a
  time.

### The Years Strip

The years run across the top, the way the sheet tabs did in Numbers — newest
first, with the one you're reading drawn as a filled pill.

Click a year to open it, or **step one year at a press with the ‹ › arrows** at
the strip's right end — the month strip's arrows, in this lens since September
2026, where they used to scroll the rail sideways and hide themselves whenever
every year already fitted. They follow the strip rather than the calendar: the
chip to the left is the year *after* the one you're reading, because the years
run newest first, so ‹ moves one to the left and › one to the right, and each
one greys out at its end rather than wrapping round. The strip still drags and
swipes sideways. From the keyboard, one Tab lands on the strip and the left and
right arrow keys walk along it (Home for the newest year, End for the oldest).

The tabs above the strip, and the strip itself, can be **pinned** to the top of
the page: press the pin at the right-hand end of the tab row and both stay put
while a long grid scrolls under them, the way the header already does. Press it
again to let them go. The setting belongs to the device you set it on — a
desk monitor has room to spend on chrome and a phone does not — so it is never
synced, never in a backup and never carried in a share link. It is in
[Preferences](#preferences) too, for anyone who would rather find it in words.

On a phone the pin holds the **tab row only**. Three bands of chrome is most of
a small screen, so the year strip is let go there and only the tabs stay — the
one that buys you changing tab without scrolling back to the top. The tabs
themselves sit in one row that scrolls sideways there, rather than wrapping to
four; a tab reached from the keyboard shows its focus ring whole, on every
side (fixed 2026-09-04 — the scrolling row used to slice the ring off along
the top and at both ends).

A year kept as a yearly summary is set in italics, one built before it has
started is underlined with dots, **this year carries an underscore** wherever it
has got to in the strip, and hovering any of them says which in words. A **This
Year** button appears at the right-hand end once you have wandered off it — the
Month lens's button, on the same terms — and takes you back in one click, from
however far down the strip you have read.

The same strip carries the Budget's **Year / Month** switch at its left end, and
in the Month lens the years are replaced by the plan's months — the arrows step
from one to the next in both lenses now, and the current month is
marked with an underscore wherever it has got to. Both lenses put their way back
to now in the same place, and neither shows it when you are already there. On a phone the switch and the
arrows take the line above and the strip gets the full width underneath.
See [Year or Month](#year-or-month).

### Where a Press Leaves the Page

**Changing what you're looking at starts at the top; changing which period
you're looking at holds still.** Press a tab and the view you open begins at the
top of its page, rather than at whatever offset the last one had you scrolled
to — before September 2026 it kept that offset, so where you landed on Goals
depended on how far down the Budget you had been, and changed again with the pin
on. Pressing the tab you're already on does nothing, so it never throws the page
about. A [Find](#find) result that only changes the view lands the same way.

(Until September 2026 the page did move, and not because the app asked it to:
with the strip pinned, every redraw of the Month page slid the reader about 15px
further down — the browser's own *scroll anchoring* banking the momentary height
of a page being rebuilt under a sticky bar. Six presses of ‹ left you 90px from
where you started. The app now turns that adjustment off and keeps your place
itself.)

The **year rail, the month rail and the Year / Month switch are the exception,
on purpose**: press 2025, then 2024, then Mar 26 and the page stays exactly
where it is, because that is a comparison — you are reading the same rows while
the figures change under them. (A year kept as a yearly summary is a single
short card, so there is simply less page to hold; that is the window, not the
app moving you.) Every other control that changes what a view is showing rather
than which view you are on — the **This Year** button, the ‹ › arrows, the
switches inside a card — holds the page in the same way.

A Find result that **opens a record** holds too: the editor is over the cell you
searched for, and moving the page would leave you at the top of a long grid the
moment you closed it.

### Arranging Things

- **The tabs are yours to arrange** — drag one anywhere along the bar, with a
  mouse or a finger, or hold Alt and use the arrow keys. The order is saved
  and follows you to your other devices.
- **Budget rows drag into place** — grab a row's name and move it up or down
  within its own section. The order follows into the years you've built ahead,
  so two grids stay readable side by side. (Sorting alphabetically turns
  dragging off, since that order isn't yours to arrange; the ↑↓ buttons in a
  row's editor still work everywhere.) The account rows drag too, in their own
  block — and since accounts are one list rather than one per year, that order
  holds across every year of the plan.
- **Every box folds up.** Click any card's heading — the shaded strip across
  the top of it — and the card collapses to that strip, so a tab can be
  trimmed down to the parts you actually read. What you fold is remembered
  across refreshes and, if you're signed in, follows you to your other
  devices. A box you fold in one year stays folded in the next, and anything
  new is open until you say otherwise. (The welcome card is the one exception:
  hiding the page that explains what the app is would be a poor greeting.)
- **Zoom** — scale the whole app from the header in quarter steps, or type an
  exact percentage in Preferences (50–200%). It belongs to the device you set
  it on: never synced, never in a backup, so a laptop and a desk monitor can
  each have the size that suits them.
- **Chart text is the page's own text.** Axis labels, legends and the hover
  panel are set in the app's typeface at the same small size as the chrome
  around them, instead of the chart library's built-in Helvetica at a fixed
  12px — so a browser set to larger default text gets larger chart text with
  everything else, and the page zoom scales it like any other line on the page.
- **A chart's hover panel wears the theme.** Hovering names what is under the pointer — on a line chart, anywhere in the month or year, because a 3px point is a target nobody should have to hit. The panel takes the theme's own card shade, text and border rather than the chart library's built-in black box, so it belongs to the page on Light and Sepia as much as on Midnight.
- **Any chart fills the window.** Every card that draws one carries a ⤢ button
  at the far right of its heading strip; press it and that chart alone fills
  the screen under the header. **The header stays where it is and stays
  usable** — change the zoom or the theme and the chart redraws in front of
  you, still full screen. Escape, the same button (now an arrows-in icon), or
  a click on the margin round the card brings it back down, and the page is
  where you left it — unless you stepped to another chart up there, in which
  case the page lands on **that** chart, its top just under the header (and
  under the tab row, if you have pinned it), with its ⤢ ready for the keyboard.
  That was decided on 2026-09-04: until then the page went back to where you
  left and was then dragged to wherever the new chart's button happened to be,
  a landing that was right by accident and put the chart nowhere in particular.
  A card with a table under its chart shows the chart: the
  table is one press of Escape away, and letting forty rows of spending squash
  the bars into a strip would answer the opposite question. On a phone the
  card's opening paragraph steps aside too, for the same reason.
- **Step between the charts without coming back down.** Beside the ⤢ are a
  **‹** and a **›** that walk the other charts on the tab you came from —
  Progress has six of them — wrapping round at both ends. The **left and right
  arrow keys** do the same, unless the caret is in a control, where an arrow
  belongs to that control. A folded card is not on the walk, and a tab with one
  chart shows no arrows at all. A step never drops the keyboard: the focus lands
  on the arrow you pressed, or — after an arrow *key* — on the new chart's ⤢,
  so the next Tab carries on inside the window rather than starting from the
  top of the page hidden underneath (fixed 2026-09-04; it used to fall to the
  page).

### Editing, Everywhere

Click any row — budget categories, accounts, goals, holdings, retirement
accounts, trips and their line items, PTO entries, donations, the old yearly
summaries — to change, annotate or delete it. Every table has a ＋ Add button,
rows reorder with ↑↓, and each editor shows only the settings the current
choice actually uses.

- **The two long windows come in sections.** A budget row and an account settle
  more than a dozen questions between them, and with a sweep rule and a due date
  showing, the budget row ran to nearly three screens of one undifferentiated
  list. Both now open at the full window width, three settings across, cut into
  labelled blocks with a line between them — *What It Is · Future Months · How
  The Money Moves · When It's Due* for a row, and *What It Is · Interest ·
  Dividends* for an account. **A block with nothing left to ask disappears**: set
  a row to sweep an account's overflow and the rule decides what the money does,
  so the block that asks goes rather than standing empty.
- **A box shows you what it kept.** Money boxes have always tidied themselves up
  when you leave them; rate boxes do now too, so a rate typed to more decimal
  places than the app stores shows you the figure it settled on rather than
  leaving you to find out next time you open the row. **And the figure it kept
  is the one you typed**: 4.57% is stored as exactly 0.0457 (fixed 2026-09-04 —
  it used to land as 0.045700000000000005, a computer's rounding slip that the
  box hid by rounding on the way back but that a backup file carried in full;
  a pasted tax schedule's rates and a raise worked out from a new salary had the
  same slip and the same fix). **A figure in brackets is
  a negative one** — paste `(500)` off a statement and the box reads
  −$500.00, the way every ledger means it, and so does `$ (1,234.56)`, the way
  Excel's Accounting format and most statement exports write it, with the
  currency symbol outside the brackets (fixed 2026-09-04: that form used to
  arrive positive, in a typed box and in an imported CSV alike). **And a minus sign is a minus sign
  whichever one it is**: a figure copied out of a statement PDF or a typeset
  table carries a real MINUS SIGN rather than the hyphen on your keyboard, and
  that used to be stripped out with the currency symbol — so −200 in a transfer
  row arrived as +200 and the money moved the other way. Both spellings read the
  same now, in a typed box and in an imported CSV alike. (A dash used as
  punctuation — "Rent — $500" — is still just punctuation; only the characters
  that really are hyphens and minus signs count.)
- **Landing on a box selects what's in it**, so typing replaces the figure
  instead of running on to the end of it. Click a second time to place the
  cursor and edit normally. The up/down arrows a browser draws on a number box
  are left alone by this — a press there steps the figure once and stops.
  (A note is the exception: those are written over several lines and added to,
  so they're left as they are.)
- **Clicking outside any dialog closes it** without saving.
- **A small ⓘ beside a figure explains the arithmetic** behind it — including
  on a chart that is filling the window: the explanation opens on top, Escape
  closes it first, and the chart is still there behind it. (Fixed 2026-09-04;
  the dots on a full-screen card used to do nothing at all.)
- **The budget grid is keyboard-operable**: Tab into it, move between cells
  with the arrow keys, and press Enter to edit the one you're on. Every
  clickable row on the other tabs — a donation, a trip line, a comp year, a
  goal card, a gathered note — takes a tab stop of its own, so Enter or Space
  opens it without a mouse.

### CSV, Out and Back

The way to a spreadsheet, and the way home again.

- **⇩ CSV on any budget year** downloads that year's grid — sections, months,
  year totals, account balances, raw numbers, ready for Excel or an
  accountant.
- **The Giving tab** exports every year's donations as the tax-season table.
  Its Deductible column is the tick you put on the row, the same field the
  table on screen reads and the year's deductible total adds up — the file and
  the screen cannot say different things about one gift.
- **⬆ Import a year's CSV**, in the Back Up dialog, reads that same file back.
  Work a year over in a spreadsheet and bring it home instead of retyping it a
  cell at a time.

What the import reads, and what it deliberately doesn't:

- **Income, Expenses and Transfers rows only.** The account balances and the
  Interest & Dividends line are the app's own answers, so writing them back
  would type over a computation with itself and silently pin anything that
  disagreed. They are counted as skipped rather than dropped in silence.
- **A figure lands exactly as a typed one would** — a fact in a month already
  entered, your own estimate beyond it. It is typing, done faster.
- **An empty column empties that month**, which is what a round trip means, and
  only for the months the file has columns for. A month the file says nothing
  about is left alone.
- **A line of words is skipped, not added.** A heading repeated halfway down a
  file, or a column of notes you added while working, is counted among the
  skipped rows rather than becoming a budget row of its own. A row whose columns
  are simply EMPTY is a different thing and still read — that is a round trip
  clearing the months it names.
- **A row the plan doesn't have is added**, since a row that appeared in the
  spreadsheet is usually one you meant to add. Rows are matched by name within
  their own section, however they are cased.
- **A file that isn't an exported year is refused whole**, naming what is wrong
  with it, and the confirmation quotes the real figures — how many cells will
  be written, emptied, added — before anything moves.

Text fields are defused against spreadsheet formula injection, and a BOM keeps
Excel honest about UTF-8.

### Printing

⌘P prints the page properly. The furniture goes — the header controls, the tab
bar, every ＋ Add and ✎ Edit — every horizontal scroller opens out so a budget
year prints all twelve months, cards try not to be torn across a page break,
and a long table repeats its headings. What you folded away stays folded: a
fold is a decision about what you want to read, and printing is not the moment
to overrule it.

Printing borrows the **Light** theme and gives it back afterwards, so a dark
theme doesn't arrive on paper. Nothing is saved, and the theme you were looking
at is the one you are still looking at.

If a chart is filling the window when you print, it comes down first and prints
in its own place on the page, with everything else. (Until 2026-09-04 it did the
opposite: the full-screen window is hidden on paper, and the card was hidden
inside it, so the one chart you were looking at was the one missing from the
print.) The window stays down afterwards.

---

## Preferences

The header's **⚙ Preferences** button opens one editor holding the settings
that apply across the whole app rather than to a row. It is laid out in five
ruled blocks — the same rule and small heading the Budget Row and Account
windows use — and the last of them is the one worth reading twice: everything
above it travels with the plan, and nothing in it does.

**Your Plan**

| Setting | What it changes |
| --- | --- |
| **Subtitle** | Your own words beside "Financial Plan" in the header and the browser tab |
| **You file taxes as** | Which bracket table the Tax tab reads and which Roth (MAGI) threshold it checks against — always asked, since the Tax tab needs no household. Filing jointly also counts both incomes once there are two of you |
| **Compensation tab follows** | Which person that tab's salary history is about, once there are two of you |

**How Figures Read** — neither changes a number:

| Setting | What it changes |
| --- | --- |
| **Currency** | A three-letter code (USD, EUR, GBP, CAD) — the currency the plan itself is in. It changes how figures read, not what they are. Something held in *another* currency is a rate you state on the [Household](#other-currencies) tab |
| **Budget row order** | Your own arrangement, or alphabetical within a section (which turns dragging off and leaves your order stored underneath) |

**What Each Tab Offers**

| Setting | What it changes |
| --- | --- |
| **Paychecks vary by month** | Three some months, two in others — this is what lets a row be an amount per check |
| **Donor-advised fund** | Whether the Giving tab shows a fund's holdings. Donations are tracked either way |
| **PTO days a year** | What each new holiday-planner year starts with |
| **Warn about a due bill this many days ahead** | How early a hand-paid bill with a [due date](#due-dates) starts saying so on the Month page. 0 warns on the day itself |

**Rates The Plan Assumes** — four figures with no source but you:

| Setting | What it changes |
| --- | --- |
| **Dividend row interest %/yr** | The rate a dividend row uses when it has none of its own |
| **Retirement real return %/yr** | The growth rate the [Retirement](#retirement) tab assumes, after inflation. An account can state its own and follow this only when it doesn't |
| **If it goes worse / better %/yr** | The two rates around it that draw the cautious and optimistic lines on the same chart |

**This Device Only** — three settings that live in this browser and nowhere
else: never synced, never in a backup, never in a share link.

| Setting | What it changes |
| --- | --- |
| **Keep the tabs on screen while scrolling** | Pins the view tabs — and the Budget's year or month strip — to the top of the page. The pin button at the right-hand end of the tab row is the same switch |
| **Zoom** | The exact percentage (50–200%), the quarter steps in the header being the everyday version |
| **Twelve Data key** | The [price-lookup](#investments) key — typed here, handed to your password manager, and out of backups, share links and sync |

---

## Themes

Four themes, shared with every other app in this family and listed
alphabetically in the header dropdown below **Auto**: **Dark**, **Light**,
**Midnight** (deep indigo/navy — the base palette, and what Auto shows on a
dark system) and **Sepia**.

The palettes come from `theme.css`, a byte-copy of the generated file in the
private `claude-theme-pack` repo, which is the source of truth for every app
here — a colour is changed in the pack's `tokens.json` and rebuilt, never
retuned in this file. The pack's own gate checks every token for WCAG AA
contrast on each surface it can sit on, which is what lets the grid lean on
colour at all.

**Your theme belongs to the device**, like the zoom: it lives under its own
localStorage key rather than with the plan, so it is never synced, never in a
backup, and a share link never carries the sender's theme. Anything
unrecognised falls back to **Auto** — the default since 2026-08-22, which follows
your own system rather than opening dark on a machine set to light — and the
picker's own options are the only list of themes the app has.

**Colour is never the only thing saying what a figure is.** A projection is
*italic*, a total spanning actual and projected months is dashed, a snapshot's
estimate carries a dashed rail — the same conventions read the same way in all
four palettes.

---

## Backups and Starting Over

**⇩ Back Up** in the header opens one dialog for everything to do with the
file on disk.

- **Export** writes `financial-plan-YYYY-MM-DD.json`.
- **Restore JSON…** reads one back. It's the same path Charlie's one-time
  spreadsheet import uses.
- **Import a year's CSV…** brings one budget year back from a spreadsheet —
  see [CSV, Out and Back](#csv-out-and-back).
- **Compare with a backup…** opens a saved plan beside the live one.

### Comparing Two Plans

"What if we bought the house" means changing a dozen figures across five tabs,
and there was no way to see the before and the after together — two browser
windows and a good memory.

Compare with a backup puts the headline figures side by side: net worth, liquid
savings, what you owe, this year's income and spending, the savings rate, the
runway, the pot at retirement and the year the money runs out. **It reads the
file and writes nothing** — there is deliberately no "use this one instead",
because that is what Restore is and putting it here would turn a comparison
into a way to lose your plan by mis-clicking.

A scenario in this app is what it already was: **a plan you exported and then
changed**. A second plan living inside the first was the obvious design and is
the wrong one — it doubles what syncs, doubles what a backup carries, and gives
the app two answers to "what am I worth" when the whole thing is built on there
being one.

Every figure is read from the same function the tab that owns it draws, so a
comparison can never quote a number the app itself doesn't show. A difference
is worked out only where both plans have an answer; a row only one of them can
answer is kept and dashed, because that is itself the finding. More spending
and more owed read as worse, not better, and a gap between two percentages is
stated in points.

Folded away at the foot of that dialog, under **Start again**, is **Delete all
data**. It's behind a fold on purpose: the one irreversible action in the app
shouldn't sit a mis-click away from Export.

Pressing it opens a confirmation of its own that:

- says exactly how much is going ("This deletes 8 years of budgets, 3
  goals…");
- says out loud, when you're signed in, that the copy in your Google account
  goes too;
- offers the same JSON export as a last chance to keep any of it.

It clears the price-lookup key and the cached ticker prices along with the
plan — "everything" includes the credential.

**You stay signed in, and the deletion reaches your other devices.** The
emptied plan goes out through the normal save path, so the phone sees it land
and asks *"another device has cleared its data — clear this one too?"*;
cancelling keeps the phone's copy and restores it everywhere. The surviving
document holds `{ json: "<blank plan>", updatedAt }` — no name, no month and
no figure in it.

*(Until 2026-08-14 this button deleted the Firestore document and signed you
out instead, which looked tidier and was worse: your other devices were never
told, so the next edit on the phone re-created the document and signing back
in poured the whole plan back.)*

---

## Share a Read-Only Link

Show someone part of the plan without giving them an account, a file or edit
rights.

You pick which tabs go in and how many years go with them. **The whole payload
rides in the link's `#fragment`**, so nothing is uploaded, nothing is stored on
the reader's device, and whatever they already had saved in their own browser
is untouched.

**The most personal things stay behind by default:**

- People's names are replaced with "Adult 1" and "Child 1" unless you tick the
  box.
- Your written notes stay out unless you ask for them.
- So do the years you've built ahead — a projection is a guess about money you
  don't have yet, and handing someone one is a different claim from showing
  them what happened. (A year stops counting as a projection the moment it
  takes over as the real one, so that box has nothing to hold back once it
  has.)

**The dialog tells you what you're sending**: what the link costs in
characters, any tab the year window left empty, and when a tab drags another
tab's data along with it (Giving measures donations against the salary
history, so a Giving link carries it).

Trimming the years shortens the **link**, never the figures: the oldest year
kept is re-seeded with the balances it opened on, so the recipient sees the
same numbers you do.

It's a snapshot — later edits don't appear, and **a link can't be withdrawn
once sent**, so treat one like emailing a spreadsheet.

A link made by a **newer version** of the app than the copy you're running is
refused with an explanation rather than opened with pieces silently missing —
reloading the page picks up the current version, and the link then opens.

---

## Cross-Device Sync

*Firebase, free tier — entirely optional.*

Signing in with Google does one thing: puts the same plan on your other
devices. Without it the app is fully usable and fully local.

Sync is **enabled** in this deployment, backed by the `financialplan-60c6e`
Firebase project. `FIREBASE_CONFIG` in the sync module at the bottom of
`index.html` points at it, and setting that constant back to `null` returns
the app to local-only mode and hides all sync UI.

The whole state travels as **one JSON string** in a `financialplan/{uid}`
document, because Firestore refuses arrays nested inside arrays and this
plan's tables are exactly that. [`firestore.rules`](firestore.rules) is the
checked-in copy of what the console enforces, confining every account to its
own document.

### Why the Sign-In Looks Unusual

Sign-in goes through **Google Identity Services** — a popup straight to
`accounts.google.com`, exchanged for a Firebase session — rather than
`signInWithPopup`, which opens at `<project>.firebaseapp.com` and dies on the
corporate networks that block those hostnames one at a time.

Same account, same data, same rules; only the doorway differs. This is why
`GOOGLE_CLIENT_ID` is a separate constant: it is not part of `firebaseConfig`
and can't be derived from it.

### Which Copy Wins

**`localStorage` stays in charge and the cloud only mirrors it.**

The first time a given Google account signs in on a browser, if both sides
already hold something, a dialog asks **which copy to keep** and names what is
in each — years, goals, people, trips — rather than guessing by timestamp. It
is the one dialog in the app that a click outside will not close: "which copy
of your data?" has no safe default.

After that, whichever side changed most recently wins, and an update pushed
from another device arrives live.

Underneath that, **an empty copy never beats a copy with data in it**,
whichever looks newer — otherwise signing in on a fresh browser would push its
emptiness, stamped `now`, over the device that actually holds the plan. Naming
your household counts as data, not just budget years. Clearing everything
deliberately still reaches your other devices, but each one asks before it
follows.

### When It Stops Working, It Says So

The button reads **⚠️ Not syncing**, and the note at the foot of the page
gives the cause and the fix. Nothing is lost when it happens — this browser is
still the source of truth.

There is no retry button on purpose: Google retries the transient causes
itself, and the state clears the moment a save gets through. If Google had
also dropped the listener that brings other devices' changes in, it is
re-opened when the next save gets through, and on a timer in the meantime —
until 2026-09-01 the button said *Syncing again* while incoming changes were
quietly lost until a reload.

---

## Installing It as an App

The page can live in the Dock or the Applications folder instead of a tab.
Nothing is downloaded and there is no separate version to keep updated — it is
the same page in a window of its own, so it updates when the site does.

- **Chrome** — ⋮ → Cast, Save and Share → **Install page as app…**
- **Safari** (macOS 14+) — **File → Add to Dock**

**The two are not equivalent, and the difference is your data.** Chrome's
installed app shares storage with the browser, so the plan you already have is
simply there. **A Safari web app gets its own storage container**: it shares no
localStorage with Safari, so it opens EMPTY, and the way to fill it is to sign
in and let sync pull the plan down. Treat the Safari one as another device,
not as a shortcut to the tab you already had.

Installing is a window, not a sandbox — an installed app can reach exactly
what any tab on this origin could already reach, no more and no less. The one
real difference is Safari's, and it runs in the safer direction: its separate
container cannot see the sibling apps' data at all.

`manifest.webmanifest` is what makes the install a real app rather than a bare
shortcut, and two things in it are deliberate. **`scope` is `"./"`** — every
one of these apps is served from one origin, and a scope of `/` would swallow
the sibling apps into this app's window; relative keeps it right on the local
server too, where the app sits at the root rather than under
`/financial-plan/`. And it carries **no `file_handlers`, `protocol_handlers`
or `share_target`**: those hand outside data to a page on a shared origin, and
nothing here needs them. The CSP gained exactly one directive for all this,
`manifest-src 'self'`.

---

## Working Offline

The app opens and works with no connection — on a plane, on the Tube, on hotel
wifi that has stopped answering. Your plan was always stored in the browser
rather than fetched from anywhere, so once the app itself loads, everything
except the online-only extras behaves normally: every tab, every projection,
every edit, saved as usual.

What needs the network still needs it — signing in to sync and holding price
lookups — and each says so rather than failing quietly.

This is `sw.js`, a small service worker, and it was refused here for a long
time. Two rules make it safe enough to have changed that:

**It only ever caches files that are already public in this repo** — the page
itself, the vendored chart library, the stylesheet, the icons. Never your
plan, never a sync reply, never a price quote. That matters because these apps
share one browser origin, and a cache is shared across the whole origin rather
than belonging to one app: keeping it to public files means there is nothing
in there that could not be read straight off GitHub anyway.

**It always tries the network first.** The cache is a fallback for a
connection that actually failed, never a shortcut taken while you are online.
So you can never be quietly running yesterday's version — if the network
answers, you get the current app, every time. Offline costs you a few seconds'
wait before it gives up and uses the saved copy.

Belt and braces on the one risk that remains: if this device is running an
older version from its cache and finds a plan saved by a newer one — another
device updated first, then synced — it stops and says so rather than reading
your figures with code that predates them. Nothing is changed or deleted;
connect and reload and it picks up the current version.

If the worker ever misbehaves, `sw-kill.js` is the switch that removes it:
copy it over `sw.js` and push, and every installed copy uninstalls itself and
goes back to being an ordinary online-only page.

---

## Architecture

**One file — `index.html`** — no build step, alongside `theme.css` (byte-copy
from the private claude-theme-pack, the palette source of truth for all apps),
a vendored `chart.min.js`, and `sw.js` with its `sw-kill.js` escape hatch.
Served by GitHub Pages from `main`.

**There is a sample plan.** The welcome screen offers **Load Sample Data** beside Start Fresh:
an invented household of three — two earners, a child, five accounts, this year's budget with two
years of real history behind it — which fills every one of the nine tabs. It carries one of every
shape each feature reads differently: a secured mortgage and an unsecured student loan and a card
with no payment said; a flat and its mortgage in another currency; equity and an employer
contribution on the comp years; and a spending row that existed last year and does not now. It exists because this is the
most complex app of the family and an empty grid shows none of what it does. It goes in through
the same door a backup does, which is worth saying because `coerceShape` is built to carry an odd
shape rather than throw: a key in the wrong place there does not fail, it settles to a default and
the feature it was meant to show draws $0.00 or nothing at all. Its tests therefore read the
values the way their readers do rather than only counting entries. **The figures are
invented**, the app says so in its own header while the sample is loaded, and the tax bands are
round numbers labelled *"not real tax brackets"* in the field the reader is shown — the app's
promise that it ships no tax figure of its own is kept by making the demo's obviously fake. It
saves like any other plan and is removed with Back Up → Start Again.

**State is versioned.** The schema is `7` today, as the `SCHEMA` constant.
Schema 7 moved what was owed off the property rows and into debts of their own,
once — a pure re-filing that leaves the net worth identical to the cent, since
a debt secured on a property reduces that property's equity exactly as the old
number did.
Every entry point runs the payload through `coerceShape()`, whose upgrades are
presence-based and safe to run twice. Its first act is to pin every id — people,
accounts, goals, budget rows, portfolios, trips, and every field pointing at one — to
`[A-Za-z0-9_-]`, at most 64 characters. That is the rule the sibling apps already
keep, and here it guards something specific: cells, overrides and balance
adjustments are stored under `<id>|<month>` keys, so an id containing a `|` from
a hand-edited backup or a crafted share link would be read back with the split in
the wrong place. Ids are re-slugged rather than replaced, so the references and
the stored figures follow their row instead of being orphaned, and a plan whose
ids are already well-formed is left exactly as it was. `migrate()` walks an older plan up to
the current schema — and because all of its gates are `<`, a plan from a
*newer* build would sail through untouched, so `load()` checks for that case
first and halts instead.

It also holds every free scalar in `settings` to a type — the PTO allowance, the
subtitle, the currency code and the two assumed rates. Those look like the least
important fields in the file and are in fact the most exposed ones: a read-only
share link carries the whole of `settings` on purpose, so that a recipient reads
the sender's figures under the sender's own assumptions. Until this landed a
crafted link could put markup where the PTO card prints its allowance without
escaping, or a number where the page expects the subtitle to be text — the first
running script on an origin shared with every other app in the account, the
second bringing the page up blank. A value that cannot be read is *removed*
rather than blanked, so the app's own default still wins the merge.

**`computeAll()` is the only place numbers are calculated.** Every cell,
balance and goal figure derives from stored inputs at render time; nothing
computed is ever persisted.

**The icon** is drawn by `make_favicon.py` (Pillow). The inline SVG in the
page is what browsers use, `favicon.ico` is the fallback a browser fetches on
its own, and the install icons (`icon-192`, `icon-512`, `icon-512-maskable`,
`apple-touch-icon`) are files because a manifest icon cannot be a data URI.
One script draws all of them from one set of coordinates rather than leaving
binaries nobody can review in a diff. The three shapes differ on purpose:
rounded where nothing will mask them, full-bleed with the mark inset where the
platform crops to a circle, and square for Apple, which applies its own
corners. Re-running it means bumping the `?v=` on every `favicon.ico`
reference — two in `index.html`, one in `privacy.html` — or the old icon stays
cached for months.

## Tests

Open `tests.html` on a local server — it runs the pure functions in the real
`index.html` inside a hidden iframe:

```bash
python3 -m http.server 8016
```

All fixtures are synthetic. On this Mac only, if the import files are present,
it additionally diffs the JS engine against the spreadsheet's own cached
values for the live year's own months. (Months beyond that are now a
projection the app works out from the rules, where the spreadsheet had them
typed in, so the two are not meant to agree.)

**And a smoke walk, because everything else is a pure function.** Pinning the engine and the
tax tables leaves the largest part of the file — the render layer — never executed at all, so
a throw inside a tab would ship green. A coverage run on 2026-08-27 measured exactly that:
`renderMonthView` (35KB), `gridCard` (27KB), `openCellEditor` (16KB) and 208 others sat at
zero, and none of the nine tabs had ever been drawn by anything. The walk loads the sample
plan in a second, full-size frame, visits every tab, reads the Budget through **both lenses**
— the year grid and the month page are two different renderers over one tab — opens a grid
cell's editor, presses every button that isn't destructive, and fails if the frame throws or
a view comes back empty. Verified by breaking `renderMonthView` on purpose. Nothing it does
can write: `save()` and `confirm()` are replaced in that frame before anything is pressed,
and the saved plan is read back at the end and compared.

CI (`.github/workflows/tests.yml`) runs the same page headless on every push.

**The page only runs on localhost, and enforces that itself.** GitHub Pages
publishes `tests.html` next to the app, and on that origin the hidden frame
would be a live session — a signed-in browser would start real cloud sync
inside a frame nobody can see. Anywhere but localhost it refuses, explains
itself, and changes nothing. The frame is also marked `data-fin-tests`, which
the app's sync module checks so it never initialises inside the harness — the
same guard as the sibling apps.

## The Migration Scripts

Charlie's own one-time migration from the Numbers spreadsheet:

```bash
python3 import_xlsx.py "~/Downloads/Financial Plan.xlsx"
```

Then open the app → **⇩ Back Up** → **Restore JSON…** → pick
`financial-plan-data.json`.

`migrate_local_data.py` does the one thing the app deliberately won't do to
your data by itself: it takes the next year back out of the live grid.

```bash
python3 migrate_local_data.py financial-plan-data.json
```

The spreadsheet ran 24 months so it could see a year ahead; the app ends a
year at December and starts the next with "Build ⟨year⟩". So the hand-typed
next-year months go and the grid comes back to twelve — while next year's
paycheck counts are kept, because the rollover carries them into the new year.
It writes a new file beside the input and never modifies the original.

(Folding a year into a summary is a per-year decision with a button on the
year itself — the script never does it for you.)

`merge_debit_card.py` is the other one-off: it makes the **ATM** row and the
**Debit Card** row into one row, in every year.

```bash
python3 merge_debit_card.py financial-plan-data.json
```

The same spending had been recorded under four ids since 2013 — `atm`,
`debit-card`, `atm-debit` and 2020's `cash` — and two of them were both wearing
the name "ATM". Nothing paired them, because *Where the Money Goes* matches this year's
rows against last year's by category **id**: the live year's row read "new this
year" while the previous year's read "down 100%", two lines apart in the same
table. All four become `debit-card`, named **Debit Card**, which is what the
row actually holds — card purchases and cash taken out on the card. `cash` is
also the checking ACCOUNT's id, so it is listed in `ONLY_IN` with the single
year it may move in rather than trusted to a bare id match; only `cells` are
ever rekeyed, which is the rule `normalizeIds` follows in the app.

2019 is the only year that is a real merge: it kept both rows, and four months
have a figure in each. Those become one **split cell**, the app's own way of
saying a month was several payments, so every original amount is still on the
screen and nothing is added up out of sight. The script asserts each year's row
total is unchanged, writes a new file beside the input, and never modifies the
original.

**Why there is a `package.json` in a repo with no build step.** It is not a package and it
installs nothing — it exists so Dependabot has a manifest to scan. Its only entry is the
Chart.js that is *vendored* as `chart.min.js` beside the app, pinned exactly, and CI passes
`--omit=dev` so npm never downloads it. Dependabot cannot re-vendor a file, so a version-bump
PR would otherwise raise the manifest while the app went on serving the old bytes; a test pins
the two to the same version, which makes a manifest-only bump fail and turns the PR into the
right instruction — update the file too, in all four repos that carry it.

## When Google's Code Loads (2026-08-22)

**Not on an ordinary visit any more.** `init()` used to run unconditionally at the foot of the
sync module, so `firebase-app`, `firebase-auth`, `firebase-firestore` and the Google sign-in
client were fetched from `www.gstatic.com` and `accounts.google.com` before anyone had touched
anything — four requests to Google carrying the visitor's IP and user-agent, on a page that
might never sync. That is what made the old privacy wording false; this is the change that
lets the strong sentence be true.

It cannot be made *fully* lazy, and that is the whole difficulty: a returning signed-in reader
has to be recognised **without clicking anything**, and the only thing that knows whether this
browser holds a live Firebase session is Firebase. So the app records the answer itself:

| `fin-sync-live` | meaning | on load |
|---|---|---|
| `'1'` | a session was live at last report | load Firebase now |
| `'0'` | there was none, or they signed out | load nothing |
| absent | never asked, or a browser from before this change | fall back to the legacy `fin-sync-uid` marker |

`onAuthStateChanged` writes `'1'` or `'0'` on **every** auth report, including the null one
that follows signing out — so signing out stops the requests, not just the syncing. The
`absent` case is the migration and costs at most **one** eager load per browser:
`fin-sync-uid` has been written on the first successful sync for an account since long
before this, and is never removed, so its presence means "this browser has signed in at some
point". A browser that has never signed in has neither key and never takes that path.

**The warming is load-bearing, not an optimisation.** `requestAccessToken()` has to be called
from inside the click handler or the browser judges the popup unsolicited and blocks it, and
awaiting a cold SDK import first would spend the gesture. So the load starts on
`pointerenter`, `pointerdown` and `focus` — all of which fire *before* click. `onClick` still
awaits `ensureInit()` as a fallback, for somebody who tabs straight to the button and presses
Enter; if the popup is refused there, the existing `popup_failed_to_open` message says what to
do and the second press always works. `ensureInit()` is idempotent, or a hover and a click
would start two Firebase apps.

The click listener is wired at the **boot branch**, not at the end of `init()` — `init()` may
not have run yet, and the button has to be pressable in order to be what causes it to run.

`tests.html` pins the shape of all of this, and the privacy page's wording with it.

## Firebase Version

All three sync apps are on the **same** Firebase version, moved together, exactly like the
vendored Chart.js: `package.json` pins it for Dependabot and `tests.html` pins the manifest to
the `firebasejs/…` URL in `index.html`, so a manifest-only bump fails. Bumping means changing
the URL and the pin in the same commit, in all three repos, and then proving a real Google
sign-in still works on the live origin.

## The Landmarks (2026-08-21)

`<main>` opens **above** the tab strip, not below it. It used to wrap the tab panel alone,
which had two consequences: the tabs sat in no landmark at all (axe-core's `region` rule),
and — the reason worth acting on — **the skip link jumped past them**, so a keyboard user who
took "Skip to content" had the entire tab row behind them, reachable only by shift-tabbing
back. The tabs and the panel they drive are one widget, so the landmark goes round both. The
share bar comes inside with them: it describes what is on screen, so it is content rather
than furniture.

`role="tabpanel"` still goes on the inner div and never on `<main>` — putting a role ON an
element IS its role, so it would silently replace the landmark. That older note stands
unchanged.

Every page in this repo passes axe-core at WCAG 2.1 A and AA, the 2.2 AA additions and its
best-practice rules, in all four themes, with data loaded, on every tab and in every window
(last run 2026-09-05). The things axe cannot see are checked by hand the same day: a Tab
through every view reading the focus ring, every window opened from the keyboard and closed
with Esc, hover colours, a 320px-wide window, widened text spacing and reduced motion.

## What Watches the Firebase SDK (2026-08-21)

The one genuinely third-party thing this app runs is Google's Firebase SDK, and it is loaded
by **URL** from `www.gstatic.com` — so nothing was watching it. Dependabot reads manifests, and
no manifest named it; the clean bill of health it reported covered nothing at all. (There are
no known advisories against the pinned version — the problem was that nobody would have been
told if there were.)

`package.json` is that manifest. It installs nothing — it is `private`, has no `scripts`, and
CI passes `--omit=dev` — and the bytes that run still come from Google's CDN at page load.
That creates the same way of ending up lying that a vendored library has: **Dependabot cannot
rewrite a URL**, so a version-bump PR would raise the manifest while the page went on fetching
the old one. `tests.html` pins the manifest's version to the `firebasejs/…` URL in
`index.html`, which makes a manifest-only bump fail and turns the PR into the right
instruction: *a newer SDK exists, now change the URL too.*

Never let that pin become a `^` or `~` range — a range cannot be checked against a URL.

## The Header Strapline

The header reads **Financial Plan · Charlie's Epic Money Map**, matching the six sibling apps.
It is a **Preference**, not a hardcoded name: change it in Preferences and it changes; clear
it and the app is just "Financial Plan" again, and stays that way. A plan written before
2026-08-22 gains the default once, through the schema-6 migration, and only if its subtitle
was empty — one somebody had typed is never overwritten.

It appears in the browser tab as well as the header, and it travels in a share link along with
everything else in `state.settings`, so a recipient sees the sender's subtitle over the
sender's figures. That is the existing deliberate pairing, and the Preferences hint says so.
