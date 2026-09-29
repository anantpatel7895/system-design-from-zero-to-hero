# Experiment 07 — Event Basics

# Question & Answer

---

## Q1. What is an Event?

An **event** is a record/fact that says:

> Something already happened.

For our reservation system:

```text
ReservationCreated
```

means:

```text
A reservation was successfully created.
```

The event contains information about what happened:

```text
reservation_id
product_id
user_id
quantity
occurred_at
```

### Important

An event represents a **past occurrence**.

```text
Event = "This happened"
```

---

## Q2. What is the difference between an Event and a Command?

### Command

A command asks someone/system to perform an action.

```text
CreateReservation
```

Meaning:

```text
"Please create a reservation."
```

### Event

An event tells other systems that something already happened.

```text
ReservationCreated
```

Meaning:

```text
"The reservation has been created."
```

### Simple way to remember

```text
Command:
"DO THIS"

Event:
"THIS HAPPENED"
```

---

## Q3. Who is the Producer?

The **producer** is the component that creates/publishes the event.

### In our real application

The producer will eventually be:

```text
ReservationService
```

because `ReservationService` performs the reservation operation.

The flow will eventually become:

```text
ReservationService
        |
        | reservation successful
        ▼
ReservationCreated
```

### But what are we doing in Experiment 07?

Experiment 07 is only a **controlled demonstration**.

We manually create the event:

```python
event = create_reservation_created_event(
    reservation_id=101,
    product_id=1,
    user_id=5001,
    quantity=2,
)
```

Therefore:

```text
Experiment 07
    |
    └── Manually creates event
```

Nobody in the actual reservation application is creating the event yet.

This is intentional.

The purpose of Experiment 07 is to understand the basic event concept before connecting it to the real `ReservationService`.

---

## Q4. Who are the Consumers?

A **consumer** is a component that receives an event and reacts to it.

Our demo has two consumers:

```text
ReservationCreated
       |
       ├── Notification Consumer
       |
       └── Analytics Consumer
```

For example:

### Notification Consumer

```text
ReservationCreated
        |
        ▼
Send notification to user
```

### Analytics Consumer

```text
ReservationCreated
        |
        ▼
Record reservation analytics
```

---

## Q5. Why can one Event have multiple Consumers?

Because the same business fact can be useful to different parts of the system.

For example:

```text
                  ReservationCreated
                         |
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
    Notification      Analytics       Audit
```

All three systems are interested in the same fact:

```text
A reservation was created.
```

The producer does not need to know the internal implementation of each consumer.

This creates **loose coupling**.

---

## Q6. What happens if the Analytics Consumer fails?

In our current Experiment 07:

```text
ReservationCreated
       |
       ├── Notification Consumer
       |
       └── Analytics Consumer ❌
```

If the analytics consumer raises an exception, there is currently:

```text
No queue
No retry
No persistence
No dead-letter queue
No independent worker
```

It is simply a Python function call.

Therefore, the application would need explicit exception handling if we wanted the notification consumer to continue operating.

---

# Q7. Are we actually doing Event-Driven Architecture in Experiment 07?

Not yet.

Experiment 07 is primarily a **demonstration of the event concept**.

We are manually creating an event:

```text
                 Demo
                  |
                  ▼
       Manually create event
                  |
                  ▼
        ReservationCreated
             /        \
            ▼          ▼
      Notification   Analytics
```

We have NOT introduced:

```text
Kafka
RabbitMQ
SQS
Event Bus
Outbox
Message Queue
Async Worker
Retry
```

---

# Q8. Who should create the Event in the real system?

In our reservation system, the real producer should eventually be:

```text
ReservationService
```

The flow should become:

```text
Customer
   |
   ▼
ReservationService
   |
   | 1. Begin transaction
   |
   | 2. Lock product
   |
   | 3. Validate stock
   |
   | 4. Decrease stock
   |
   | 5. Create reservation
   |
   | 6. Commit
   |
   ▼
ReservationCreated
```

The event should represent the successful business fact:

```text
ReservationCreated
```

---

# Q9. Why didn't we connect ReservationService immediately?

Because we want to learn this incrementally.

The learning progression is:

```text
Experiment 07
Understand Event
        ↓
Experiment 08
Connect Event to ReservationService
        ↓
Experiment 09
Introduce Event Publishing Failure
        ↓
Experiment 10
Implement Outbox Pattern
```

This allows us to understand **why** the Outbox Pattern is required instead of simply implementing it without understanding the problem.

---

# Q10. What is the important problem we will discover next?

Suppose we connect `ReservationService` to event publishing.

We might have:

```text
ReservationService
       |
       ├── Database COMMIT ✅
       |
       └── Publish Event ❌
```

The database says:

```text
Reservation = CREATED
```

but the event system says:

```text
No event received
```

Now the system is inconsistent.

This is commonly called the **dual-write problem**.

---

# Q11. What is the opposite failure?

The reverse can also happen:

```text
ReservationService
       |
       ├── Publish Event ✅
       |
       └── Database COMMIT ❌
```

Now consumers may believe:

```text
ReservationCreated
```

while the database does not contain the reservation.

Therefore, simply doing:

```text
DB write
+
Event publish
```

is not automatically reliable.

---

# Q12. How will we eventually solve this?

We will introduce the **Outbox Pattern**.

The eventual architecture will be:

```text
                 ReservationService
                         |
                         ▼
                 BEGIN TRANSACTION
                         |
             ┌───────────┴───────────┐
             ▼                       ▼
      Reservation Table        Outbox Table
             |                       |
             |                       |
             └───────────┬───────────┘
                         |
                      COMMIT
                         |
                         ▼
                   Outbox Worker
                         |
                         ▼
                 Event Infrastructure
                         |
                  ┌──────┴──────┐
                  ▼             ▼
             Notification    Analytics
```

The important idea is:

```text
Reservation
+
Event record
```

are stored in the **same database transaction**.

Therefore, we avoid the simple dual-write problem where one succeeds and the other fails.

---

# Key Takeaways

```text
1. Event = something that already happened.

2. Command = request to perform an action.

3. Producer = component that creates/publishes the event.

4. Consumer = component that reacts to the event.

5. One event can have multiple consumers.

6. Experiment 07 is only a controlled demo.

7. We manually create the event in Experiment 07.

8. The real producer will eventually be ReservationService.

9. Experiment 07 has no queue, retry, persistence, or EventBus.

10. Connecting DB writes and event publishing introduces the
    dual-write problem.

11. The Outbox Pattern will be introduced later to solve that problem.
```

---

# Learning Progression

```text
Experiment 07
Event Basics
    │
    ▼
Experiment 08
Real Producer: ReservationService
    │
    ▼
Experiment 09
Dual-Write Failure
    │
    ▼
Experiment 10
Outbox Pattern
    │
    ▼
Experiment 11
Outbox Worker
    │
    ▼
Experiment 12
Multiple Workers + SKIP LOCKED
    │
    ▼
Experiment 13
Distributed Event Processing
    │
    ▼
Message Queue
Kafka / RabbitMQ / SQS
```
