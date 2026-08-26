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
- **Back up before you experiment.** The **⇩ Back up** button writes a JSON
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
- **Sync is optional.** "Sign in to sync" (Google) mirrors your data to a
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
end as easily as within one; a **This Month** button appears once you have
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
  are close or already late, and of any you are still waiting on. It isn't there
  at all in a month with nothing to say.
- **The accounts**, each with what it held at the end of the month, how far that
  moved, and what it earned.
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
- **Interest starts where it grows.** A new account pays its interest into
  itself, which is what an account holding money does; its dividends default to
  the main account instead, since a brokerage usually sweeps those somewhere
  spendable. Both are a dropdown, and either can be pointed anywhere.
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
  never goes missing after a scroll or an edit.
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

### Notes

**Every note you've written anywhere in a year is gathered into a box of its
own under the budget** — cells, split parts, balances and rows — each one
clickable to jump back to what it was about. The box isn't there at all in a
year you haven't annotated. Notes are grouped by month and laid out across the
width of the card, so a year's worth reads at a glance instead of running down
one long strip.

### Entered Months and Finished Years

Mark a month **entered** to freeze its estimates into numbers, like
overtyping formulas in Numbers.

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
this month's liquid total, the Investments tab's holdings, the retirement
accounts, the Household tab's property at your stated values, and everything
you owe. The giving fund is deliberately left out — that money is
already given — and a part with nothing recorded shows no tile rather than a
$0.00.

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

**Record today's figures** turns the strip into history. Each press states the
card's exact figures as a dated snapshot — a deliberate act, like pinning a
balance; the app never records one on its own — and two or more draw the
net-worth-over-time line, with the parts in the hover.

- The table under it lists each snapshot's parts beside its total, in the same
  order as the tiles above; a part a snapshot never stated shows a dash rather
  than a $0.00.
- A second press the same day restates rather than duplicating.
- Old statements can be typed in by hand to backfill the line.
- Every snapshot is clickable to correct or delete.

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

The trips come first — they are what the tab is for and what you edit.

- **Per-trip cost tables**, grouped into one row per year, newest first, and
  reorderable within a year. A new trip starts from the lines most trips need
  — airfare, stay, transport, excursions, food, tips, spa — or from nothing,
  your choice.
- **Each line tracks what's paid, what's credited and what's still due**, with
  a **✓ Paid** button that settles the rest in one click.
- **A holidays & PTO planner**, with from/to dates, under the trips it counts.
- **Trip Spending, Year by Year** — a chart at the foot of the tab, once two
  years have trips. Each bar adds a year's trips up (paid, minus credits, plus
  still due), with the trips themselves broken out in the hover, a dotted
  average across the finished years, and a dashed edge on a year whose figure
  can still grow.

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
  every row or sum to 100%.
- **Asset classes in your own words** ("S&P 500", "Bonds") — the app
  deliberately ships no fund taxonomy, the same principle as the tax tables. A
  **By Class** table folds the rollup into those labels, so three funds
  tracking one index read as the single bet they are; anything unlabelled
  gathers honestly under "Not classed yet".
- **Targets per class** — click a class row. This is usually where a
  rebalancing rule actually lives: "90% US stocks" is one target at the class
  level, where saying it per ticker would measure each fund alone against the
  whole.

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
| **⇩ Back up** | Export, restore, or start again |
| **↗ Share** | Create a read-only link |
| **☁️ Sign in to sync** | Optional Google sign-in |

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
on the right tab. When results are capped it says how many more there were
rather than trimming silently.

### Undo

Every change banks the state it replaced, up to twenty deep, and ⌘Z / Ctrl+Z
(or the ↩ Undo button, which appears once there is something to undo) walks
straight back through them, one honest step at a time.

- **The ring lives in memory for this sitting only** — a reload starts fresh.
- **It clears when another device's changes arrive**, since undoing past
  somebody else's work would overwrite it.
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

