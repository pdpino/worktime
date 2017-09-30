# Epic 1: Manage a collection of subjects to work on.

## Theme 1: Work Subjects
Use for a subject you may be working for a long period
#### CRUD
  * Create work subjects
    - name
    - info
  * Delete work subject
  * Edit information or name of a work subject

#### Nesting
  * Nest subjects ???
    - REVIEW: This can be replaced with categories?

#### Archive
  * Archive/Unarchive work subjects
    - don't delete, just hide
    - Can't archive an archived one

## Theme 2: Work Task
Use for a specific task (usually time bounded)

#### CRUD
  * Create tasks
    - name
    - info
  * Delete task
  * Edit information or name of a task

#### Nesting
  * Nest tasks
    - ability to divide in subtasks
    - REVIEW: better yet, divide tasks in steps (that are also tasks)
  * Mark/unmark a task as part of a subject

#### Finish task
  * Finish Task (mark as finished, can't use it anymore)
  * Undo finished action

## Theme 3: Subject Categories
#### CRUD
  * Create categories for subjects
  * Delete categories
  * Edit information or name of a category
  * Categorize/uncategorize subjects


## Theme 4: Tags
#### CRUD
  * Create tags
  * Delete tags
  * Edit information or name of a tag

#### Nesting
  * Nest tags in one another
    - then, tagging something with a child tag automatically tags it with the parent tag

#### Tagging
  * Tag/untag subjects
  * Tag/untag tasks
  * Tag/untag sessions

#### Different behavior for specific created tags
  * Restrict that a tag can or cannot be applied to: subjects, tasks or sessions
  * Restrict that a tag can only be applied to one subject
  * Restrict that a tag can only be applied to one task
