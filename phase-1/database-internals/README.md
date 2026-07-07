phase-1/
│
├── database-internals/
│   │
│   ├── 01-transaction-lifecycle/
│   ├── 02-acid-properties/
│   ├── 03-concurrent-transactions/
│   ├── 04-lost-update/
│   ├── 05-row-level-locking/
│   ├── 06-mvcc/
│   ├── 07-isolation-levels/
│   ├── 08-deadlocks/
│   ├── 09-atomic-update/
│   ├── 10-high-concurrency-counter/
│   └── README.md
│
└── url-shortener/

Experiment 05 — What happens if you don't call commit()? (ROLLBACK behavior)
Experiment 06 — Explicit BEGIN vs implicit BEGIN
Experiment 07 — Connection pool reuse (prove the same backend PID can be reused)
Experiment 08 — Session lifecycle vs transaction lifecycle vs connection lifecycle


02-concurrency/
│
├── experiments/
│   ├── experiment-01-lost-update.py
│   ├── experiment-02-row-lock.py
│   ├── experiment-03-select-for-update.py
│   ├── experiment-04-deadlock.py
│   ├── experiment-05-mvcc-snapshot.py
│   ├── experiment-06-repeatable-read.py
│   ├── experiment-07-serializable.py
│   └── experiment-08-atomic-update.py
│
├── observations/
│   ├── experiment-01-observation.md
│   ├── experiment-02-observation.md
│   └── ...
│
├── question-answer.md
└── README.md

03-production-patterns/
│
├── 01-high-concurrency-counter/
├── 02-inventory-reservation/
├── 03-money-transfer/
├── 04-job-queue/
├── 05-idempotency/
├── 06-outbox-pattern/
└── README.md


01-high-concurrency-counter/
│
├── 01-naive-counter/
├── 02-atomic-update/
├── 03-thread-test/
├── 04-process-test/
├── 05-load-test/
├── 06-performance-analysis/
├── 07-production-design/
│
├── observations/
├── question-answer.md
└── README.md

03-production-patterns/
└── 01-high-concurrency-counter/
    │
    ├── app/
    │   ├── db.py
    │   ├── repository.py
    │   ├── counter_service.py
    │   └── models.py
    │
    ├── experiments/
    │   ├── experiment-01-naive-counter.py
    │   ├── experiment-02-atomic-counter.py
    │   ├── experiment-03-thread-load.py
    │   ├── experiment-04-process-load.py
    │   └── experiment-05-performance.py
    │
    ├── observations/
    │
    ├── question-answer.md
    │
    └── README.md

02-inventory-reservation/

Experiment 01
Naive Purchase (Overselling)

↓

Experiment 02
SELECT FOR UPDATE

↓

Experiment 03
Concurrent Buyers

↓

Experiment 04
Reservation Timeout

↓

Experiment 05
Production Benchmark