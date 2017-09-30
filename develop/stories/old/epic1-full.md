# Epic 1: Manage a collection of subjects to work on.

### Theme 1.1: Subjects
#### User Story 1.1: Create Subjects
As an user I want to create work subjects so I can divide my work in different subjects.  
Validation:
* Test that an user can create a work subject with a name and optional information.
* Test that two subjects can't have the same name.

#### User Story 1.2: Delete Subjects
As an user I want to be able to delete a work subject so I can delete old subjects that I don't work with anymore.  
Validation:
* User can delete a work subject, which deletes all the information.

#### User Story 1.3: Archive Subjects
As an user I want to archive my work subjects so I can maintain order in my subjects.  
Validation:
* User can archive a work subject, which don't delete the information but hide the subject.
* User can't archive a subject that is already archived.

#### User Story 1.4: Unarchive Subjects
As an user I want to be able to undo the archive operation on a subject (unarchive) so I can reorder my subjects.
Validation:
* User can unarchive an archived work subject, show the subject again.
* User can't unarchive an unarchived work subject.

#### User Story 1.5: Edit Subjects
As an user I want to be able to edit work subjects, their information, name, etc. so I have better management of my subjects.  
Validation:
* User can edit the name, information and any other characteristic of a work subject, without changing any of the other content.
* After editing the name, the user can't access the subject with the old name, only with the new name.


### Theme 2: Categories
#### User Story 2.1: Create Categories
As an user I want to create categories for my work subjects so I have better management of the subjects.  
Validation:
* User can create a subject category, with a name and optional information.
* Names of the categories must be unique (to identify them) and can't be the same that a tag's name.

#### User Story 2.2: Categorize subjects
As an user I want to be able to categorize my work subjects so I have better management of the subjects.  
Validation:
* User can categorize (apply a category to) a subject, only if the subject does not have a category already.

#### User Story 2.3: Uncategorize subjects
As an user I want to be able to remove a subject from a category so I have better management of the subjects.  
Validation:
* User can remove a category (uncategorize) from a subject only if the subject previously had the category.

#### User Story 2.4: Delete Categories
As an user I want to be able to delete a category so I have a complete management of the categories.  
Validation:
* User can delete categories, which doesn't delete the subjects that belong to that category, but remove the category from them.


### Theme 3: Tags
#### User Story 3.1: Create Tags
As an user I want to create tags for my work subjects so I have better management of the subjects.  
Validation:
* User can create a subject tag, with a name and optional information.
* Names of the tags must be unique (to identify them) and can't be the same that a category's name.

#### User Story 3.2: Tag subjects
As an user I want to be able to tag my work subjects so I have better management of the subjects.  
Validation:
* User can tag a subject.
* A subject can be tagged with an arbitrary number of tags (they are not exclusive).

#### User Story 3.3: Untag subjects
As an user I want to be able to remove a tag from a subject so I have better management of the subjects.  
Validation:
* User can remove a tag from a subject, only if the subject previously had the tag.

#### User Story 3.4: Delete Tags
As an user I want to be able to delete a tag so I have a complete management of the tags.  
Validation:
* User can delete tags, which doesn't delete the subjects that have that tag, but remove the tag from them.



### Theme 4: Inner tags
#### User Story 4.1: Create inner-tags
As an user I want to create tags for a specific work subject so I can categorize my work within a subject.  
Validation:
* User can create a tag for a work subject, with a name and optional information.
* Names of the tags must be unique inside the subject they belong to.

#### User Story 4.2: Delete inner-tags
As an user I want to be able to delete tags that belong to a specific subject so I have a better management of the tags of a subject.  
Validation:
* User can delete a tag from a specific work subject.
* Test that removing a tag implies untagging every session that is tagged with it, but the sessions are not deleted.

#### User Story 4.3: Tag sessions with inner-tags
As an user I want to be able to tag my work sessions with a tag for the subject of that session, so I have specific tags for the sessions within a subjects.  
Validation:
* User can tag a session.
* Test that the user can't tag a session with a tag from a different subject that the one from the session.
* Test to tag a session with at least 20 tags (tags are not exclusive).

#### User Story 4.4: Untag sessions
As an user I want to be able to remove a tag from a session so I have better management of the sessions of a subject.  
Validation:
* Test that the user can remove a tag from a session, only if the session previously had the tag.
