# Design notes for report and diagrams

## Entity relationships
- `employees(employee_id PK, username UNIQUE, password_hash)`
- `movies(movie_id PK, title, genre, release_year, rental_price, producer)`
- `customers(customer_id PK, name, contact)`
- `rentals(rental_id PK, movie_id FK, customer_id FK, rental_date, due_date, return_date, late_fee)`
- Movie 1 — many rentals (historically); Customer 1 — many rentals.
- Functional application components: `App` -> `ManagementPage`; GUI calls `auth`, `movies`, `customers`, `rentals`, `reports`; these call `db`.

## Proposed modules and real contributor log
Record actual GitHub account, PR URL, dates, functionality implemented, testing and code review for each group member. Do not infer contribution from branch name alone.

## Manual tests for screenshots
T01 Incorrect login denied; T02 Correct login accepted; T03 Add movie; T04 Update movie; T05 Search movie; T06 Add/update/search customer; T07 Issue valid movie; T08 Prevent duplicate open rental; T09 Return on time (zero late fee); T10 Return 3 days late (3 * configured daily fee); T11 Delete referenced movie/customer blocked; T12 Export Excel and inspect four sheets; T13 Display genre chart.