Drag or swipe the strip sideways, or use the ‹ › arrows at its right end,
which grey out once you reach an end and vanish altogether when every year
already fits. Click a year to open it; from the keyboard, one Tab lands on the
strip and the left and right arrow keys walk along it (Home for the newest
year, End for the oldest).

A year kept as a yearly summary is set in italics, one built before it has
started is underlined with dots, **this year carries an underscore** wherever it
has got to in the strip, and hovering any of them says which in words. A **This
Year** button appears at the right-hand end once you have wandered off it — the
Month lens's button, on the same terms — and takes you back in one click, from
however far down the strip you have read.

The same strip carries the Budget's **Year / Month** switch at its left end, and
in the Month lens the years are replaced by the plan's months — the arrows there
step from one month to the next rather than scrolling, and the current month is
marked with an underscore wherever it has got to. Both lenses put their way back
to now in the same place, and neither shows it when you are already there. On a phone the switch and the
arrows take the line above and the strip gets the full width underneath.
See [Year or Month](#year-or-month).

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

### Editing, Everywhere

Click any row — budget categories, accounts, goals, holdings, retirement
accounts, trips and their line items, PTO entries, donations, the old yearly
summaries — to change, annotate or delete it. Every table has a ＋ Add button,
rows reorder with ↑↓, and each editor shows only the settings the current
choice actually uses.

- **Landing on a box selects what's in it**, so typing replaces the figure
  instead of running on to the end of it. Click a second time to place the
  cursor and edit normally. The up/down arrows a browser draws on a number box
  are left alone by this — a press there steps the figure once and stops.
  (A note is the exception: those are written over several lines and added to,
  so they're left as they are.)
- **Clicking outside any dialog closes it** without saving.
- **A small ⓘ beside a figure explains the arithmetic** behind it.
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
- **⬆ Import a year's CSV**, in the Back up dialog, reads that same file back.
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

---

## Preferences

The header's **⚙ Preferences** button opens one editor holding the settings
that apply across the whole app rather than to a row:

| Setting | What it changes |
| --- | --- |
| **Subtitle** | Your own words beside "Financial Plan" in the header and the browser tab |
| **You file taxes as** | Which bracket table the Tax tab reads and which Roth (MAGI) threshold it checks against — always asked, since the Tax tab needs no household. Filing jointly also counts both incomes once there are two of you |
| **Compensation tab follows** | Which person that tab's salary history is about, once there are two of you |
| **Currency** | A three-letter code (USD, EUR, GBP, CAD) — the currency the plan itself is in. It changes how figures read, not what they are. Something held in *another* currency is a rate you state on the [Household](#other-currencies) tab |
| **Budget row order** | Your own arrangement, or alphabetical within a section (which turns dragging off and leaves your order stored underneath) |
| **Paychecks vary by month** | Three some months, two in others — this is what lets a row be an amount per check |
| **Donor-advised fund** | Whether the Giving tab shows a fund's holdings. Donations are tracked either way |
| **PTO days a year** | What each new holiday-planner year starts with |
| **Dividend row interest %/yr** | The rate a dividend row uses when it has none of its own |
| **Warn about a due bill this many days ahead** | How early a hand-paid bill with a [due date](#due-dates) starts saying so on the Month page. 0 warns on the day itself |
| **Zoom** | The exact percentage (50–200%), the quarter steps in the header being the everyday version |

---

## Themes

Four themes, shared with every other app in this family and listed
alphabetically in the header dropdown: **Dark**, **Light**, **Midnight** (deep
indigo/navy — the default) and **Sepia**.

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

**⇩ Back up** in the header opens one dialog for everything to do with the
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
itself, and the state clears the moment a save gets through.

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
saves like any other plan and is removed with Back up → Start again.

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

Then open the app → **⇩ Back up** → **Restore JSON…** → pick
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

Every page in this repo passes axe-core at WCAG 2.1 A and AA plus its best-practice rules, in
all four themes, with data loaded and on every tab.

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
