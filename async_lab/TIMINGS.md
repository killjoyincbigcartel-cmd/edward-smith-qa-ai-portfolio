# Synchronous Baseline Timings

| Number of Calls | Total Time |
|---:|---:|
| 1 (eggs) | 2.104 seconds |
| 3 (eggs, milk, rice) | 6.287 seconds |
| 5 (eggs, milk, rice, beans, bread) | 10.461 seconds |

## Why the time increases

The total time increases as more requests are added because each request has to finish before the next one starts. The requests run sequentially, so the waiting time adds up.

## Why the baseline matters

Having baseline timings gives us a starting point before changing how the program executes. We can compare these results with the async version later to see whether it actually reduces the total runtime.
