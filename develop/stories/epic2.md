# Epic 2: Register sessions of work

## Basic operations
1. Register start of a work session (creation)
  - A work session belongs to a subject XOR a task (can't be both?)
2. Register stop of a work session
  - `--discard` option
  - `--edit-time` option
3. Register a pause of a work session
  - pause and unpause when wanted
  - `--wait` option
  - differentiate in tiny, small, medium, long, super-long pauses (etc)
4. Delete a session


5. Modify amount of time worked in a session (edit timestamp)
  - ask for confirmation, only use for errors
6. Add information to a session
  - At any time, when starting, stopping, when running, when stopped

## Currently running sessions
1. Check the state of the running sessions (must be easy/fast to do)
  - see time running, effective and paused
  - see time since last pause
  - see amount of pauses
  - if not working in anything, see time since last work
2. Limit the amount of running sessions to a maximum of X
3. Visualize on the screen (at all times) the status of the sessions (running, paused, stopped)
